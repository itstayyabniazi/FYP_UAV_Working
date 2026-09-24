"""
ros_io.py

ROS 2 implementation of the `io` interface that vision_landing.VisionLander
expects (see that module's docstring), plus a preflight check. Reuses
ResetManager for everything that talks to landing_controller / PX4, so the
control path is exactly the one Phase 1's takeoff_and_land.py already proved.
"""
import time
from collections import deque

import numpy as np
import rclpy
from rclpy.node import Node

from interfaces.msg import LandingCommand, LandingTarget, UAVState
from px4_msgs.msg import VehicleLocalPosition
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
from std_msgs.msg import Empty

from config.parameters import Parameters
from environment.reset_manager import ResetManager
from mission.target_tracker import PositionHistory

TOUCHDOWN_ALTITUDE = 0.3  # [m] AGL below which the UAV counts as landed


class RosMissionIO:

    def __init__(self, params: Parameters = None, fresh_age=0.5, estimate_window=5):
        rclpy.init()
        self.params = params or Parameters()
        self.node = Node("vision_mission")
        self.reset = ResetManager(self.node, self.params)
        self.fresh_age = fresh_age              # [s] a detection older than this is not "current"
        self.estimate_window = estimate_window  # detections averaged into one estimate

        # (wall time, marker x, marker y, rel_x, rel_y, rel_z); marker x/y are
        # ABSOLUTE PX4-local coordinates: UAV position at receipt + the
        # camera's relative measurement.
        self._detections = deque(maxlen=200)
        # (wall time, detected) for EVERY /landing_target message, so a failed
        # detection can be told apart from a silent aruco node.
        self._messages = deque(maxlen=400)
        self.node.create_subscription(LandingTarget, "/landing_target", self._on_target, 10)
        # Absolute marker samples not yet consumed by a tracker: (capture time, x, y, receipt time).
        self._pending = deque(maxlen=600)
        # Camera -> estimate latency [s]. The camera measurement describes the scene at the moment the image was
        # taken, but it arrives this much later; the marker's world position must be built from where the UAV
        # WAS then. ~0.35 s was inferred from a real Gazebo run; measure yours with
        # `python3 -m mission.measure_camera_latency`.
        self.camera_latency = 0.35
        self._uav_history = PositionHistory()
        self.node.create_subscription(UAVState, "/uav/state", self._on_uav_history, 10)
        # NOT for the staleness watchdog below: px4_bridge's uav_state_node republishes /uav/state on its
        # own 0.05 s TIMER using whatever it last received, with no check that PX4 is still sending
        # anything new -- so /uav/state keeps ticking, unchanged, forever, even after PX4/Gazebo has
        # actually died. A watchdog on THIS topic never fires (confirmed: a real crash during takeoff was
        # only caught by the unrelated 40 s takeoff_timeout, not this). Watch the raw PX4 topic instead,
        # the same one px4_bridge itself subscribes to -- that one genuinely goes silent when PX4 does.
        px4_qos = QoSProfile(reliability=ReliabilityPolicy.BEST_EFFORT, durability=DurabilityPolicy.VOLATILE,
                             history=HistoryPolicy.KEEP_LAST, depth=1)
        self.node.create_subscription(VehicleLocalPosition, "/fmu/out/vehicle_local_position_v1",
                                      self._on_px4_alive, px4_qos)
        self._last_px4_msg_time = None
        # (time, uncompensated est x, y, uav vx, vy) -- only for measure_camera_latency
        self._raw = deque(maxlen=2000)
        self._cmd_pub = self.node.create_publisher(LandingCommand, "/landing_command", 10)
        self._start_pub = self.node.create_publisher(Empty, "/moving_platform/start", 10)

    def log(self, message):
        self.node.get_logger().info(message)

    # -- time -------------------------------------------------

    def now(self):
        return time.time()

    def sleep(self, duration):
        end = time.time() + duration
        while (remaining := end - time.time()) > 0:
            rclpy.spin_once(self.node, timeout_sec=remaining)

    # -- preflight --------------------------------------------

    def preflight(self, require_platform=False) -> bool:
        """Check the pipeline is up before arming anything. Same lesson as
        Phase 1: a duplicate/stale publisher silently corrupts the target, so
        insist on exactly one /landing_target publisher."""
        problems = []
        deadline = time.time() + 10.0
        while self.reset._uav_state is None and time.time() < deadline:
            rclpy.spin_once(self.node, timeout_sec=0.2)
        if self.reset._uav_state is None:
            problems.append("no /uav/state -- is `px4_bridge uav_state_node` running?")
        self.sleep(1.0)  # let DDS discovery settle before counting publishers
        for topic, hint in (
            ("/drone_camera", "the camera bridge (ros_gz_bridge parameter_bridge /drone_camera ...)"),
            ("/drone_camera/camera_info", "the camera bridge (camera_info)"),
        ):
            if self.node.count_publishers(topic) < 1:
                problems.append(f"nothing publishes {topic} -- start {hint}")
        n = self.node.count_publishers("/landing_target")
        if n < 1:
            problems.append("nothing publishes /landing_target -- start `ros2 run vision_node aruco_landing_target_node`")
        elif n > 1:
            problems.append(f"{n} nodes publish /landing_target (expected 1) -- kill the stale one(s)")
        elif not problems:
            # A publisher existing proves nothing (a silent node still has
            # one): require actual traffic. The aruco node reports
            # detected=False for every frame it processes, so ANY message
            # means camera_info (or its fallback), /uav/state and the images
            # are all flowing.
            deadline = time.time() + 6.0
            while not self._messages and time.time() < deadline:
                rclpy.spin_once(self.node, timeout_sec=0.2)
            if not self._messages:
                problems.append(
                    "aruco_landing_target_node is running but published nothing on /landing_target "
                    "in 6 s -- check its terminal (waiting for /uav/state? images not arriving?)")
        if require_platform:
            n = self.node.count_publishers("/platform/state")
            if n < 1:
                problems.append("nothing publishes /platform/state -- start moving_platform_node "
                                "(it also drives the platform; see the vision_node README)")
            elif n > 1:
                problems.append(f"{n} nodes publish /platform/state (expected 1) -- kill the stale one(s): "
                                "pkill -f moving_platform_node")
            else:
                deadline = time.time() + 5.0
                while self.reset._platform_state is None and time.time() < deadline:
                    rclpy.spin_once(self.node, timeout_sec=0.2)
                if self.reset._platform_state is None:
                    problems.append("no /platform/state message received in 5 s")
        if self.node.count_publishers("/rl_observation") > 0:
            self.log("Note: something publishes /rl_observation (vision_relative_state_node / "
                     "relative_state_node / RL run). Not used by this mission; harmless.")
        for problem in problems:
            self.log(f"PREFLIGHT FAILED: {problem}")
        return not problems

    # -- UAV --------------------------------------------------

    def uav_position(self):
        s = self.reset._uav_state
        return (s.x, s.y, -s.z)

    def uav_speed(self):
        s = self.reset._uav_state
        return float(np.linalg.norm([s.vx, s.vy, s.vz]))

    def start(self, x, y, altitude):
        self.reset.start_takeoff({"x": x, "y": y, "z": altitude})

    def command(self, x, y, altitude):
        self.reset.update_takeoff_target({"x": x, "y": y, "z": altitude})

    def land(self):
        self.reset.land_and_disarm()

    def wait_landed(self, timeout):
        start = time.time()
        while time.time() - start < timeout:
            self.sleep(0.2)
            # Vertical speed only: on a moving platform the horizontal speed stays non-zero.
            if self.uav_position()[2] <= TOUCHDOWN_ALTITUDE and abs(self.reset._uav_state.vz) < 0.1:
                break
        return self.uav_position()

    def uav_velocity(self):
        s = self.reset._uav_state
        return (s.vx, s.vy, s.vz)

    def enter_velocity_mode(self):
        """Switch landing_controller to velocity setpoints. It only streams
        offboard setpoints once it has a command, so publish a zero one first
        (otherwise PX4 would drop out of offboard for a few ticks)."""
        self._cmd_pub.publish(LandingCommand())
        self.sleep(0.1)
        self.reset.finish_takeoff()

    def command_velocity(self, north, east, down):
        msg = LandingCommand()
        msg.vx, msg.vy, msg.vz, msg.yaw_rate = float(north), float(east), float(down), 0.0
        self._cmd_pub.publish(msg)

    def start_platform(self):
        for _ in range(3):  # publisher/subscriber discovery can swallow the first message
            self._start_pub.publish(Empty())
            self.sleep(0.2)

    def platform_truth(self):
        """Sim ground truth from /platform/state, converted to PX4 local NED:
        (north, east, v_north, v_east), or None. Evaluation only, never steering."""
        p = self.reset._platform_state
        if p is None:
            return None
        north, east = self.reset.platform_position_local(p.x, p.y)
        return (north, east, p.vy, p.vx)

    def drain_samples(self):
        """New absolute marker samples (time, x, y) since the last call."""
        samples = list(self._pending)
        self._pending.clear()
        return samples

    # -- vision -----------------------------------------------

    def _on_uav_history(self, msg):
        self._uav_history.add(time.time(), msg.x, msg.y)

    def _on_px4_alive(self, _msg):
        self._last_px4_msg_time = time.time()

    def telemetry_stale(self, max_age=2.0):
        """True if no RAW PX4 message (/fmu/out/vehicle_local_position_v1) has arrived in the last
        `max_age` s -- PX4 (and so, almost always, Gazebo) has stopped publishing: a crash or hang, not a
        normal 'nothing changed this tick'. Deliberately not based on /uav/state -- see the comment on its
        subscription above."""
        return self._last_px4_msg_time is None or time.time() - self._last_px4_msg_time > max_age

    def _on_target(self, msg):
        self._messages.append((time.time(), bool(msg.detected)))
        s = self.reset._uav_state
        if not msg.detected or s is None:
            return
        now = time.time()
        captured = now - self.camera_latency
        uav_then = self._uav_history.at(captured) or (s.x, s.y)
        est_x, est_y = uav_then[0] + msg.relative_x, uav_then[1] + msg.relative_y
        self._detections.append((now, est_x, est_y, msg.relative_x, msg.relative_y, msg.relative_z))
        # The tracker gets the CAPTURE time, so its velocity fit and forward prediction are in the right time frame.
        self._pending.append((captured, est_x, est_y, now))
        self._raw.append((now, s.x + msg.relative_x, s.y + msg.relative_y, s.vx, s.vy))

    def stream_summary(self, window):
        """(messages, of which detected) received on /landing_target in the last `window` s."""
        now = time.time()
        recent = [m for m in self._messages if now - m[0] <= window]
        return len(recent), sum(1 for m in recent if m[1])

    def confirmed(self, count, window):
        now = time.time()
        return sum(1 for d in self._detections if now - d[0] <= window) >= count

    def estimate(self):
        """Mean absolute marker (x, y) over the latest few FRESH detections,
        or None if there is no current detection."""
        now = time.time()
        fresh = [d for d in self._detections if now - d[0] <= self.fresh_age]
        if not fresh:
            return None
        last = fresh[-self.estimate_window:]
        return (float(np.mean([d[1] for d in last])), float(np.mean([d[2] for d in last])))

    def relative_measurement(self, window):
        """(mean rel_x, rel_y, rel_z, n) over the last `window` s, or None."""
        now = time.time()
        recent = [d for d in self._detections if now - d[0] <= window]
        if not recent:
            return None
        return (float(np.mean([d[3] for d in recent])), float(np.mean([d[4] for d in recent])),
                float(np.mean([d[5] for d in recent])), len(recent))
