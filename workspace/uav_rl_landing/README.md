# uav_rl_landing

Tabular Double Q-learning agent (Hasselt 2010) for landing on the moving platform, ported from
the reference paper's `custom_q_learning`/`landing_simulation_env`/`utils_multiresolution` design
to this repo's ROS 2 Humble + PX4 + Gazebo Harmonic stack.

This is a plain Python module (not an ament package) run against an already-sourced ROS 2
workspace, using `interfaces/msg/RLObservation` and `interfaces/msg/LandingCommand` as its ROS
boundary. It does not simulate anything itself — it drives the pipeline already defined in
`ros2_ws`: `px4_bridge` → `relative_state` → **this agent** → `/landing_command` /
`/takeoff_setpoint` → `landing_controller` → PX4 offboard setpoint.

## Status: runs end to end against live PX4 SITL + Gazebo Harmonic

Confirmed working on real hardware (a Docker container running Ubuntu 22.04 + ROS 2 Humble + PX4
SITL + `gz sim` 8.14 / Gazebo Harmonic): all 5 nodes start, the message chain flows
(`/fmu/out/...` → `/uav/state` → `/rl_observation`), and `agent/q_learning.py` runs episodes
end to end. Two real bugs were found and fixed by actually running it (see git history):
`px4_bridge` and `relative_state` both registered an `rclpy` node under the identical name
`"relative_state_node"`, and `termination.py` was reporting `success` after ~1 second on every
episode because nothing commanded the UAV to actually take off, so it stayed on the ground the
whole time (near-zero horizontal offset + near-zero velocity + `rel_z` already below
`minimum_altitude` reads as an instant "landing").

Fixing the second bug properly needed a real takeoff phase (below) rather than a one-line patch —
velocity-only control can't get a PX4 vehicle to a target position/altitude on its own. **This
takeoff phase has not itself been run against live hardware yet** — it's the next thing to
validate.

## Takeoff / reset phase

`landing_controller_node` now has two modes, switched via `/landing_controller/control_mode`
(`std_msgs/String`, `"position"` or `"velocity"`):

- **`"position"`** (default, and used during reset): follows `/takeoff_setpoint`
  (`interfaces/msg/TakeoffSetpoint`) as a PX4 position offboard setpoint.
- **`"velocity"`**: follows `/landing_command` (`interfaces/msg/LandingCommand`) as a PX4 velocity
  offboard setpoint — this is the RL agent's actual control output during an episode.

`landing_env.reset()` now: samples a target pose → `reset_manager.start_takeoff(pose)` (switches
`landing_controller` to `"position"` mode, publishes the target) → spins, polling
`reset_manager.is_at_target(pose)` against real `/uav/state` telemetry, until converged within
`simulation_parameters.takeoff_position_tolerance`/`takeoff_velocity_tolerance` or
`takeoff_timeout` (15s default) elapses → `reset_manager.finish_takeoff()` (switches to
`"velocity"` mode) → the RL agent's `LandingCommand`s take over for the episode.

This replaces an earlier attempt at repositioning the Gazebo entity directly
(`ros_gz_interfaces/srv/SetEntityPose`), which was removed: flying to the target for real is more
reliable (a teleport leaves PX4's EKF believing it never moved, fighting the discontinuity), and
it's the only approach that still makes sense once the moving platform actually moves. There is
still no equivalent of the paper's `/gazebo/reset_world` here — episodes fly back-to-back in one
continuously running simulation rather than a fully reset one.

## Deliberate simplifications (read before extending)

- **State space is 1D (longitudinal) only**: `rel_x`, `rel_vx`, matching the paper's own default
  config. `rel_y`/`rel_vy` bounds are still enforced as termination criteria, but aren't part of
  the discretized state or controlled by the agent yet. Extend
  `uav_parameters.observation_msg_strings` (and `rl_parameters.discretization_steps`) to add axes
  once 1D is validated.
- **No relative-acceleration observation.** The paper derived `rel_a_x` by filtering; nothing here
  computes or publishes an acceleration signal, so that curriculum axis is dropped entirely.
- **Curriculum discretization is simplified**: `state_discretizer.py` uses evenly-spaced bins
  within the current curriculum step's range, not the paper's non-uniform goal-region binning
  scheme. The Q-table also does not grow/copy across curriculum steps the way the paper's did —
  advancing `rl_parameters.curriculum_step` just narrows the bin range for the *same*-sized table
  next run. Curriculum progression is still the same manual between-runs workflow as the paper
  (train → bump `curriculum_step` → optionally `--load_data_from` the previous run → re-run).
- **No contact sensor.** "Touchdown" in `termination.py` is inferred purely from altitude above
  the platform (`rel_z`) crossing `minimum_altitude`, combined with horizontal offset and closing
  speed, and only once the UAV has actually been airborne past `airborne_altitude_threshold` this
  episode (guards against the false-"success"-on-the-ground bug above) — there's no Gazebo
  contact-sensor plugin bridged into ROS 2 yet.
- **`moving_platform_node` is still a stub** (always publishes a stationary platform at the
  origin) — that's the other repo priority you deprioritized this round. Training will "work" but
  against a fixed target until that's implemented.

## Running

```bash
# terminal 1: your Gazebo + PX4 SITL + Micro-XRCE-DDS-Agent launch, plus
colcon build --packages-select interfaces px4_bridge relative_state moving_platform landing_controller
source install/setup.bash
ros2 run px4_bridge uav_state_node              # UAVState from PX4 topics
ros2 run moving_platform moving_platform_node  # PlatformState (stub)
ros2 run relative_state relative_state_node    # RLObservation
ros2 run landing_controller landing_controller_node

# terminal 2, from workspace/uav_rl_landing (with the same ROS 2 workspace sourced):
python3 -m agent.q_learning
```

Sanity checks before trusting a training run: `ros2 topic echo /uav/state --once` and
`ros2 topic echo /rl_observation --once` should both show live, changing data; watch the first
episode or two of `q_learning.py`'s log output and confirm `outcome` looks plausible (a UAV that
climbs out to `init_altitude` and only then descends toward the platform, not an instant
`success`/`timeout` on step 1).
