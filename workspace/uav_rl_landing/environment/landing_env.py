"""
Reinforcement learning environment for UAV landing on a moving platform.

This is an rclpy.Node, not a gym.Env: rclpy nodes need to own their executor,
and the training loop here is a synchronous spin-between-steps loop (see
agent/q_learning.py), not a generic Gym runner. The previous version of this
file subclassed gym.Env and imported rospy/gazebo_msgs, neither of which
exist in this ROS 2 / Gazebo Harmonic environment.
"""
import time

import rclpy
from rclpy.node import Node

from interfaces.msg import RLObservation

from environment.state_discretizer import StateDiscretizer
from environment.reward import RewardManager
from environment.termination import TerminationManager
from environment.action_manager import ActionManager
from environment.reset_manager import ResetManager
from config.parameters import Parameters


class LandingEnv(Node):

    def __init__(self, parameters: Parameters = None):

        super().__init__("landing_env")

        self.parameters = parameters or Parameters()

        self.discretizer = StateDiscretizer(self.parameters)
        self.reward_manager = RewardManager(self.parameters)
        self.termination_manager = TerminationManager(self.parameters)
        self.action_manager = ActionManager(self, self.parameters)
        self.reset_manager = ResetManager(self, self.parameters)

        self.running_step_time = self.parameters.rl_parameters.running_step_time

        self._latest_observation = None
        self.create_subscription(
            RLObservation,
            "/rl_observation",
            self._on_observation,
            10,
        )

        self.episode = 0
        self.step_number_in_episode = 0
        self.episode_reward = 0.0
        # Only "success"/"crash_landing" come from termination.py's near-ground
        # (minimum_altitude) branch -- "out_of_bounds"/"timeout" can end an
        # episode with the UAV still mid-air, and PX4 correctly refuses to
        # disarm something it doesn't believe has landed. reset() only
        # attempts a disarm when this says it's safe to.
        self._last_outcome = None

    def _on_observation(self, msg):
        self._latest_observation = msg

    def _spin_for(self, duration_sec: float):
        """Spin this node's callbacks for approximately duration_sec, so
        subscription callbacks (and service futures) are actually processed
        while the agent "waits" for the next control period."""

        end_time = time.time() + duration_sec
        while True:
            remaining = end_time - time.time()
            if remaining <= 0:
                break
            rclpy.spin_once(self, timeout_sec=remaining)

    def _spin_until_observation(self, timeout_sec: float = 5.0):
        start = time.time()
        while self._latest_observation is None:
            rclpy.spin_once(self, timeout_sec=0.1)
            if time.time() - start > timeout_sec:
                raise TimeoutError(
                    "No message received on /rl_observation -- "
                    "is relative_state_node running?"
                )

    def reset(self):
        """
        Reset the episode: sample a target pose, fly there for real and hold
        (position-hold, see reset_manager.py) until converged or a timeout is
        hit, then hand control to the RL agent's velocity commands and return
        the first discretized state.
        """

        if self._last_outcome in ("success", "crash_landing"):
            # Only disarm when the previous episode actually ended near the
            # ground -- attempting it after "out_of_bounds"/"timeout" (UAV
            # potentially still mid-air) gets rejected by PX4 ("Disarming
            # denied: not landed"), and that's fine: those cases fly straight
            # into the next takeoff the same way they always safely did.
            self.reset_manager.land_and_disarm()
            self._spin_for(self.parameters.simulation_parameters.post_landing_rest_time)

        pose = self.reset_manager.generate_initial_pose()
        self.reset_manager.start_takeoff(pose)
        self.reset_manager.reset_platform()
        self.termination_manager.reset()

        self._wait_for_takeoff(pose)

        self.action_manager.reset()
        self.action_manager.publish()
        self.reset_manager.finish_takeoff()

        self._latest_observation = None
        self._spin_until_observation()

        self.step_number_in_episode = 0
        self.episode_reward = 0.0
        self.episode += 1

        return self.discretizer.discretize(self._latest_observation)

    def _wait_for_takeoff(self, pose):
        timeout_sec = self.parameters.simulation_parameters.takeoff_timeout
        start = time.time()
        while not self.reset_manager.is_at_target(pose):
            if time.time() - start > timeout_sec:
                self.get_logger().warn(
                    f"Takeoff did not converge within {timeout_sec}s; "
                    "starting the episode anyway from wherever the UAV currently is."
                )
                return
            self._spin_for(0.2)

    def step(self, action: int):
        """Apply one discrete action, advance one control period, and return
        (state, reward, done, info)."""

        self.action_manager.update(action)
        self.action_manager.publish()

        self._spin_for(self.running_step_time)

        observation = self._latest_observation
        state = self.discretizer.discretize(observation)

        self.step_number_in_episode += 1

        done, outcome, success = self.termination_manager.check(
            observation, self.step_number_in_episode,
        )

        reward = self.reward_manager.compute_reward(
            observation, done=done, success=success,
        )
        self.episode_reward += reward

        if done:
            self._last_outcome = outcome

        info = {"outcome": outcome, "success": success}
        return state, reward, done, info

    def close(self):
        self.destroy_node()
