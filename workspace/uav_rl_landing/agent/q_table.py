"""
q_table.py

Creates and manages the Q-Tables used by Double Q-Learning.
"""

import numpy as np

from utils.grid_utils import initialize_grid_list


class QTableManager:

    def __init__(self, grid, number_of_actions):

        self.grid = grid
        self.num_actions = number_of_actions

        self.q_table = None
        self.q_table_double = None
        self.state_action_counter = None

    def initialize_tables(self):
        """
        Create:

        Q(s,a)
        DoubleQ(s,a)
        VisitCounter(s,a)
        """

        init_shape = np.zeros(self.num_actions)

        self.q_table = initialize_grid_list(
            self.grid,
            init_shape
        )

        self.q_table_double = initialize_grid_list(
            self.grid,
            init_shape
        )

        self.state_action_counter = initialize_grid_list(
            self.grid,
            np.zeros(self.num_actions, dtype=np.int64)
        )

        return (
            self.q_table,
            self.q_table_double,
            self.state_action_counter
        )