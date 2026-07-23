"""
q_learning.py

Double Q-learning training loop (Hasselt 2010), ported from the paper's
custom_q_learning.py to the rclpy-based LandingEnv and the (simpler,
non-curriculum-transferring) StateDiscretizer used in this repo.

Curriculum progression is manual, same workflow as the original paper: train,
then bump parameters.rl_parameters.curriculum_step in config/parameters.py
and re-run with --load_data_from pointing at the previous run's tables.

Run (from workspace/uav_rl_landing, with the ROS 2 workspace + the Gazebo/PX4
simulation already up and running):

    python3 -m agent.q_learning
    python3 -m agent.q_learning --load_data_from ~/uav_rl_landing_results/<run>/final
"""
import argparse
import os
from datetime import datetime

import numpy as np
import rclpy

from agent.q_table import QTableManager
from agent.exploration import ExplorationManager
from config.parameters import Parameters
from environment.landing_env import LandingEnv


def build_grid(parameters: Parameters):
    n_r = parameters.rl_parameters.n_r
    state_names = list(parameters.uav_parameters.observation_msg_strings.values())
    return [list(range(n_r)) for _ in state_names]


class QLearning:

    def __init__(self, parameters: Parameters = None, log_dir: str = None):

        self.parameters = parameters or Parameters()
        rl = self.parameters.rl_parameters

        self.gamma = rl.gamma
        self.max_num_timesteps_episode = rl.max_num_timesteps_episode
        self.max_num_episodes = rl.max_num_episodes
        self.omega = rl.omega
        self.alpha_min = rl.alpha_min
        self.successful_fraction_threshold = rl.successful_fraction

        self.number_of_actions = len(self.parameters.uav_parameters.action_strings)
        grid = build_grid(self.parameters)

        self.q_table_manager = QTableManager(grid, self.number_of_actions)
        self.q_table, self.q_table_double, self.state_action_counter = (
            self.q_table_manager.initialize_tables()
        )

        self.exploration = ExplorationManager(self.parameters)

        self.env = LandingEnv(self.parameters)

        self.log_dir = log_dir
        self.successful_episodes_array = np.zeros(rl.number_of_successful_episodes)
        self.episode = 0

    def load(self, base_path: str):
        """Load previously saved Q-tables (as produced by save())."""
        self.q_table = np.load(base_path + "_Q_table.npy")
        self.q_table_double = np.load(base_path + "_Q_table_double.npy")
        self.state_action_counter = np.load(base_path + "_state_action_counter.npy")

    def save(self, base_path: str):
        np.save(base_path + "_Q_table.npy", self.q_table)
        np.save(base_path + "_Q_table_double.npy", self.q_table_double)
        np.save(base_path + "_state_action_counter.npy", self.state_action_counter)

    def _learning_rate(self, state_action_idx):
        rl = self.parameters.rl_parameters
        if rl.learning_rate == "adaptive":
            visits = self.state_action_counter[state_action_idx]
            return max((1.0 / (visits + 1)) ** self.omega, self.alpha_min)
        elif isinstance(rl.learning_rate, dict):
            from utils.schedule import decay_rate_from_schedule
            return decay_rate_from_schedule(self.episode, rl.learning_rate, None)
        else:
            return rl.learning_rate

    def train(self):

        stop = False
        while self.episode <= self.max_num_episodes and not stop:

            state = self.env.reset()
            done = False
            outcome = "in_progress"

            for _ in range(self.max_num_timesteps_episode):

                action = self.exploration.choose_action(
                    state, self.q_table, self.q_table_double, self.number_of_actions,
                )

                next_state, reward, done, info = self.env.step(action)
                outcome = info["outcome"]

                state_action_idx = state + (action,)
                alpha = self._learning_rate(state_action_idx)

                # Double Q-learning update: randomly update Q_table or Q_table_double,
                # bootstrapping off the *other* table's value estimate.
                if np.random.randint(0, 2) == 0:
                    a_star = int(np.argmax(self.q_table[next_state]))
                    target = 0.0 if done else self.q_table_double[next_state + (a_star,)]
                    td_error = reward + self.gamma * target - self.q_table[state_action_idx]
                    self.q_table[state_action_idx] += alpha * td_error
                else:
                    b_star = int(np.argmax(self.q_table_double[next_state]))
                    target = 0.0 if done else self.q_table[next_state + (b_star,)]
                    td_error = reward + self.gamma * target - self.q_table_double[state_action_idx]
                    self.q_table_double[state_action_idx] += alpha * td_error

                self.state_action_counter[state_action_idx] += 1

                if done:
                    break
                state = next_state

            stop = self._on_episode_end(outcome)

    def _on_episode_end(self, outcome: str) -> bool:
        """Log/save/decay after an episode. Returns True if training should stop."""

        success = outcome == "success"
        self.successful_episodes_array[1:] = self.successful_episodes_array[:-1]
        self.successful_episodes_array[0] = 1 if success else 0
        successful_fraction = float(np.mean(self.successful_episodes_array))

        if self.parameters.rl_parameters.verbose:
            self.env.get_logger().info(
                f"episode={self.episode} outcome={outcome} "
                f"episode_reward={self.env.episode_reward:.2f} "
                f"success_fraction={successful_fraction:.2f} "
                f"epsilon={self.exploration.get_value():.3f}"
            )

        if (
            self.log_dir
            and self.episode % self.parameters.rl_parameters.episode_save_freq == 0
        ):
            self.save(os.path.join(self.log_dir, f"episode_{self.episode}"))

        self.episode += 1
        self.exploration.update(self.episode)

        if successful_fraction >= self.successful_fraction_threshold:
            self.env.get_logger().info(
                f"Stopping: success_fraction {successful_fraction:.2f} reached "
                f"threshold {self.successful_fraction_threshold} at episode {self.episode}."
            )
            return True
        return False


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--load_data_from", type=str, default="")
    parser.add_argument(
        "--log_dir", type=str,
        default=os.path.expanduser("~/uav_rl_landing_results"),
    )
    args, _ = parser.parse_known_args()

    rclpy.init()

    parameters = Parameters()

    run_dir = os.path.join(args.log_dir, datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(run_dir, exist_ok=True)

    q_learning = QLearning(parameters, log_dir=run_dir)

    if args.load_data_from:
        q_learning.load(args.load_data_from)

    try:
        q_learning.train()
    except KeyboardInterrupt:
        pass
    finally:
        q_learning.save(os.path.join(run_dir, "final"))
        q_learning.env.close()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
