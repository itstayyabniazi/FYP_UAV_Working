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
