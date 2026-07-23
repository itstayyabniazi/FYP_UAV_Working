from copy import deepcopy

from interfaces.msg import LandingCommand

from config.parameters import Parameters


class ActionManager:
    """
    Handles UAV actions.

    Responsibilities
    ----------------
    - Maintain current control commands (vx, vy, vz, yaw_rate).
    - Update commands from the RL agent's discrete action.
    - Publish commands to ROS 2 as interfaces/msg/LandingCommand, consumed by
      landing_controller_node to drive PX4 offboard velocity control.
    """

    def __init__(self, node, parameters: Parameters):
        """
        node : rclpy.node.Node
            The owning node, used to create the publisher. ActionManager is not
            itself a Node -- rclpy publishers/subscriptions must be owned by one.
        """

        self.parameters = parameters

        self.action_values = deepcopy(
            self.parameters.uav_parameters.initial_action_values
        )

        self.publisher = node.create_publisher(
            LandingCommand,
            "/landing_command",
            10,
        )

    def reset(self):
        """Reset actions to their initial values."""

        self.action_values = deepcopy(
            self.parameters.uav_parameters.initial_action_values
        )

    def update(self, action: int):
        """
        Update action values using the discrete action selected by the RL
        agent. Only vx is controlled by the agent in this MVP; vy, vz and
        yaw_rate stay at their initial (fixed) values.
        """

        action_name = self.parameters.uav_parameters.action_strings[action]

        delta = self.parameters.uav_parameters.action_delta_values["vx"]
        max_vx = self.parameters.uav_parameters.action_max_values["vx"]

        if action_name == "increase_vx":
            self.action_values["vx"] += delta

        elif action_name == "decrease_vx":
            self.action_values["vx"] -= delta

        elif action_name == "do_nothing":
            pass

        else:
            raise ValueError(f"Unknown action: {action_name}")

        self.action_values["vx"] = max(
            -max_vx,
            min(max_vx, self.action_values["vx"])
        )

    def publish(self):
        """Publish the current control command."""

        msg = LandingCommand()

        msg.vx = self.action_values["vx"]
        msg.vy = self.action_values["vy"]
        msg.vz = self.action_values["vz"]
        msg.yaw_rate = self.action_values["yaw_rate"]

        self.publisher.publish(msg)

    def get_action(self):
        """Return the current action values."""

        return deepcopy(self.action_values)
