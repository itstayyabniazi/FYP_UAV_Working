"""
Grid utilities.

This module contains helper functions used for
multi-resolution state discretization.
"""

from copy import deepcopy
import numpy as np

def initialize_grid_list(grid, init_value):
    """
    Create a nested numpy array whose shape matches the
    discretization grid.

    Parameters
    ----------
    grid : list
        List containing each discretization axis.

    init_value :
        Initial value to fill.

    Returns
    -------
    numpy.ndarray
    """

    table = deepcopy(init_value)

    for dimension in reversed(grid):
        table = np.array([deepcopy(table) for _ in range(len(dimension))])

    return table

def create_empty_q_table(grid, n_actions):
    """
    Create an empty Q-table.

    The last dimension corresponds to actions.
    """

    return initialize_grid_list(
        grid,
        np.zeros(n_actions, dtype=np.float32)
    )

def create_visit_counter(grid, n_actions):
    """
    Create the state-action visit counter.
    """

    return initialize_grid_list(
        grid,
        np.zeros(n_actions, dtype=np.int32)
    )

def create_double_q_tables(grid, n_actions):
    """
    Create two Q tables for Double Q-learning.
    """

    q1 = create_empty_q_table(grid, n_actions)
    q2 = create_empty_q_table(grid, n_actions)

    return q1, q2

