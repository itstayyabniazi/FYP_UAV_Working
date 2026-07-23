import rospy

from copy import deepcopy

from training_q_learning.msg import Action

from config.parameters import Parameters


class ActionManager:
    """
    Handles UAV actions.

    Responsibilities
    ----------------
    • Maintain current control commands.
    • Update commands from RL actions.
    • Publish commands to ROS.
    """

    def __init__(self, parameters: Parameters):

        self.parameters = parameters

        self.action_values = deepcopy(
            self.parameters.uav_parameters.initial_action_values
        )

        self.publisher = rospy.Publisher(
            "training_action_interface/action_to_interface",
            Action,
            queue_size=1,
        )

    def reset(self):
        """
        Reset actions to their initial values.
        """

        self.action_values = deepcopy(
            self.parameters.uav_parameters.initial_action_values
        )

    def update(self, action: int):
        """
        Update action values using the discrete action selected
        by the RL agent.
        """

        action_name = self.parameters.uav_parameters.action_strings[action]

        delta = self.parameters.uav_parameters.action_delta_values["pitch"]

        max_pitch = self.parameters.uav_parameters.action_max_values["pitch"]

        if action_name == "increase_pitch":

            self.action_values["pitch"] += delta

        elif action_name == "decrease_pitch":

            self.action_values["pitch"] -= delta

        elif action_name == "do_nothing":

            pass

        self.action_values["pitch"] = max(
            -max_pitch,
            min(max_pitch, self.action_values["pitch"])
        )

    def publish(self):
        """
        Publish current control command.
        """

        msg = Action()

        msg.pitch = self.action_values["pitch"]
        msg.roll = self.action_values["roll"]
        msg.yaw = self.action_values["yaw"]
        msg.v_z = self.action_values["v_z"]

        self.publisher.publish(msg)

    def get_action(self):
        """
        Return current action values.
        """

        return deepcopy(self.action_values)