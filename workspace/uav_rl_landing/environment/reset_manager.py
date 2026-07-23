"""
reset_manager.py

Handles episode reset logic.

Responsibilities
----------------
- Generate initial UAV position
- Reset Gazebo simulation
- Reset moving platform
- Reset UAV pose
- Publish reset signals
- Wait until simulation becomes stable
"""

import numpy as np
import rospy

from config.parameters import Parameters


class ResetManager:

    def __init__(self, parameters: Parameters):

        self.parameters = parameters

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def reset_episode(self):
        """
        Main function called every episode.

        Returns
        -------
        dict
            Initial state information.
        """

        initial_pose = self.generate_initial_pose()

        self.reset_simulation()

        self.reset_uav(initial_pose)

        self.reset_platform()

        self.wait_until_ready()

        return initial_pose

    # ---------------------------------------------------------
    # Initial Position Generation
    # ---------------------------------------------------------

    def generate_initial_pose(self):
        """
        Generate UAV initial position according
        to parameters.py.
        """

        sim = self.parameters.simulation_parameters

        if sim.init_distribution == "normal":

            x = np.random.normal(
                sim.init_mu_x,
                sim.init_sigma_x
            )

            y = np.random.normal(
                sim.init_mu_y,
                sim.init_sigma_y
            )

        else:

            x = np.random.uniform(
                sim.init_min_x[0],
                sim.init_max_x[1]
            )

            y = np.random.uniform(
                sim.init_min_y[0],
                sim.init_max_y[1]
            )

        z = sim.init_altitude

        return {
            "x": x,
            "y": y,
            "z": z
        }

    # ---------------------------------------------------------
    # Gazebo Reset
    # ---------------------------------------------------------

    def reset_simulation(self):
        """
        Reset Gazebo simulation.

        Placeholder.
        Later this will call Gazebo services.
        """

        rospy.loginfo("Resetting simulation...")

    # ---------------------------------------------------------
    # UAV Reset
    # ---------------------------------------------------------

    def reset_uav(self, pose):
        """
        Move UAV to initial pose.

        Placeholder.
        """

        rospy.loginfo(f"Reset UAV -> {pose}")

    # ---------------------------------------------------------
    # Platform Reset
    # ---------------------------------------------------------

    def reset_platform(self):
        """
        Reset moving platform.

        Placeholder.
        """

        rospy.loginfo("Reset moving platform")

    # ---------------------------------------------------------
    # Synchronization
    # ---------------------------------------------------------

    def wait_until_ready(self):
        """
        Wait until all ROS topics
        become valid after reset.
        """

        rospy.sleep(1.0)