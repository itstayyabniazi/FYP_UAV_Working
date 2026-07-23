"""
schedule.py

Utility functions for learning-rate and exploration-rate scheduling.
"""

import numpy as np


def decay_rate_from_schedule(
    episode: int,
    schedule: dict,
    default_value: float = None,
):
    """
    Compute a value from a decay schedule.

    Supported schedule types:

        "lin"  -> Linear decay
        "exp"  -> Exponential decay

    Schedule format:

    {
        0: ["lin", start_episode, end_episode,
            start_value, end_value],

        1: ["exp", start_episode, end_episode,
            start_value, end_value],
    }
    """

    # -------------------------------
    # Validate schedule
    # -------------------------------

    for i in range(len(schedule)):

        mode = schedule[i][0]

        assert mode in ["lin", "exp"]

        assert schedule[i][1] < schedule[i][2]

        assert schedule[i][3] >= schedule[i][4]

    for i in range(1, len(schedule)):

        assert (
            schedule[i][1]
            == schedule[i - 1][2]
        )

    # -------------------------------
    # Default value
    # -------------------------------

    decay_rate = default_value

    # -------------------------------
    # Find current interval
    # -------------------------------

    current = None

    for i in range(len(schedule)):

        start = schedule[i][1]
        end = schedule[i][2]

        if start <= episode < end:
            current = i
            break

    # -------------------------------
    # Beyond last interval
    # -------------------------------

    if current is None:

        last = len(schedule) - 1

        return schedule[last][4]

    mode, start_ep, end_ep, start_val, end_val = schedule[current]

    # -------------------------------
    # Linear decay
    # -------------------------------

    if mode == "lin":

        slope = (
            end_val - start_val
        ) / (end_ep - start_ep)

        decay_rate = (
            start_val
            + slope * (episode - start_ep)
        )

    # -------------------------------
    # Exponential decay
    # -------------------------------

    elif mode == "exp":

        B = (
            np.log(start_val)
            - np.log(end_val)
        ) / (start_ep - end_ep)

        A = start_val / np.exp(B * start_ep)

        decay_rate = A * np.exp(B * episode)

    return decay_rate