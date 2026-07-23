#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from interfaces.msg import LandingCommand

from px4_msgs.msg import OffboardControlMode
from px4_msgs.msg import TrajectorySetpoint
from px4_msgs.msg import VehicleCommand

from rclpy.qos import QoSProfile
from rclpy.qos import ReliabilityPolicy
from rclpy.qos import HistoryPolicy
from rclpy.qos import DurabilityPolicy


class LandingController(Node):

    def __init__(self):

        super().__init__("landing_controller")

        # Latest velocity command from the RL agent (uav_rl_landing/environment/action_manager.py).
        # None until the agent has published at least once.
        self.command = None

        self.offboard_counter = 0

        px4_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        self.create_subscription(
            LandingCommand,
            "/landing_command",
            self.command_callback,
            10
        )

        self.offboard_pub = self.create_publisher(
            OffboardControlMode,
            "/fmu/in/offboard_control_mode",
            px4_qos
        )

        self.traj_pub = self.create_publisher(
            TrajectorySetpoint,
            "/fmu/in/trajectory_setpoint",
            px4_qos
        )

        self.command_pub = self.create_publisher(
            VehicleCommand,
            "/fmu/in/vehicle_command",
            px4_qos
        )

        self.timer = self.create_timer(
            0.05,
            self.control_loop
        )

        self.get_logger().info("Landing Controller Started")

    def command_callback(self, msg):
        self.command = msg

    def arm(self):
        msg = VehicleCommand()
        msg.timestamp = self.get_clock().now().nanoseconds // 1000
        msg.command = VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM
        msg.param1 = 1.0

        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1

        msg.from_external = True

        self.command_pub.publish(msg)

        self.get_logger().info("Arm Command Sent")

    def engage_offboard_mode(self):
        msg = VehicleCommand()
        msg.timestamp = self.get_clock().now().nanoseconds // 1000
        msg.command = VehicleCommand.VEHICLE_CMD_DO_SET_MODE

        msg.param1 = 1.0
        msg.param2 = 6.0

        msg.target_system = 1
        msg.target_component = 1

        msg.source_system = 1
        msg.source_component = 1

        msg.from_external = True

        self.command_pub.publish(msg)

        self.get_logger().info("Offboard Command Sent")


    def control_loop(self):

        if self.command is None:
            return

        self.offboard_counter += 1

        offboard = OffboardControlMode()
        offboard.timestamp = self.get_clock().now().nanoseconds // 1000
        offboard.position = False
        offboard.velocity = True
        offboard.acceleration = False
        offboard.attitude = False
        offboard.body_rate = False

        self.offboard_pub.publish(offboard)

        traj = TrajectorySetpoint()
        traj.timestamp = self.get_clock().now().nanoseconds // 1000

        # PX4 convention: fields not being controlled must be NaN, not 0.0,
        # or PX4 will also try to honor them as an active (zero) setpoint.
        nan = float("nan")
        traj.position[0] = nan
        traj.position[1] = nan
        traj.position[2] = nan
        traj.acceleration[0] = nan
        traj.acceleration[1] = nan
        traj.acceleration[2] = nan
        traj.yaw = nan

        traj.velocity[0] = self.command.vx
        traj.velocity[1] = self.command.vy
        traj.velocity[2] = self.command.vz
        traj.yawspeed = self.command.yaw_rate

        self.traj_pub.publish(traj)

        if self.offboard_counter == 20:
            self.engage_offboard_mode()

        if self.offboard_counter == 25:
            self.arm()


def main():

    rclpy.init()

    node = LandingController()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()