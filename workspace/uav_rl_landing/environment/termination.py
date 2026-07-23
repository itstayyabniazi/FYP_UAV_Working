"""
termination.py

Episode termination / success logic. This has no equivalent file in the
original scaffold (landing_simulation_object.check_done_criteria() from the
paper was never ported) -- it's new.

IMPORTANT CAVEAT: there is no contact sensor bridged from Gazebo into ROS 2 in
this repo yet (that would need a contact-sensor Gazebo plugin wired through
ros_gz_bridge, similar in spirit to the paper's /moving_platform/contact).
"Touchdown" here is therefore only INFERRED from the UAV's altitude above the
platform (rel_z) crossing simulation_parameters.minimum_altitude, combined
with horizontal offset and closing speed to decide success vs. crash_landing.
Replace this with a real contact event once that sensor exists.

SEPARATE CAVEAT this guards against: with no takeoff/position-hold behavior
implemented yet (see uav_rl_landing/README.md), a UAV that never leaves the
ground has rel_z near 0 from the very first step of the episode -- i.e. below
minimum_altitude before it has ever actually flown. Without a guard, that
reads as an instant "landing" (usually a false "success", since a stationary
grounded drone also has ~0 horizontal offset and ~0 velocity). is_airborne()
requires rel_z to have exceeded airborne_altitude_threshold at least once
during the episode before the minimum_altitude/touchdown branch is allowed to
fire at all; until then, an episode that stays on the ground just runs to
"timeout" instead of a bogus "success".
"""
import numpy as np


class TerminationManager:

    def __init__(self, parameters):
        self.parameters = parameters
        # Minimum altitude above the platform the UAV must have reached at least
        # once this episode before a landing (success/crash) can be registered.
        self.airborne_altitude_threshold = max(
            1.0, 0.5 * parameters.simulation_parameters.init_altitude
        )
        self._max_rel_z_seen = -np.inf

    def reset(self):
        """Call at the start of every episode."""
        self._max_rel_z_seen = -np.inf

    def check(self, observation, step_number_in_episode: int):
        """
        Returns (done: bool, outcome: str, success: bool).

        outcome is one of:
            "in_progress", "timeout", "out_of_bounds", "success", "crash_landing"
        """
        sim = self.parameters.simulation_parameters

        self._max_rel_z_seen = max(self._max_rel_z_seen, observation.rel_z)
        has_been_airborne = self._max_rel_z_seen >= self.airborne_altitude_threshold

        if step_number_in_episode >= self.parameters.rl_parameters.max_num_timesteps_episode:
            return True, "timeout", False

        if sim.done_criteria.get("max_lon_distance", False) and abs(observation.rel_x) >= sim.max_abs_p_x:
            return True, "out_of_bounds", False

        if sim.done_criteria.get("max_lat_distance", False) and abs(observation.rel_y) >= sim.max_abs_p_y:
            return True, "out_of_bounds", False

        if (
            has_been_airborne
            and sim.done_criteria.get("minimum_altitude", False)
            and observation.rel_z <= sim.minimum_altitude
        ):
            horizontal_dist = float(np.hypot(observation.rel_x, observation.rel_y))
            rel_speed = float(np.linalg.norm(
                [observation.rel_vx, observation.rel_vy, observation.rel_vz]
            ))
            success = (
                horizontal_dist <= sim.success_horizontal_radius
                and rel_speed <= sim.success_max_rel_speed
            )
            if success and sim.done_criteria.get("success", False):
                return True, "success", True
            return True, "crash_landing", False

        return False, "in_progress", False
