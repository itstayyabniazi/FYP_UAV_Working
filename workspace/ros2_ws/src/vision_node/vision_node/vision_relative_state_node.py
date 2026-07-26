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


# How long to keep publishing the last known relative pose after the marker
# is reported lost (LandingTarget.detected=False) before treating it as
# fully stale. See the module docstring's note on target-lost handling being
# a known limitation of this first version -- there's no "target lost"
# termination case wired up yet, so this just avoids the observation
# free-falling to (0,0,0) the instant a single frame misses.
STALE_TARGET_TIMEOUT_SEC = 1.0


class VisionRelativeStateNode(Node):

    def __init__(self):
        super().__init__("vision_relative_state_node")

        self.uav = None
        self.target = None
        self._target_stamp = None

        self._prev_rel = None  # (t, rel_x, rel_y, rel_z) of the last DETECTED target
        self._last_rel_vel = (0.0, 0.0, 0.0)  # last computed (rel_vx, rel_vy, rel_vz)

        self.create_subscription(UAVState, "/uav/state", self.uav_callback, 10)
        self.create_subscription(LandingTarget, "/landing_target", self.target_callback, 10)

        self.publisher = self.create_publisher(RLObservation, "/rl_observation", 10)

        self.timer = self.create_timer(0.02, self.publish_observation)

        self.get_logger().info("Vision Relative State Node Started")

    def uav_callback(self, msg):
        self.uav = msg

    def target_callback(self, msg):
        self.target = msg
        self._target_stamp = self.get_clock().now().nanoseconds / 1e9

    def publish_observation(self):
        if self.uav is None or self.target is None:
            return

        now = self.get_clock().now().nanoseconds / 1e9

        if not self.target.detected:
            if self._target_stamp is None or (now - self._target_stamp) > STALE_TARGET_TIMEOUT_SEC:
                # No usable pose at all yet / for too long -- nothing to publish.
                return
            # else: within the grace window, keep publishing the last
            # message's (frozen) relative pose below.

        rel_x = self.target.relative_x
        rel_y = self.target.relative_y
        rel_z = self.target.relative_z
        rel_yaw = self.target.relative_yaw

        if self.target.detected:
            if self._prev_rel is not None:
                prev_t, prev_x, prev_y, prev_z = self._prev_rel
                dt = now - prev_t
                if dt > 1e-3:
                    rel_vx = (rel_x - prev_x) / dt
                    rel_vy = (rel_y - prev_y) / dt
                    rel_vz = (rel_z - prev_z) / dt
                else:
                    rel_vx, rel_vy, rel_vz = self._last_rel_vel
            else:
                rel_vx, rel_vy, rel_vz = self._last_rel_vel
            self._prev_rel = (now, rel_x, rel_y, rel_z)
            self._last_rel_vel = (rel_vx, rel_vy, rel_vz)
        else:
            # Marker currently not detected (grace window) -- hold the last
            # computed relative velocity rather than snapping to zero.
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

        self.publisher.publish(obs)


def main():
    rclpy.init()

    node = VisionRelativeStateNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
