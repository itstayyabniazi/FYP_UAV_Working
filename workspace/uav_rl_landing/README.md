# uav_rl_landing

Tabular Double Q-learning agent (Hasselt 2010) for landing on the moving platform, ported from
the reference paper's `custom_q_learning`/`landing_simulation_env`/`utils_multiresolution` design
to this repo's ROS 2 Humble + PX4 + Gazebo Harmonic stack.

This is a plain Python module (not an ament package) run against an already-sourced ROS 2
workspace, using `interfaces/msg/RLObservation` and `interfaces/msg/LandingCommand` as its ROS
boundary. It does not simulate anything itself — it drives the pipeline already defined in
`ros2_ws`: `px4_bridge` → `relative_state` → **this agent** → `/landing_command` →
`landing_controller` → PX4 offboard velocity setpoint.

## What changed in this pass

The module existed as scaffolding but didn't run: `landing_env.py`, `action_manager.py` and
`reset_manager.py` imported `rospy`/`gazebo_msgs`/`training_q_learning.msg` (ROS 1 APIs that
don't exist here), `config/parameters.py` and `state_discretizer.py` disagreed on attribute names
(`parameters.rl` vs. `parameters.rl_parameters`), `reward.py` and `state_discretizer.py` expected
observation field names (`rel_p_x`, `rel_v_x`, ...) that don't match what `RLObservation` actually
publishes (`rel_x`, `rel_vx`, ...), and `agent/q_learning.py` — the actual training loop — was an
empty file. All of that is fixed/implemented now:

- `interfaces/msg/RLObservation.msg` gained a `rel_yaw` field (platform yaw − UAV yaw), populated
  in `relative_state_node.py`; `reward.py` already expected it.
- `config/parameters.py`, `state_discretizer.py`, `reward.py` now agree on field names and
  attribute paths.
- `action_manager.py` and `reset_manager.py` are `rclpy`-based. The RL action is now a `vx`
  velocity setpoint (published as `interfaces/msg/LandingCommand`) instead of the paper's `pitch`
  attitude setpoint, since PX4 offboard control here is driven via `TrajectorySetpoint.velocity`.
- `landing_env.py` is an `rclpy.Node` (not a `gym.Env` — rclpy nodes need to own their own spin
  loop; there's no generic Gym runner in play here) tying the discretizer, reward, a new
  `termination.py` (done/success criteria — nothing filled this role before), `action_manager`
  and `reset_manager` together.
- `agent/q_learning.py` now has the actual Double Q-learning training loop.
- `landing_controller_node.py` (in `ros2_ws`) now subscribes to `/landing_command` and forwards it
  as a PX4 velocity offboard setpoint, instead of computing its own naive position setpoint
  directly from `/rl_observation`.

**None of this has been run against a live ROS 2 / PX4 / Gazebo Harmonic instance** — there's no
ROS 2 install available in the environment this was written in. Everything was checked for syntax
(`py_compile`) and cross-file consistency (field names, attribute paths, message shapes) by
reading every file it touches, but integration bugs are still likely on first real run.

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
  speed — there's no Gazebo contact-sensor plugin bridged into ROS 2 yet.
- **Episode reset is only best-effort.** `reset_manager.py` attempts to reposition the UAV entity
  in Gazebo via `ros_gz_interfaces/srv/SetEntityPose` (untested — verify the world/model name for
  your setup), but this does **not** reset PX4's EKF/arming/offboard state. Resetting a PX4 SITL
  episode mid-training is a known-hard problem; decide deliberately how you want to handle it
  (full process respawn per episode vs. re-arm/re-engage-offboard and accept EKF settling time as
  part of the episode boundary) rather than assuming the Gazebo-side reset alone is enough.
- **`moving_platform_node` is still a stub** (always publishes a stationary platform at the
  origin) — that's the other repo priority you deprioritized this round. Training will "work" but
  against a fixed target until that's implemented.

## Running

```bash
# terminal 1: your Gazebo + PX4 SITL + Micro-XRCE-DDS-Agent launch, plus
colcon build --packages-select interfaces px4_bridge relative_state moving_platform landing_controller
source install/setup.bash
ros2 run px4_bridge relative_state_node        # UAVState from PX4 topics
ros2 run moving_platform moving_platform_node  # PlatformState (stub)
ros2 run relative_state relative_state_node    # RLObservation
ros2 run landing_controller landing_controller_node

# terminal 2, from workspace/uav_rl_landing (with the same ROS 2 workspace sourced):
python3 -m agent.q_learning
```
