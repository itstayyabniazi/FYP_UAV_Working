"""
State Discretizer

Converts continuous observations (an interfaces/msg/RLObservation instance, or
anything else that supports attribute access to the same field names) into
discrete grid indices used by the Q-Learning agent.

Replaces the paper's add_cur_step_lims_of_state() / get_discrete_state_from_ros_msg()
/ curriculum discretization logic, simplified to evenly-spaced bins per curriculum
step (the paper additionally shrunk the bin nearest the goal disproportionately;
that refinement isn't reproduced here).
"""

import numpy as np


class StateDiscretizer:

    def __init__(self, parameters):
        self.params = parameters

        self.n_r = parameters.rl_parameters.n_r

        self.state_names = list(
            parameters.uav_parameters.observation_msg_strings.values()
        )

        self.curriculum_step = parameters.rl_parameters.curriculum_step

        self.state_limits = self._build_state_limits()

    def _build_state_limits(self):
        """
        Build discretization limits for every observation according to the
        current curriculum step. Each entry is a list, indexed by curriculum
        step, of (low, high) bounds -- narrower for later curriculum steps.
        """

        limits = {}

        for state in self.state_names:

            max_value = self.params.uav_parameters.observation_max_values[state]
            step_list = list(reversed(self.params.rl_parameters.discretization_steps[state]))

            current = []
            total = len(step_list)

            for i, scale in enumerate(step_list):
                if i >= total - 1 - self.curriculum_step:
                    limit = scale * max_value
                    current.append((-limit, limit))

            limits[state] = current

        return limits

    def discretize_value(self, value, state_name):
        """Convert one continuous value into a discrete bin index (evenly-spaced
        bins over the current curriculum step's [low, high] range)."""

        low, high = self.state_limits[state_name][-1]

        value = np.clip(value, low, high)

        bins = np.linspace(low, high, self.n_r + 1)

        idx = np.digitize(value, bins)

        idx = np.clip(idx, 1, self.n_r) - 1  # zero-based index in [0, n_r - 1]

        return int(idx)

    def discretize(self, observation):
        """
        Convert a continuous observation into a discrete state tuple.

        `observation` must expose each name in self.state_names as an
        attribute (e.g. an interfaces/msg/RLObservation instance).
        """

        state = []

        for name in self.state_names:
            state.append(
                self.discretize_value(getattr(observation, name), name)
            )

        return tuple(state)

    def update_curriculum(self, curriculum_step):
        self.curriculum_step = curriculum_step
        self.state_limits = self._build_state_limits()
