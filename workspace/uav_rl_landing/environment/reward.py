import numpy as np


class RewardManager:
    """
    Computes the reinforcement learning reward.

    This class contains the complete reward function used during
    UAV landing training.
    """

    def __init__(self, parameters):

        self.parameters = parameters

        sim = parameters.simulation_parameters

        self.w_p = sim.w_p
        self.w_v = sim.w_v
        self.w_theta = sim.w_theta
        self.w_dur = sim.w_dur
        self.w_fail = sim.w_fail
        self.w_suc = sim.w_suc

    def position_reward(self,
                        rel_px,
                        rel_py):

        distance = np.sqrt(rel_px ** 2 + rel_py ** 2)

        return self.w_p * distance

    def velocity_reward(self,
                        rel_vx,
                        rel_vy):

        velocity = np.sqrt(rel_vx ** 2 + rel_vy ** 2)

        return self.w_v * velocity

    def heading_reward(self,
                       rel_yaw):

        return self.w_theta * abs(rel_yaw)

    def duration_reward(self):

        return self.w_dur

    def success_reward(self):

        return self.w_suc

    def failure_reward(self):

        return self.w_fail

    def compute_reward(
            self,
            observation,
            done=False,
            success=False):

        reward = 0.0

        reward += self.position_reward(
            observation.rel_p_x,
            observation.rel_p_y,
        )

        reward += self.velocity_reward(
            observation.rel_v_x,
            observation.rel_v_y,
        )

        reward += self.heading_reward(
            observation.rel_yaw,
        )

        reward += self.duration_reward()

        if done:

            if success:
                reward += self.success_reward()
            else:
                reward += self.failure_reward()

        return reward