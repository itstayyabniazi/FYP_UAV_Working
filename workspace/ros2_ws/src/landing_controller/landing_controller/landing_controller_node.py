#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from interfaces.msg import LandingCommand
from interfaces.msg import TakeoffSetpoint
from std_msgs.msg import String

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

        # "position" during the reset/takeoff phase (uav_rl_landing/environment/
        # reset_manager.py flies to + holds a TakeoffSetpoint), "velocity" once
        # the RL agent's LandingCommand takes over for the episode itself.
        self.mode = "position"

        # Latest setpoint for each mode. Both start out None -- control_loop()
        # won't publish anything (and PX4 won't be commanded into offboard/armed)
        # until the mode currently selected has received at least one setpoint.
        self.takeoff_setpoint = None
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

        self.create_subscription(
            TakeoffSetpoint,
            "/takeoff_setpoint",
            self.takeoff_setpoint_callback,
            10
        )

        self.create_subscription(
            String,
            "/landing_controller/control_mode",
            self.control_mode_callback,
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

    def takeoff_setpoint_callback(self, msg):
        self.takeoff_setpoint = msg

    def control_mode_callback(self, msg):
        if msg.data not in ("position", "velocity"):
            self.get_logger().warn(f"Ignoring unknown control mode: {msg.data!r}")
            return
        if msg.data != self.mode:
            self.get_logger().info(f"Control mode: {self.mode} -> {msg.data}")
        self.mode = msg.data

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

        if self.mode == "position" and self.takeoff_setpoint is None:
            return
        if self.mode == "velocity" and self.command is None:
            return

        self.offboard_counter += 1

        offboard = OffboardControlMode()
        offboard.timestamp = self.get_clock().now().nanoseconds // 1000
        offboard.position = self.mode == "position"
        offboard.velocity = self.mode == "velocity"
        offboard.acceleration = False
        offboard.attitude = False
        offboard.body_rate = False

        self.offboard_pub.publish(offboard)

        traj = TrajectorySetpoint()
        traj.timestamp = self.get_clock().now().nanoseconds // 1000

        # PX4 convention: fields not being controlled must be NaN, not 0.0,
        # or PX4 will also try to honor them as an active (zero) setpoint.
        nan = float("nan")
        traj.acceleration[0] = nan
        traj.acceleration[1] = nan
        traj.acceleration[2] = nan

        if self.mode == "position":
            traj.position[0] = self.takeoff_setpoint.x
            traj.position[1] = self.takeoff_setpoint.y
            traj.position[2] = self.takeoff_setpoint.z
            traj.yaw = self.takeoff_setpoint.yaw
            traj.velocity[0] = nan
            traj.velocity[1] = nan
            traj.velocity[2] = nan
            traj.yawspeed = nan
        else:
            traj.position[0] = nan
            traj.position[1] = nan
            traj.position[2] = nan
            traj.yaw = nan
            traj.velocity[0] = self.command.vx
            traj.velocity[1] = self.command.vy
            traj.velocity[2] = self.command.vz
            traj.yawspeed = self.command.yaw_rate

        self.traj_pub.publish(traj)

        # Retry periodically rather than once: PX4 can reject the first arm
        # attempt (e.g. "No connection to the GCS" until QGroundControl/a
        # companion connects) and nothing here currently checks whether it
        # actually succeeded, so a one-shot attempt would never be retried.
        if self.offboard_counter >= 20 and (self.offboard_counter - 20) % 100 == 0:
            self.engage_offboard_mode()

        if self.offboard_counter >= 25 and (self.offboard_counter - 25) % 100 == 0:
            self.arm()


def main():

    rclpy.init()

    node = LandingController()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()