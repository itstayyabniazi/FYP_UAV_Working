#!/usr/bin/env python3
"""
Publishes the moving platform's ground-truth state (PlatformState, the RL
pipeline's reference) and drives the actual Gazebo model
(models/moving_platform/model.sdf) in sync via a Twist command on
/model/moving_platform/cmd_vel -- bridged to Gazebo Transport by ros_gz_bridge,
see the package README for the exact spawn + bridge commands.

Trajectory: circular motion around (center_x, center_y) at a fixed height,
the simplest of the "rectilinear periodic movement" scenarios described by
the reference paper, parametrized by radius and angular_speed. Position and
velocity are both computed analytically as functions of elapsed time, so
there's no integration drift on the RL/ground-truth side. The actual Gazebo
model is only driven by an open-loop velocity command though (no pose
feedback/correction) -- it will track this closely for the slow, smooth
motion typical of a landing platform, but nothing here corrects for any
drift between the model's simulated position and this analytic ground truth
over a long-running training session. Add periodic resync (e.g. via a
ros_gz_bridge service bridge for /world/<world>/set_pose) if that turns out
to matter in practice.
"""
import math
import time

import rclpy
from rclpy.node import Node

from interfaces.msg import PlatformState
from geometry_msgs.msg import Twist


class MovingPlatformNode(Node):

    def __init__(self):
        super().__init__("moving_platform_node")

        self.declare_parameter("radius", 1.5)         # [m]
        self.declare_parameter("angular_speed", 0.3)   # [rad/s]
        self.declare_parameter("center_x", 0.0)        # [m]
        self.declare_parameter("center_y", 0.0)        # [m]
        self.declare_parameter("z", 0.025)             # [m] -- match the spawn height
        self.declare_parameter("publish_hz", 20.0)

        self.radius = self.get_parameter("radius").value
        self.angular_speed = self.get_parameter("angular_speed").value
        self.center_x = self.get_parameter("center_x").value
        self.center_y = self.get_parameter("center_y").value
        self.z = self.get_parameter("z").value
        publish_hz = self.get_parameter("publish_hz").value

        self.state_publisher = self.create_publisher(
            PlatformState, "/platform/state", 10,
        )
        self.cmd_vel_publisher = self.create_publisher(
            Twist, "/model/moving_platform/cmd_vel", 10,
        )

        # t=0 of the trajectory below is "whenever this node starts", not
        # whenever the Gazebo model was spawned -- spawn the model at rest at
        # (center_x + radius, center_y, z) (t=0's position) before starting
        # this node, and start this node soon after, so the two agree from
        # then on. See the package README for the exact spawn command.
        self.start_time = time.time()

        self.timer = self.create_timer(1.0 / publish_hz, self.publish_platform)

        self.get_logger().info(
            f"Moving Platform Node Started: circular motion, "
            f"radius={self.radius}m, angular_speed={self.angular_speed}rad/s, "
            f"center=({self.center_x}, {self.center_y})"
        )

    def publish_platform(self):

        t = time.time() - self.start_time
        omega = self.angular_speed

        x = self.center_x + self.radius * math.cos(omega * t)
        y = self.center_y + self.radius * math.sin(omega * t)
        vx = -self.radius * omega * math.sin(omega * t)
        vy = self.radius * omega * math.cos(omega * t)
        yaw = math.atan2(vy, vx)  # face the direction of travel

        msg = PlatformState()
        msg.x = x
        msg.y = y
        msg.z = self.z
        msg.vx = vx
        msg.vy = vy
        msg.vz = 0.0
        msg.yaw = yaw
        self.state_publisher.publish(msg)

        cmd = Twist()
        cmd.linear.x = vx
        cmd.linear.y = vy
        cmd.linear.z = 0.0
        self.cmd_vel_publisher.publish(cmd)


def main():

    rclpy.init()

    node = MovingPlatformNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
