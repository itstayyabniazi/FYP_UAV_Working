#!/usr/bin/env python3
"""
Vision-based drop-in alternative to relative_state package's
relative_state_node.py: consumes the ArUco-derived LandingTarget (see
aruco_landing_target_node.py) instead of ground-truth /platform/state, and
publishes the same /rl_observation (RLObservation) the rest of the pipeline
(state_discretizer, reward, termination, landing_controller) already
consumes -- so nothing downstream needs to know or care whether the
platform's position came from ground truth or a camera.

Run this INSTEAD OF relative_state_node (not alongside it -- both publish
/rl_observation, so running both would just have them race/overwrite each
other) for real/vision-based deployment or demoing the open-world "moving
car" scenario. moving_platform_node still needs to run either way in sim, to
actually drive the platform's physical motion -- only its ground-truth
PlatformState publication goes unused on this path.

Target-lost handling: this node ALWAYS publishes an observation once the
marker has been detected at least once (never goes silent), using the last
known relative pose while the marker is out of view, but sets
RLObservation.detected accordingly. termination.py's target-lost watchdog is
the actual consumer of that flag -- it decides how long a loss is tolerated
before ending the episode/flight as "target_lost". This node's own job is
just to report ground truth about what it currently sees, honestly, not to
decide policy about how long is too long.

platform_vx/vy/vz and roll/pitch/yaw semantics: see RLObservation.msg and
relative_state_node.py -- reproduced here to match, with platform velocity
derived as uav.velocity + relative_velocity (since relative_velocity =
platform_velocity - uav_velocity by definition) rather than measured
directly, since a single monocular marker detection has no independent
velocity sensor of its own.
"""
import math

import rclpy
from rclpy.node import Node

from interfaces.msg import UAVState, LandingTarget, RLObservation


class VisionRelativeStateNode(Node):

    def __init__(self):
        super().__init__("vision_relative_state_node")

        self.uav = None

        # Last known good relative pose -- updated only on an actual
        # detection, so a "not detected" LandingTarget (which zeroes its own
        # relative_x/y/z, see aruco_landing_target_node's
        # _publish_not_detected) never overwrites this with a misleading 0.
        self._last_known_rel = None  # (rel_x, rel_y, rel_z, rel_yaw)
        self._last_rel_vel = (0.0, 0.0, 0.0)

        self._detected = False
        self._prev_detection = None  # (t, rel_x, rel_y, rel_z) of the last DETECTED reading

        self.create_subscription(UAVState, "/uav/state", self.uav_callback, 10)
        self.create_subscription(LandingTarget, "/landing_target", self.target_callback, 10)

        self.publisher = self.create_publisher(RLObservation, "/rl_observation", 10)

        self.timer = self.create_timer(0.02, self.publish_observation)

        self.get_logger().info("Vision Relative State Node Started")

    def uav_callback(self, msg):
        self.uav = msg

    def target_callback(self, msg):
        self._detected = msg.detected

        if not msg.detected:
            return  # keep whatever _last_known_rel/_last_rel_vel already holds

        now = self.get_clock().now().nanoseconds / 1e9
        rel_x, rel_y, rel_z = msg.relative_x, msg.relative_y, msg.relative_z

        if self._prev_detection is not None:
            prev_t, prev_x, prev_y, prev_z = self._prev_detection
            dt = now - prev_t
            if dt > 1e-3:
                self._last_rel_vel = (
                    (rel_x - prev_x) / dt,
                    (rel_y - prev_y) / dt,
                    (rel_z - prev_z) / dt,
                )
        self._prev_detection = (now, rel_x, rel_y, rel_z)
        self._last_known_rel = (rel_x, rel_y, rel_z, msg.relative_yaw)

    def publish_observation(self):
        if self.uav is None or self._last_known_rel is None:
            return  # no attitude yet, or the marker has never been seen at all

        rel_x, rel_y, rel_z, rel_yaw = self._last_known_rel
        rel_vx, rel_vy, rel_vz = self._last_rel_vel

        obs = RLObservation()

        obs.rel_x = rel_x
        obs.rel_y = rel_y
        obs.rel_z = rel_z

        obs.rel_vx = rel_vx
        obs.rel_vy = rel_vy
        obs.rel_vz = rel_vz

        obs.roll = self.uav.roll
        obs.pitch = self.uav.pitch
        obs.yaw = self.uav.yaw

        obs.rel_yaw = rel_yaw

        obs.platform_vx = self.uav.vx + rel_vx
        obs.platform_vy = self.uav.vy + rel_vy
        obs.platform_vz = self.uav.vz + rel_vz

        obs.distance = math.sqrt(rel_x ** 2 + rel_y ** 2 + rel_z ** 2)

        obs.detected = self._detected

        self.publisher.publish(obs)


def main():
    rclpy.init()

    node = VisionRelativeStateNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
