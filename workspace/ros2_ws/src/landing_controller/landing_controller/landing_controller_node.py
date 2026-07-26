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
        # the RL agent's LandingCommand takes over for the episode itself, and
        # "disarm" briefly at the end of each episode -- see reset_manager.py's
        # land_and_disarm(). Without this, reset() used to fly straight from
        # wherever the previous episode ended (often still resting on/near the
        # platform) to the next episode's takeoff target while still armed.
        self.mode = "position"

        # Latest setpoint for each mode. Both start out None -- control_loop()
        # won't publish anything (and PX4 won't be commanded into offboard/armed)
        # until the mode currently selected has received at least one setpoint.
        self.takeoff_setpoint = None
        self.command = None

        self.offboard_counter = 0
        self.disarm_counter = 0

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
        if msg.data not in ("position", "velocity", "disarm"):
            self.get_logger().warn(f"Ignoring unknown control mode: {msg.data!r}")
            return
        if msg.data != self.mode:
            self.get_logger().info(f"Control mode: {self.mode} -> {msg.data}")
            if msg.data == "disarm":
                self.disarm_counter = 0
                # Hand the actual landing off to PX4's own AUTO.LAND, rather
                # than us faking a touchdown under offboard velocity control
                # (tried and unreliable -- see engage_land_mode()'s docstring).
                self.engage_land_mode()
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

    def disarm(self):
        msg = VehicleCommand()
        msg.timestamp = self.get_clock().now().nanoseconds // 1000
        msg.command = VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM
        msg.param1 = 0.0

        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1

        msg.from_external = True

        self.command_pub.publish(msg)

        self.get_logger().info("Disarm Command Sent")

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

    def engage_land_mode(self):
        """
        Switch PX4 into its own AUTO.LAND flight mode instead of us trying to
        fake a touchdown under offboard velocity control.

        Two things were tried and both failed to ever get PX4 to accept a
        disarm: (1) holding a position setpoint at ground level just makes
        the controller hover near the ground -- PX4's land-detector keys off
        measured thrust/velocity actually settling from real ground contact,
        not the commanded position, so it never fires; (2) commanding a
        constant descent velocity under offboard control was meant to let
        Gazebo's rigid-body contact stop the vehicle, but in practice this
        still never converged to a state PX4 recognized as landed. AUTO.LAND
        is PX4's own well-tested descent-to-touchdown-to-disarm sequence and
        is what actually drives its land-detector correctly; letting it own
        the landing instead of reimplementing it ourselves is the reliable
        fix. control_loop() stops streaming offboard setpoints once this
        mode is engaged (see the "disarm" branch there) so we don't fight it.
        """
        msg = VehicleCommand()
        msg.timestamp = self.get_clock().now().nanoseconds // 1000
        msg.command = VehicleCommand.VEHICLE_CMD_DO_SET_MODE

        msg.param1 = 1.0  # custom mode enabled
        msg.param2 = 4.0  # PX4_CUSTOM_MAIN_MODE_AUTO
        msg.param3 = 6.0  # PX4_CUSTOM_SUB_MODE_AUTO_LAND

        msg.target_system = 1
        msg.target_component = 1

        msg.source_system = 1
        msg.source_component = 1

        msg.from_external = True

        self.command_pub.publish(msg)

        self.get_logger().info("Land Command Sent")

    def control_loop(self):

        if self.mode == "position" and self.takeoff_setpoint is None:
            return
        if self.mode == "velocity" and self.command is None:
            return

        if self.mode == "disarm":
            # PX4 is now in AUTO.LAND (engaged once on entering this mode,
            # see control_mode_callback) and driving its own descent -- don't
            # stream offboard setpoints here, that would fight/override it.
            # Retry a manual disarm periodically as a fallback in case
            # COM_DISARM_LAND auto-disarm isn't enabled in this PX4 build;
            # harmless once PX4 has already disarmed itself.
            self.disarm_counter += 1
            if self.disarm_counter % 20 == 0:
                self.disarm()
            return

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

        self.offboard_counter += 1

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