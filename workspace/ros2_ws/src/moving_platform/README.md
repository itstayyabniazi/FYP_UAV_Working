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
