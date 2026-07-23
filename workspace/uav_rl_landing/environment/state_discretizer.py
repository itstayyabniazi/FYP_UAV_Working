"""
State Discretizer

Converts continuous observations into discrete grid indices
used by the Q-Learning agent.

Replaces:

- add_cur_step_lims_of_state()
- get_discrete_state_from_ros_msg()
- curriculum discretization logic
"""

import numpy as np


class StateDiscretizer:

    def __init__(self, parameters):
        self.params = parameters

        self.n_r = parameters.rl.n_r

        self.state_names = list(
            parameters.uav.observation_max_values.keys()
        )

        self.curriculum_step = parameters.rl.curriculum_step

        self.state_limits = self._build_state_limits()

    def _build_state_limits(self):
        """
        Build discretization limits for every observation
        according to the current curriculum step.
        """

        limits = {}

        for state in self.state_names:

            max_value = self.params.uav.observation_max_values[state]

            step_list = self.params.rl.discretization_steps[state]

            step_list = list(reversed(step_list))

            current = []

            total = len(step_list)

            for i, scale in enumerate(step_list):

                if i >= total - 1 - self.curriculum_step:

                    limit = scale * max_value

                    current.append((-limit, limit))

            limits[state] = current

        return limits

    def discretize_value(self,
                         value,
                         state_name):
        """
        Convert one continuous value into
        a discrete bin.
        """

        limits = self.state_limits[state_name][-1]

        low, high = limits

        value = np.clip(value, low, high)

        bins = np.linspace(low, high, self.n_r + 1)

        idx = np.digitize(value, bins)

        idx = np.clip(idx, 1, self.n_r)

        return idx

    def discretize(self,
                   observation):
        """
        Convert a continuous observation
        into a discrete state tuple.

        observation example:

        {
            "rel_p_x": 1.2,
            "rel_v_x": -0.8,
            "rel_a_x": 0.2
        }
        """

        state = []

        for name in self.state_names:

            state.append(
                self.discretize_value(
                    observation[name],
                    name
                )
            )

        return tuple(state)

    def update_curriculum(
            self,
            curriculum_step):

        self.curriculum_step = curriculum_step

        self.state_limits = self._build_state_limits()