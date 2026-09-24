#!/usr/bin/env python3
"""
Publishes the moving platform's ground-truth state (PlatformState, the RL
pipeline's reference) and drives the actual Gazebo model
(models/moving_platform/model.sdf) in sync via a Twist command on
/model/moving_platform/cmd_vel -- bridged to Gazebo Transport by ros_gz_bridge,
see the package README for the exact spawn + bridge commands.

Trajectory (parameter `motion`):
  - "circular" (default): motion around (center_x, center_y) at a fixed height,
    parametrized by radius and angular_speed.
  - "linear": straight line from (start_x, start_y) along heading_deg (0 = east,
    90 = north) at `speed`; with travel_length > 0 it goes back and forth over
    that distance, with 0 it goes one way forever. Same spawn rule: spawn the
    Gazebo model at (start_x, start_y).
Optional `wait_for_start`: hold still at the start until a std_msgs/Empty
arrives on /moving_platform/start (the vision landing mission can send it once
it is airborne, so every run begins with the platform in the same place).
Position and
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

import rclpy
from rclpy.node import Node

from interfaces.msg import PlatformState
from geometry_msgs.msg import Twist
from std_msgs.msg import Empty

from moving_platform.trajectories import circular_state, linear_state


class MovingPlatformNode(Node):

    def __init__(self):
        super().__init__("moving_platform_node")

        self.declare_parameter("radius", 1.5)         # [m]
        self.declare_parameter("angular_speed", 0.3)   # [rad/s]
        self.declare_parameter("center_x", 0.0)        # [m]
        self.declare_parameter("center_y", 0.0)        # [m]
        self.declare_parameter("z", 0.025)             # [m] -- match the spawn height
        self.declare_parameter("publish_hz", 20.0)

        self.declare_parameter("motion", "circular")   # "circular" | "linear"
        self.declare_parameter("start_x", 10.0)        # [m] linear: start point (spawn here)
        self.declare_parameter("start_y", 0.0)         # [m]
        self.declare_parameter("heading_deg", 90.0)    # linear: 0 = east, 90 = north
        self.declare_parameter("speed", 0.4)           # [m/s] linear speed
        self.declare_parameter("travel_length", 0.0)   # [m] linear: >0 = back and forth over this distance
        self.declare_parameter("wait_for_start", False)  # hold still until /moving_platform/start

        self.radius = self.get_parameter("radius").value
        self.angular_speed = self.get_parameter("angular_speed").value
        self.center_x = self.get_parameter("center_x").value
        self.center_y = self.get_parameter("center_y").value
        self.z = self.get_parameter("z").value
        publish_hz = self.get_parameter("publish_hz").value
        self.motion = self.get_parameter("motion").value
        if self.motion not in ("circular", "linear"):
            raise ValueError(f"motion must be 'circular' or 'linear', got {self.motion!r}")
        self.start_x = self.get_parameter("start_x").value
        self.start_y = self.get_parameter("start_y").value
        self.heading_deg = self.get_parameter("heading_deg").value
        self.speed = self.get_parameter("speed").value
        self.travel_length = self.get_parameter("travel_length").value
        self.moving = not self.get_parameter("wait_for_start").value

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
        self.start_time = self._now()

        self.create_subscription(Empty, "/moving_platform/start", self._on_start, 10)

        self.timer = self.create_timer(1.0 / publish_hz, self.publish_platform)

        if self.motion == "linear":
            length = (f"back and forth over {self.travel_length} m" if self.travel_length > 0
                      else "one way, no end")
            description = (f"linear motion from ({self.start_x}, {self.start_y}) heading "
                           f"{self.heading_deg} deg at {self.speed} m/s, {length}")
        else:
            description = (f"circular motion, radius={self.radius}m, "
                           f"angular_speed={self.angular_speed}rad/s, "
                           f"center=({self.center_x}, {self.center_y})")
        if not self.moving:
            description += " -- HOLDING STILL until /moving_platform/start"
        self.get_logger().info(f"Moving Platform Node Started: {description}")

    def _now(self):
        """Seconds on the ROS clock. Wall time by default; SIM time with `-p use_sim_time:=true` (needs
        `ros2 run ros_gz_bridge parameter_bridge /clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock`). The Gazebo model is
        commanded in metres per SIM second, so if the simulation runs slower than real time (real-time factor < 1,
        common with PX4 SITL + camera rendering) a wall-clock trajectory drifts ahead of where the model really is
        -- e.g. 10% at RTF 0.9 = 4.8 m after two minutes at 0.4 m/s."""
        return self.get_clock().now().nanoseconds * 1e-9

    def _on_start(self, _msg):
        if not self.moving:
            self.moving = True
            self.start_time = self._now()
            self.get_logger().info("Start received -- platform is now moving.")

    def _state_at(self, t):
        if self.motion == "linear":
            return linear_state(t, self.start_x, self.start_y, self.heading_deg,
                                self.speed, self.travel_length)
        return circular_state(t, self.center_x, self.center_y, self.radius, self.angular_speed)

    def publish_platform(self):

        if not self.moving:
            self._held_ticks = getattr(self, "_held_ticks", 0) + 1
            if self._held_ticks % int(20 * self.get_parameter("publish_hz").value) == 1:   # ~ every 20 s
                self.get_logger().info(
                    "Platform is HOLDING STILL, waiting for /moving_platform/start (the vision mission sends it "
                    "with --start-platform once it is airborne; or by hand: ros2 topic pub --once "
                    "/moving_platform/start std_msgs/msg/Empty '{}').")
        t = (self._now() - self.start_time) if self.moving else 0.0
        x, y, vx, vy = self._state_at(t)
        if not self.moving:
            vx = vy = 0.0
        # Face the direction of travel (keep the last heading when stationary).
        yaw = math.atan2(vy, vx) if (vx or vy) else getattr(self, "_last_yaw", 0.0)
        self._last_yaw = yaw

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
