#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from interfaces.msg import PlatformState


class MovingPlatformNode(Node):

    def __init__(self):
        super().__init__("moving_platform_node")

        self.publisher = self.create_publisher(
            PlatformState,
            "/platform/state",
            10
        )

        self.timer = self.create_timer(
            0.05,
            self.publish_platform
        )

        self.get_logger().info("Moving Platform Node Started")

    def publish_platform(self):

        msg = PlatformState()

        # Stationary platform
        msg.x = 0.0
        msg.y = 0.0
        msg.z = 0.0

        msg.vx = 0.0
        msg.vy = 0.0
        msg.vz = 0.0

        self.publisher.publish(msg)


def main():

    rclpy.init()

    node = MovingPlatformNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()