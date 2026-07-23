import numpy as np

from utils.schedule import decay_rate_from_schedule


class ExplorationManager:
    """
    Handles epsilon-greedy exploration.
    """

    def __init__(self, parameters):

        self.parameters = parameters

        self.epsilon = (
            parameters.rl_parameters.exploration_initial_eps
        )

    def choose_action(
        self,
        state,
        q_table,
        q_table_double,
        number_actions
    ):
        """
        Choose action using epsilon-greedy policy.
        """

        if np.random.rand() < self.epsilon:

            return np.random.randint(number_actions)

        q_mean = (
            q_table[state]
            + q_table_double[state]
        ) / 2.0

        return np.argmax(q_mean)

    def update(self, episode):
        """
        Update epsilon according to schedule.
        """

        self.epsilon = decay_rate_from_schedule(
            episode,
            self.parameters.rl_parameters.exploration_rate_schedule,
            None
        )

    def set_value(self, epsilon):
        """
        Restore epsilon from checkpoint.
        """

        self.epsilon = epsilon

    def get_value(self):
        """
        Current exploration rate.
        """

        return self.epsilon