#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from interfaces.msg import UAVState
from interfaces.msg import PlatformState
from interfaces.msg import RLObservation


class RelativeStateNode(Node):

    def __init__(self):

        super().__init__("relative_state_node")

        self.uav = None
        self.platform = None

        self.create_subscription(
            UAVState,
            "/uav/state",
            self.uav_callback,
            10,
        )

        self.create_subscription(
            PlatformState,
            "/platform/state",
            self.platform_callback,
            10,
        )

        self.publisher = self.create_publisher(
            RLObservation,
            "/rl_observation",
            10,
        )

        self.timer = self.create_timer(
            0.02,
            self.publish_observation,
        )

        self.get_logger().info("Relative Observation Node Started")

    def uav_callback(self, msg):
        self.uav = msg

    def platform_callback(self, msg):
        self.platform = msg

    def publish_observation(self):

        if self.uav is None:
            return

        if self.platform is None:
            return

        obs = RLObservation()

        # Relative Position
        obs.rel_x = self.platform.x - self.uav.x
        obs.rel_y = self.platform.y - self.uav.y
        obs.rel_z = self.platform.z - self.uav.z

        # Relative Velocity
        obs.rel_vx = self.platform.vx - self.uav.vx
        obs.rel_vy = self.platform.vy - self.uav.vy
        obs.rel_vz = self.platform.vz - self.uav.vz

        # UAV Attitude
        obs.roll = self.uav.roll
        obs.pitch = self.uav.pitch
        obs.yaw = self.uav.yaw

        # Relative yaw, wrapped to [-pi, pi]
        obs.rel_yaw = math.atan2(
            math.sin(self.platform.yaw - self.uav.yaw),
            math.cos(self.platform.yaw - self.uav.yaw),
        )

        # Platform Velocity
        obs.platform_vx = self.platform.vx
        obs.platform_vy = self.platform.vy
        obs.platform_vz = self.platform.vz

        # Euclidean Distance
        obs.distance = math.sqrt(
            obs.rel_x**2 +
            obs.rel_y**2 +
            obs.rel_z**2
        )

        # Ground truth is always "detected" by definition -- only the vision
        # path (vision_relative_state_node) ever reports this false, when the
        # ArUco marker drops out of view. See termination.py's target-lost
        # watchdog, the only consumer that branches on this field.
        obs.detected = True

        self.publisher.publish(obs)


def main():

    rclpy.init()

    node = RelativeStateNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()