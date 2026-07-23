"""
reset_manager.py

Handles episode reset / takeoff logic.

Flow per episode (orchestrated by landing_env.reset()):
1. generate_initial_pose() -- sample a target (x, y, init_altitude AGL)
2. start_takeoff(pose) -- put landing_controller into "position" mode and
   publish that as its TakeoffSetpoint; PX4 actually flies there.
3. landing_env spins, polling is_at_target(pose), until convergence or a
   timeout (parameters.simulation_parameters.takeoff_timeout) is hit.
4. finish_takeoff() -- switch landing_controller to "velocity" mode, handing
   control to the RL agent's LandingCommand (via action_manager).

This does NOT attempt to teleport the Gazebo entity (an earlier version tried
ros_gz_interfaces/SetEntityPose): flying to the target for real is more
reliable -- a teleport leaves PX4's EKF believing it's still where it was,
fighting the discontinuity -- and it's the only approach that still makes
sense once the moving platform actually moves. There is currently no
equivalent of the paper's /gazebo/reset_world for PX4 SITL + Gazebo Harmonic
in this repo: episodes fly back-to-back in one continuously running
simulation rather than a fully reset one.
"""

import numpy as np

from interfaces.msg import UAVState
from interfaces.msg import TakeoffSetpoint
from std_msgs.msg import String


class ResetManager:

    def __init__(self, node, parameters):
        """
        node : rclpy.node.Node
            The owning node, used to create subscriptions/publishers.
        """

        self.node = node
        self.parameters = parameters

        self._uav_state = None
        node.create_subscription(UAVState, "/uav/state", self._on_uav_state, 10)

        self._takeoff_setpoint_pub = node.create_publisher(
            TakeoffSetpoint, "/takeoff_setpoint", 10,
        )
        self._control_mode_pub = node.create_publisher(
            String, "/landing_controller/control_mode", 10,
        )

    def _on_uav_state(self, msg):
        self._uav_state = msg

    # ---------------------------------------------------------
    # Initial Position Generation
    # ---------------------------------------------------------

    def generate_initial_pose(self):
        """Generate the UAV's initial (x, y, altitude-AGL) target for this episode."""

        sim = self.parameters.simulation_parameters

        if sim.init_distribution == "normal":
            x = np.random.normal(sim.init_mu_x, sim.init_sigma_x)
        else:
            x = np.random.uniform(sim.init_min_x, sim.init_max_x)

        y = np.random.uniform(sim.init_min_y, sim.init_max_y)
        z = sim.init_altitude

        return {"x": float(x), "y": float(y), "z": float(z)}

    # ---------------------------------------------------------
    # Takeoff (position-hold phase)
    # ---------------------------------------------------------

    def start_takeoff(self, pose):
        """Command landing_controller into position-hold mode, targeting `pose`."""

        self.node.get_logger().info(f"Takeoff -> {pose}")

        mode_msg = String()
        mode_msg.data = "position"
        self._control_mode_pub.publish(mode_msg)

        setpoint = TakeoffSetpoint()
        setpoint.x = pose["x"]
        setpoint.y = pose["y"]
        setpoint.z = -pose["z"]  # altitude AGL -> PX4 local NED (z down positive)
        setpoint.yaw = 0.0
        self._takeoff_setpoint_pub.publish(setpoint)

    def is_at_target(self, pose) -> bool:
        """True once /uav/state has converged on `pose` within tolerance."""

        if self._uav_state is None:
            return False

        sim = self.parameters.simulation_parameters
        target_z_ned = -pose["z"]

        position_error = float(np.linalg.norm([
            self._uav_state.x - pose["x"],
            self._uav_state.y - pose["y"],
            self._uav_state.z - target_z_ned,
        ]))
        speed = float(np.linalg.norm([
            self._uav_state.vx, self._uav_state.vy, self._uav_state.vz,
        ]))

        return (
            position_error <= sim.takeoff_position_tolerance
            and speed <= sim.takeoff_velocity_tolerance
        )

    def finish_takeoff(self):
        """Hand control back to the RL agent's velocity commands."""

        mode_msg = String()
        mode_msg.data = "velocity"
        self._control_mode_pub.publish(mode_msg)

    # ---------------------------------------------------------
    # Platform Reset
    # ---------------------------------------------------------

    def reset_platform(self):
        """
        Reset moving platform. moving_platform_node currently always publishes
        a stationary platform, so there's nothing to reset yet -- placeholder
        for once it has an actual trajectory generator.
        """

        self.node.get_logger().info("Reset moving platform (no-op: platform is currently stationary)")
