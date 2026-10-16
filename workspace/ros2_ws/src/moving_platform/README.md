# moving_platform

Publishes the RL pipeline's ground-truth `PlatformState` and drives an actual moving Gazebo model
so the simulation matches it, instead of the earlier stationary stub.

`moving_platform_node.py` computes a circular trajectory analytically (radius, angular speed,
center — all ROS 2 parameters) and:
1. Publishes `PlatformState` (position + velocity) on `/platform/state` — the RL pipeline's ground
   truth, exact by construction (no integration).
2. Publishes a `geometry_msgs/Twist` on `/model/moving_platform/cmd_vel`, which — once bridged —
   drives the actual `moving_platform` Gazebo model via its `VelocityControl` system plugin
   (`models/moving_platform/model.sdf`). This is open-loop (velocity only, no pose feedback), so
   over a long run it can drift slightly from the analytic ground truth; not corrected for here.

## Linear (straight-line) motion

Besides the default circle, the node can drive the platform along a straight line
(`-p motion:=linear`). Parameters: `start_x`/`start_y` (start point, Gazebo ENU metres -- **spawn the model
here**), `heading_deg` (0 = east, 90 = north), `speed` (m/s), `travel_length` (metres; `0` = go one way
forever, `> 0` = go back and forth over that distance, reversing instantly at each end).

```bash
ros2 run moving_platform moving_platform_node --ros-args \
  -p motion:=linear -p start_x:=10.0 -p start_y:=0.0 -p heading_deg:=90.0 -p speed:=0.4 -p wait_for_start:=true
```
`wait_for_start:=true` holds the platform still at the start point until a `std_msgs/Empty` arrives on
`/moving_platform/start` (the Phase 3 mission sends it once it is airborne, so every run begins with the
platform in the same place). Leave it out and the platform starts moving as soon as the node starts.
The trajectory maths lives in `moving_platform/trajectories.py` (no ROS imports; unit-tested from
`workspace/uav_rl_landing/tests`). Requires the Gazebo model spawned at `start_x, start_y, 0.025` and the cmd_vel
bridge below, exactly as for the circular motion. The node's trajectory clock is the ROS clock: wall time by
default, simulation time with `-p use_sim_time:=true` (needs the `/clock` bridge; see the `vision_node` README, "Simulation
speed") -- use that when Gazebo's real-time factor is below 1, or the analytic ground truth drifts ahead of the model. After changing the package: `colcon build --packages-select
moving_platform` and re-source.

## Platform tracker (live trajectory log in its own terminal)

`platform_tracker` listens to `/platform/state` and shows, in a separate terminal, where the platform is now and where it
has been: the current position in both Gazebo ENU (east, north) and the mission's NED (north, east), speed, compass bearing,
whether it is going straight or turning (with the turning radius), distance travelled, a table of past positions (one row per
second by default) and a top-down ASCII map of the whole path (`S` start, `@` now). It only listens, so it can be started or
restarted at any time.

```bash
ros2 run moving_platform platform_tracker --ros-args -p use_sim_time:=true            # live dashboard
ros2 run moving_platform platform_tracker --ros-args -p use_sim_time:=true -p csv_path:=/workspace/platform_track.csv
ros2 run moving_platform platform_tracker --ros-args -p plain:=true                   # scrolling lines instead of redraw
```

Stop it with **Ctrl+C** (press it a second time if it has not exited within a second; it then force-quits). Ctrl+Z only
suspends it. From another terminal: `pkill -9 -f platform_tracker`.

Other parameters: `history_period` (s, 1.0), `history_rows` (shown, 14), `csv_period` (s, 0.1), `map_width`, `map_height`.
To open it with the other simulation terminals, add `"8-Platform-Tracker"` to `LABELS`, the command above to `CMDS`, and
`"moving_platform platform_tracker"` to `KILL_PATTERNS` in `scripts/run_sim_terminals.sh`. After pulling this change run
`colcon build --packages-select moving_platform` once to register the command. Preview without ROS or Gazebo:
`python3 -m moving_platform.platform_tracker --demo --seconds 60 --seed 5 --speed 1.0`.

## Random motion

`-p motion:=random` drives the platform along a random but smooth, car-like path: constant `speed`, a chain of
straight stretches and arcs with a limited turn rate (heading is continuous, so there are no instant reversals),
confined to an elliptical arena. It is a pure function of time in `moving_platform/trajectories.py`
(`random_state`), shared with the offline test harness.

Parameters: `speed` (m/s, default 0.4 -- pass `0.3` for the low-speed rung), `arena_x`/`arena_y` (arena centre,
default 9.5 / 6.0 -- the platform **starts at the centre, spawn the model there**), `arena_half_x`/`arena_half_y`
(default 1.5 / 5.0 m, sits on the patrol's B to C leg like the circular demo), `max_turn_rate` (rad/s, default
0.6; minimum turning radius is `speed / max_turn_rate`), `seg_min`/`seg_max` (segment length in seconds, default
3 / 8; shorter segments mean more zig-zag), and `seed`. **`seed` defaults to -1: a fresh random path every launch.**
The node prints the seed it picked in its startup line; pass it back as `-p seed:=N` to replay the same path
(offline too: `random_state(t, ..., seed=N)`).

Keep the arena's smaller half-axis above about 2.5x the minimum turning radius, or the platform cannot turn
around inside it (the node warns at startup). Faster platforms need a bigger arena or a higher `max_turn_rate`.

```bash
ros2 run ros_gz_sim create -world default -file $(ros2 pkg prefix moving_platform)/share/moving_platform/models/moving_platform/model.sdf -name moving_platform -x 9.5 -y 6.0 -z 0.025
ros2 run moving_platform moving_platform_node --ros-args -p use_sim_time:=true -p motion:=random -p speed:=0.3 -p wait_for_start:=true
```
After changing the package: `colcon build --packages-select moving_platform` and re-source.

## One-time setup per simulation session

Gazebo (brought up by PX4 SITL) must already be running. Then, **spawn the platform model**
(only needs doing once per Gazebo session — it isn't part of PX4's world file):

```bash
source /opt/ros/humble/setup.bash
source /workspace/ros2_ws/install/setup.bash

ros2 run ros_gz_sim create \
  -world default \
  -file $(ros2 pkg prefix moving_platform)/share/moving_platform/models/moving_platform/model.sdf \
  -name moving_platform \
  -x 1.5 -y 0 -z 0.025
```

The `-x 1.5 -y 0` matches the node's default `radius=1.5`/`center=(0, 0)` trajectory at `t=0`
(`x = center_x + radius`, `y = center_y`) — if you change those parameters, update the spawn
position to match, or the model will start out of sync with the analytic trajectory it's supposed
to be tracking.

Then **bridge the velocity command topic** (leave this running, e.g. in its own terminal):

```bash
ros2 run ros_gz_bridge parameter_bridge \
  /model/moving_platform/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist
```

Then run the node as before:

```bash
ros2 run moving_platform moving_platform_node
```

To change the trajectory: `ros2 run moving_platform moving_platform_node --ros-args -p radius:=2.0 -p angular_speed:=0.2`
(remember to also change the spawn `-x`/`-y` to match).
