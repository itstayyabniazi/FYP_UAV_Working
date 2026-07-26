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
from interfaces.msg import PlatformState
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

        # Needed so generate_initial_pose() can offset from where the platform
        # actually is right now, not a fixed world origin -- important once
        # it's actually moving (moving_platform_node.py).
        self._platform_state = None
        node.create_subscription(PlatformState, "/platform/state", self._on_platform_state, 10)

        self._takeoff_setpoint_pub = node.create_publisher(
            TakeoffSetpoint, "/takeoff_setpoint", 10,
        )
        self._control_mode_pub = node.create_publisher(
            String, "/landing_controller/control_mode", 10,
        )

    def _on_uav_state(self, msg):
        self._uav_state = msg

    def _on_platform_state(self, msg):
        self._platform_state = msg

    # ---------------------------------------------------------
    # Initial Position Generation
    # ---------------------------------------------------------

    def generate_initial_pose(self):
        """
        Generate the UAV's initial (x, y, altitude-AGL) target for this
        episode. simulation_parameters.init_*_x/y describe an OFFSET from the
        platform's current position (not an absolute world position) -- so
        the sampled starting point stays near the platform regardless of
        where it currently is on its trajectory. Falls back to treating the
        world origin as the platform's position if no /platform/state has
        been received yet.
        """

        sim = self.parameters.simulation_parameters

        if sim.init_distribution == "normal":
            offset_x = np.random.normal(sim.init_mu_x, sim.init_sigma_x)
        else:
            offset_x = np.random.uniform(sim.init_min_x, sim.init_max_x)

        offset_y = np.random.uniform(sim.init_min_y, sim.init_max_y)

        if self._platform_state is not None:
            platform_x = self._platform_state.x
            platform_y = self._platform_state.y
        else:
            platform_x = 0.0
            platform_y = 0.0

        x = platform_x + offset_x
        y = platform_y + offset_y
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
    # End of episode
    # ---------------------------------------------------------

    def land_and_disarm(self):
        """
        Disarm landing_controller (see its "disarm" mode) so the UAV actually
        sits still, rather than flying straight from wherever the previous
        episode ended -- often still resting on/near the platform -- to the
        next episode's takeoff target while still armed. landing_env.reset()
        calls this before generating the next episode's pose; it briefly
        rests (parameters.simulation_parameters.post_landing_rest_time) before
        the next start_takeoff() re-arms and re-engages offboard mode.

        landing_controller's "disarm" mode commands its own constant gentle
        descent (see DISARM_DESCENT_VZ there) rather than holding a position
        setpoint from here -- a position hold only makes PX4 hover near the
        ground, which never satisfies PX4's land-detector (it keys off
        measured thrust/velocity actually settling from ground contact, not
        the commanded position), so disarm would be refused forever. A
        continued descent instead lets the UAV physically settle onto the
        platform, at which point PX4 recognizes it as landed and disarm is
        accepted.
        """

        mode_msg = String()
        mode_msg.data = "disarm"
        self._control_mode_pub.publish(mode_msg)

    # ---------------------------------------------------------
    # Platform Reset
    # ---------------------------------------------------------

    def reset_platform(self):
        """
        Deliberately a no-op: moving_platform_node.py now drives the platform
        on a continuous trajectory independent of episode boundaries, the same
        way a real motorized platform wouldn't pause and reset for each
        landing attempt. generate_initial_pose() re-samples relative to
        wherever the platform currently is instead.

        Known limitation: the position-hold takeoff phase (start_takeoff/
        is_at_target) targets a single fixed point sampled once at the start
        of reset_episode(), while the platform keeps moving during that
        several-second hold -- so by the time the episode's RL-controlled
        phase actually begins, the platform may no longer be as close to the
        UAV's start position as it was at sampling time. Fine for now (the
        UAV still starts in the platform's general operating area), but if
        that turns out to matter, the fix is to re-publish an updated
        TakeoffSetpoint that tracks the platform during the hold instead of a
        single static one.
        """

        pass
