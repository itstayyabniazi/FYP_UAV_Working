"""
reset_manager.py

Handles episode reset logic.

Responsibilities
----------------
- Generate initial UAV position
- Best-effort: reposition the UAV in Gazebo between episodes
- Wait until simulation topics look valid again

What this can NOT do (and does not pretend to do)
---------------------------------------------------
Resetting a PX4 SITL + Gazebo Harmonic episode mid-training is a known-hard
problem: repositioning the Gazebo entity does not reset PX4's internal EKF
state, arming state, or offboard-mode bookkeeping, all of which need to be
consistent again before the next episode can safely command velocities. This
class only attempts the Gazebo-side entity pose reset (via
ros_gz_interfaces/srv/SetEntityPose, best-effort, logged if unavailable) and
leaves the PX4-side state-reset problem for you to design deliberately
(common approaches: fully respawn the PX4+Gazebo process per episode, or
disarm/re-trigger the arm+offboard sequence and accept the EKF settling time
as part of the episode boundary). This has not been exercised against a live
Gazebo Harmonic instance -- verify the service name/type/world name for your
world before relying on it.
"""

import numpy as np


class ResetManager:

    def __init__(self, node, parameters, world_name: str = "default", model_name: str = "x500"):
        """
        node : rclpy.node.Node
            The owning node, used for logging and to create the (optional)
            Gazebo reset service client.
        world_name : str
            Name of the Gazebo world, as used in the ros_gz service namespace
            /world/<world_name>/set_pose. Check your world's SDF / launch file.
        model_name : str
            Name of the UAV model/entity in Gazebo.
        """

        self.node = node
        self.parameters = parameters
        self.world_name = world_name
        self.model_name = model_name

        self._set_pose_client = None
        try:
            from ros_gz_interfaces.srv import SetEntityPose
            self._set_pose_client = node.create_client(
                SetEntityPose, f"/world/{world_name}/set_pose"
            )
        except ImportError:
            node.get_logger().warn(
                "ros_gz_interfaces not available; Gazebo entity pose reset is disabled. "
                "Episodes will run back-to-back without repositioning the UAV."
            )

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def reset_episode(self):
        """
        Main function called every episode.

        Returns
        -------
        dict
            Initial state information (target x/y/z for the UAV).
        """

        initial_pose = self.generate_initial_pose()

        self.reset_uav(initial_pose)

        self.reset_platform()

        self.wait_until_ready()

        return initial_pose

    # ---------------------------------------------------------
    # Initial Position Generation
    # ---------------------------------------------------------

    def generate_initial_pose(self):
        """Generate the UAV's initial position according to parameters.py."""

        sim = self.parameters.simulation_parameters

        if sim.init_distribution == "normal":
            x = np.random.normal(sim.init_mu_x, sim.init_sigma_x)
        else:
            x = np.random.uniform(sim.init_min_x, sim.init_max_x)

        y = np.random.uniform(sim.init_min_y, sim.init_max_y)
        z = sim.init_altitude

        return {"x": float(x), "y": float(y), "z": float(z)}

    # ---------------------------------------------------------
    # UAV Reset
    # ---------------------------------------------------------

    def reset_uav(self, pose):
        """
        Best-effort: move the UAV entity to `pose` in Gazebo.

        Does NOT reset PX4's EKF/arming/offboard state -- see module docstring.
        """

        self.node.get_logger().info(f"Reset UAV -> {pose}")

        if self._set_pose_client is None:
            return

        if not self._set_pose_client.wait_for_service(timeout_sec=1.0):
            self.node.get_logger().warn(
                f"/world/{self.world_name}/set_pose service not available; "
                "skipping Gazebo entity pose reset for this episode."
            )
            return

        from ros_gz_interfaces.srv import SetEntityPose
        from ros_gz_interfaces.msg import Entity

        request = SetEntityPose.Request()
        request.entity = Entity()
        request.entity.name = self.model_name
        request.pose.position.x = pose["x"]
        request.pose.position.y = pose["y"]
        request.pose.position.z = pose["z"]
        request.pose.orientation.w = 1.0

        self._set_pose_client.call_async(request)

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

    # ---------------------------------------------------------
    # Synchronization
    # ---------------------------------------------------------

    def wait_until_ready(self):
        """Give topics/services a moment to settle after a reset."""

        import time
        time.sleep(1.0)
