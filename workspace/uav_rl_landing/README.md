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
velocity-only control can't get a PX4 vehicle to a target position/altitude on its own.

**Update: the takeoff phase has since been confirmed working against live hardware too.** PX4's
own "No connection to the GCS" arming precondition blocked the first attempt (unrelated to this
pipeline — needs a MAVLink peer such as `pymavlink` sending heartbeats), and
`landing_controller_node` only tried to arm once rather than retrying (fixed). Once both were
addressed, a real run showed the UAV taking off, holding position (`position -> velocity` mode
switch after convergence, well under `takeoff_timeout`), and then genuinely flying and descending
during the RL-controlled phase, ending in `crash_landing` as expected for `epsilon=1.0` (pure
random exploration, before the Q-table has learned anything).

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
- **The moving platform now actually moves** (circular trajectory, see
  [`moving_platform`'s README](../ros2_ws/src/moving_platform/README.md) for the required
  one-time spawn + bridge setup). It's driven open-loop (`VelocityControl`, no pose feedback), so
  it can drift slightly from the analytic `PlatformState` ground truth over a long run —
  uncorrected for now. `reset_manager.generate_initial_pose()` samples the UAV's start position
  relative to wherever the platform *currently* is, but the position-hold takeoff phase still
  targets a single fixed point sampled once at the start of the episode, so by the time the
  RL-controlled phase begins (several seconds later) the platform will have moved on from there —
  see the caveat in `reset_manager.reset_platform()`'s docstring.
- **`reward.py`'s weights are tuned for the paper's normalized `[-1,1]` observations but applied
  here to raw meters/m·s⁻¹** (never rewritten, only the field names were fixed) — expect
  `episode_reward` in the thousands, not a small bounded number. Not broken, just unnormalized;
  worth revisiting if the scale becomes a problem once you're looking at learning curves.

## Running

```bash
# Gazebo + PX4 SITL + Micro-XRCE-DDS-Agent + a MAVLink GCS peer (e.g. pymavlink -- see git
# history/PR discussion; PX4 won't arm without one) already running, then:

colcon build --packages-select interfaces px4_bridge relative_state moving_platform landing_controller
source install/setup.bash

# one-time per Gazebo session -- spawn the platform model and bridge its velocity command;
# see moving_platform/README.md for the exact commands and why the spawn position matters
ros2 run ros_gz_sim create -world default -file $(ros2 pkg prefix moving_platform)/share/moving_platform/models/moving_platform/model.sdf -name moving_platform -x 1.5 -y 0 -z 0.025
ros2 run ros_gz_bridge parameter_bridge /model/moving_platform/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist

# one terminal each:
ros2 run px4_bridge uav_state_node             # UAVState from PX4 topics
ros2 run moving_platform moving_platform_node  # PlatformState + drives the real Gazebo model
ros2 run relative_state relative_state_node    # RLObservation
ros2 run landing_controller landing_controller_node

# from workspace/uav_rl_landing (with the same ROS 2 workspace sourced):
python3 -m agent.q_learning
```

Sanity checks before trusting a training run: `ros2 topic echo /uav/state`,
`ros2 topic echo /platform/state`, and `ros2 topic echo /rl_observation` should all show live,
changing data (`/platform/state` should show `x`/`y` actually varying, not stuck at a constant);
watch the Gazebo GUI to confirm the platform is visibly moving in a circle and the UAV climbs out
before descending toward it, not an instant `success`/`timeout`/`crash_landing` on step 1.
