import gym
import rospy
import numpy as np

from copy import deepcopy

from std_msgs.msg import Float64
from gazebo_msgs.msg import ModelState

from environment.state_discretizer import StateDiscretizer
from config.parameters import Parameters
from environment.reset_manager import ResetManager

class LandingEnv(gym.Env):
    """
    Reinforcement Learning Environment for UAV Landing.
    """

    def __init__(self):

        super().__init__()

        self.parameters = Parameters()

        self.discretizer = StateDiscretizer(self.parameters)

        self.episode = 0
        self.step_number = 0

        self.reward = 0
        self.episode_reward = 0

        self.reset_happened = False

        self.reset_manager = ResetManager(self.parameters)

        self.running_step_time = (
            self.parameters.rl_parameters.running_step_time
        )

    def reset(self):

        """
        Reset simulation and return first observation.
        """

        raise NotImplementedError

    def publish_action(self):

        """
        Publish current action to ROS.
        """

        raise NotImplementedError

    def get_observation(self):

        """
        Read observation from ROS.
        """

        raise NotImplementedError

    def convert_observation(self, observation):

        """
        Normalize observation.
        """

        return observation

    def close(self):

        rospy.signal_shutdown("Environment closed.")