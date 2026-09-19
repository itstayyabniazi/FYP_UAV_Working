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

from interfaces.msg import LandingTarget

from config.parameters import Parameters
from environment.reset_manager import ResetManager

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
        self.node.create_subscription(LandingTarget, "/landing_target", self._on_target, 10)

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

    def preflight(self) -> bool:
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
            if self.uav_position()[2] <= TOUCHDOWN_ALTITUDE and self.uav_speed() < 0.1:
                break
        return self.uav_position()

    # -- vision -----------------------------------------------

    def _on_target(self, msg):
        s = self.reset._uav_state
        if not msg.detected or s is None:
            return
        self._detections.append((
            time.time(),
            s.x + msg.relative_x, s.y + msg.relative_y,
            msg.relative_x, msg.relative_y, msg.relative_z,
        ))

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
