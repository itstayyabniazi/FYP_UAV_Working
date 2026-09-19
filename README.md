# FYP UAV — Autonomous Landing of a Multi-Rotor on a Moving Platform

Final Year Project: a multi-rotor UAV that autonomously detects and lands on a platform that is
itself moving, using reinforcement learning to control the approach and descent instead of a
hand-tuned classical controller.

The project is a from-scratch port of the ideas behind
[*Reinforcement Learning based Autonomous Multi-Rotor Landing on Moving Platforms*](https://link.springer.com/article/10.1007/s10514-024-10162-8)
(Goldschmid & Ahmad) — same core task, a tabular Double Q-learning agent with curriculum-style
state discretization — rebuilt on a modern PX4 + ROS 2 + Gazebo Harmonic stack instead of the
paper's ROS 1 + RotorS + Gazebo Classic one.

---

## 1. Introduction

The goal is to land a quadrotor on a platform (a small pad) that is continuously moving, without
relying on a pre-programmed trajectory: an RL agent observes the drone's position/velocity
*relative to the platform* and outputs control commands, learning through repeated simulated
landing attempts to close the gap and touch down safely as the platform moves beneath it.

The system is split into two halves that mirror how a real deployment would work:

- **A ROS 2 pipeline** (`ros2_ws/`) that talks to the flight controller (PX4, over
  `micro-XRCE-DDS`) and the simulated moving platform, computes the relative state between the
  two, and forwards control commands back to PX4 as an offboard setpoint.
- **An RL training module** (`uav_rl_landing/`) that consumes that relative state, decides an
  action (currently: a forward/backward velocity adjustment), and learns from the outcome of each
  simulated landing attempt.

Everything currently runs against PX4 SITL + Gazebo Harmonic in a Dockerized development
environment; there is no real-hardware deployment yet (see [§4](#4-whats-left-to-be-done)).

---

## 2. Prerequisites

### Host machine
- Linux with Docker and Docker Compose (developed on Ubuntu-based distros; an NVIDIA/AMD/Intel
  GPU with working DRI passthrough is used for the Gazebo GUI — see `docker/docker-compose.yml`
  for the `/dev/dri` device mapping)
- X11 (for the Gazebo GUI to display on the host)

### Inside the Docker container (`docker/Dockerfile`)
| Component | Version | Notes |
|---|---|---|
| OS | Ubuntu 22.04 (Jammy) | base image |
| ROS 2 | Humble | `ros-humble-desktop` |
| Gazebo | Harmonic (`gz sim` 8.14) | installed from OSRF's apt repo |
| `ros_gz_bridge` / `ros_gz_sim` | built **from source** (`humble` branch, `GZ_VERSION=harmonic`) | the apt-packaged versions are linked against Gazebo *Fortress* (`libignition-transport11`), not Harmonic, and silently fail to bridge any topic — see git history for the debugging trail |
| PX4-Autopilot | SITL, `x500` model | cloned separately into `workspace/px4/` at dev time, **not committed** (large, environment-specific) |
| Micro XRCE-DDS Agent | `v2.4.2` (eProsima) | built from source into `workspace/tools/`, **not committed**; bridges PX4's uORB topics onto the ROS 2/DDS side |
| `px4_msgs` | matching your PX4 version | cloned into `ros2_ws/src/px4_msgs`, **not committed** |
| `pymavlink` | latest (pip) | used as a lightweight, headless "GCS" — PX4 refuses to arm without a MAVLink heartbeat from *something*, and a full QGroundControl GUI isn't needed for automated runs (see `workspace/tools/gcs_heartbeat.py`) |
| Python | 3.10 (system) | `rclpy`, `numpy` |

None of PX4-Autopilot, `px4_msgs`, or Micro XRCE-DDS Agent are committed to this repo (see
`.gitignore`) — they're large, environment-pinned, and normally vendored locally per the
PX4/ROS 2 tutorials rather than checked into a project repo.

### Quick start
```bash
cd docker
docker compose build      # first build: ~20-30 min (compiles ros_gz from source)
docker compose up -d
docker compose exec fyp-uav bash
```
(`make build` / `make up` / `make shell` from the repo root do the same thing — see `Makefile`.)
Then, inside the container: build PX4 SITL, start the Micro XRCE-DDS Agent and a GCS heartbeat
(`workspace/tools/gcs_heartbeat.py`), and see
[`uav_rl_landing/README.md`](workspace/uav_rl_landing/README.md) and
[`moving_platform/README.md`](workspace/ros2_ws/src/moving_platform/README.md) for the full
node-by-node launch sequence.

---

## 3. What's been accomplished

### Roadmap

| Phase | Goal | Status |
|---|---|---|
| **1** | Take off and land on a **static platform whose coordinates are hard-coded** in the code | **Completed** (verified in simulation) |
| **2** | Take off, **search for the platform's ArUco marker with the downward camera**, and land on it — no coordinates given to the drone | **Completed** (verified in simulation) — see [§3.2](#32-phase-2--camera-guided-landing-on-a-static-platform-completed) |
| **3** | Land on a **moving platform**, with both **linear** and **circular** motion | **Next** — see [§3.3](#33-phase-3--landing-on-a-moving-platform-next) |
| 4+ | RL-controlled approach (the Q-learning work in §3.4), real hardware | Not started |

### 3.1 Phase 1 — takeoff and landing on hard-coded platform coordinates (completed)

The drone takes off, flies to the platform's saved location, descends onto it and lands. Confirmed in
PX4 SITL + Gazebo Harmonic: the drone ends up on the platform, not merely near it.

- **Where the location lives:** `platform_world_x/y` in
  [`config/parameters.py`](workspace/uav_rl_landing/config/parameters.py), in **Gazebo world
  coordinates** (ENU: x = east, y = north). Currently `(10, 3)`.
- **Frame conversion:** PX4 flies in a local NED frame (x = north, y = east) whose origin is the
  UAV's spawn point, so `ResetManager.platform_position_local()` converts the Gazebo coordinates
  (`platform (10, 3)` → PX4 target `north = 3, east = 10`). An early version passed the Gazebo numbers
  straight through, swapping x and y — that is why the drone first landed ~7 m from the platform.
  If you set `PX4_GZ_MODEL_POSE` when launching PX4, mirror its x/y into `uav_spawn_world_x/y`.
- **The mission:** [`mission/takeoff_and_land.py`](workspace/uav_rl_landing/mission/takeoff_and_land.py)
  — take off to 3 m, hold above the platform, descend at 0.35 m/s holding x/y, hand the last 0.5 m to
  PX4's own `AUTO.LAND`, and report the final distance from the platform centre. It reads the target
  from `/platform/state` and **refuses to take off** if more than one node publishes that topic (a
  stale `moving_platform_node` did exactly that once), the platform is reported moving, or its
  position disagrees with the configured one.

Running it (each in its own terminal, `source /opt/ros/humble/setup.bash` and
`source /workspace/ros2_ws/install/setup.bash` first; PX4 SITL, the Micro-XRCE-DDS Agent and
`tools/gcs_heartbeat.py` already running):
```bash
# spawn the platform where parameters.py says it is, and hold it still there
ros2 run ros_gz_sim create -world default -file $(ros2 pkg prefix moving_platform)/share/moving_platform/models/moving_platform/model.sdf -name moving_platform -x 10.0 -y 3.0 -z 0.025
ros2 run moving_platform moving_platform_node --ros-args -p center_x:=10.0 -p center_y:=3.0 -p radius:=0.0 -p angular_speed:=0.0

ros2 run px4_bridge uav_state_node
ros2 run landing_controller landing_controller_node

cd /workspace/uav_rl_landing && python3 -m mission.takeoff_and_land
```
The spawn `-x/-y`, the node's `center_x/center_y` and `platform_world_x/y` must always agree.

### 3.2 Phase 2 — camera-guided landing on a static platform (completed)

The drone is **not told where the platform is**. It takes off to 5 m and flies the corners of a square
(A → B → C → D), hovering 2 s at each, while the ArUco detector watches the downward camera. The moment
the marker is confirmed (3 detections within 1 s) — mid-leg or at a corner — it stops the patrol,
centres over the marker, descends only while aligned, and hands the last 0.5 m to PX4's `AUTO.LAND`.
Full run sequence, tunables and troubleshooting: the
[`vision_node` README](workspace/ros2_ws/src/vision_node/README.md).

**Result in PX4 SITL + Gazebo Harmonic** (platform at Gazebo `(10, 3)`, drone spawned at the origin):
the drone detected the marker just after leaving corner B, landed, and ended **0.05 m from the platform
centre** (the platform's half-width is 0.75 m); the camera's own marker estimate was within 0.03 m of
where it landed. The camera frame convention (`CAMERA_TO_BODY`) was verified at three known hover
points before this: measured relative offsets matched the expected ones to ~0.1 m in x/y.

Run it (each node in its own terminal, `source /opt/ros/humble/setup.bash` and
`source /workspace/ros2_ws/install/setup.bash` first; PX4 SITL, the Micro-XRCE-DDS Agent and
`tools/gcs_heartbeat.py` already running; **do not** run `moving_platform_node`):
```bash
ros2 run ros_gz_sim create -world default -file $(ros2 pkg prefix moving_platform)/share/moving_platform/models/moving_platform/model.sdf -name moving_platform -x 10.0 -y 3.0 -z 0.025
ros2 run ros_gz_bridge parameter_bridge /drone_camera@sensor_msgs/msg/Image@gz.msgs.Image /drone_camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo
ros2 run px4_bridge uav_state_node
ros2 run landing_controller landing_controller_node
ros2 run vision_node aruco_landing_target_node

cd /workspace/uav_rl_landing && python3 -m mission.vision_landing_main
```
Optional live view: `ros2 run rqt_image_view rqt_image_view /landing_target/debug_image` (detections drawn
on the camera frame).

What was learned building it (worth knowing before Phase 3):
- **The UAV's own rotor arms and props block the outer ~130 px on each side of the camera image**, so the
  usable footprint at 5 m is only ~5 m east-west × ~6.3 m north-south. Patrol legs must pass close to
  where the platform might be.
- The mission cross-checks the camera against the configured platform location (sim ground truth only,
  never used to steer). A > 1 m disagreement prints a `MISMATCH` line (with a swapped/flipped-axis hint) and
  **lands instead of following the estimate**; `--no-ground-truth` disables it. The first-sight estimate at
  the image edge can be ~0.6 m off before the drone centres over the marker, so that limit has limited margin.
- The preflight refuses to arm unless the camera, `/uav/state` and `/landing_target` are all live, and
  exactly one node publishes `/landing_target`. (A silent aruco node and a stale duplicate publisher each
  cost a debugging round earlier.)
- `aruco_landing_target_node` falls back to the ideal pinhole intrinsics for the 80° FOV if no
  `camera_info` arrives within 2 s (it logs a warning), because a silent wait made it publish nothing.

### 3.3 Phase 3 — landing on a moving platform (next)

Goal: the same take-off → find-by-camera → land sequence, but the platform is **moving**, with two motion
types: **linear** and **circular**.

What already exists: `moving_platform_node` drives the Gazebo platform along a **circle** (radius,
angular speed and centre are ROS parameters; default 1.5 m at 0.3 rad/s ≈ 0.45 m/s) and publishes the
analytic ground truth on `/platform/state`. What is still missing or will need to change:
- **Linear motion** does not exist yet — needs a linear mode in `moving_platform_node` (constant-velocity
  or back-and-forth along a line), spawned/driven consistently with its ground truth.
- **The Phase 2 landing logic assumes a static marker.** It averages *absolute* marker positions,
  descends toward a frozen estimate below 1 m (where the marker leaves the camera's view), and hands off
  to `AUTO.LAND` at a fixed x/y. For a moving platform it must instead estimate the marker's velocity,
  lead it, keep following it all the way down, and land with matched velocity.
- **The search:** a fixed patrol may never meet a moving target; the search/acquire logic needs a rethink.
- **Known open issues to fix on the way:** `relative_state_node` subtracts an ENU platform position from
  an NED UAV position (swapped axes in the ground-truth observation); the Gazebo platform is driven
  open-loop and can drift from its analytic ground truth; there is no contact sensor.

No Phase 3 code has been written yet.

### 3.4 Earlier work (ROS 2 pipeline, RL agent, moving platform, vision pipeline)

- **Full ROS 2 pipeline, confirmed running end to end against live PX4 SITL + Gazebo Harmonic**:
  `px4_bridge` (PX4 topics → `UAVState`) → `relative_state` (→ `RLObservation`) →
  `landing_controller` (→ PX4 offboard setpoint). Verified by actually arming and flying the
  simulated vehicle, not just unit-level checks.
- **A working Double Q-learning RL agent** (`uav_rl_landing/`), ported from the paper's tabular,
  curriculum-discretized design: state discretizer, reward function, episode termination/success
  logic, exploration schedule, and the training loop itself (`agent/q_learning.py`) all
  implemented and exercised against the real simulation, producing real episodes with plausible
  outcomes (`crash_landing`/`timeout`/`success`).
- **A real takeoff / position-hold phase**: `landing_controller` supports both PX4 position and
  velocity offboard control, so each episode starts by actually flying the UAV to a sampled
  starting pose and holding there before handing control to the RL agent — not a Gazebo
  teleport (which doesn't work reliably against a live PX4 EKF).
- **A moving platform that actually moves**: a Gazebo model driven by a real (circular) velocity
  trajectory, with the UAV's episode-start position sampled relative to the platform's live
  location, replacing an earlier stationary stub.
- **A working, from-source `ros_gz` build baked into the Dockerfile**, fixing a Gazebo
  Fortress/Harmonic version-mismatch bug that silently broke every `ros_gz_bridge` topic bridge
  and `ros2 run ros_gz_sim create` spawn call.
- Along the way: fixed a duplicate ROS 2 node-name collision, a false-"success"-on-the-ground
  termination bug, several missing `package.xml` dependencies, and PX4's arm-retry logic (it
  previously only attempted to arm once, ever).
- **The UAV actually lands, disarms, and sits still between episodes** instead of bouncing/RTL-ing
  forever: episode-end now hands off to PX4's own `AUTO.LAND` flight mode (its real
  descent-to-touchdown-to-disarm sequence) rather than trying to fake a landing under offboard
  control, which is what PX4's land-detector actually needs to ever accept a disarm command.
- **A full ArUco-marker vision pipeline** (`vision_node`): camera → marker detection → solvePnP →
  UAV-relative pose → `/rl_observation`, as an alternative to ground truth for real/open-world
  deployment (landing on an actual moving car, not just a Gazebo box) — see
  `workspace/ros2_ws/src/vision_node/README.md`. Training still uses ground truth; this is the
  demo/deployment path.

## 4. What's left to be done

- **No real training run yet.** Everything above gets an episode running correctly; nobody has
  yet let it train for the hours needed to see `success_fraction` actually climb as epsilon
  decays. That's the immediate next step.
- **1D control only.** The agent currently only adjusts forward/backward velocity (`vx`); lateral
  (`vy`) and descent-rate control are fixed, not learned — matching the paper's own default
  scope, but short of the full landing problem.
- **No contact sensor.** Touchdown is inferred from altitude + horizontal offset + speed
  thresholds, not a real Gazebo contact event — there's no bridged contact-sensor plugin yet.
- **Vision pipeline: verified in simulation for a static platform only** (Phase 2, §3.2). It has not been
  run against a moving platform or a real camera; relative velocity is still a raw finite difference (no
  filtering). RL training still uses ground truth by design.
- **Reward function is unnormalized.** `reward.py`'s weights were tuned (in the reference paper)
  for observations clipped to `[-1,1]`; here they're applied to raw meters/m·s⁻¹, so
  `episode_reward` lands in the thousands rather than a small bounded number. Not broken, just
  worth revisiting once real learning curves are being analyzed.
- **Curriculum learning is simplified.** State discretization uses even bins per curriculum step
  rather than the paper's non-uniform goal-region binning, and the Q-table doesn't grow/transfer
  knowledge across curriculum steps automatically — advancing the curriculum still requires a
  manual re-run, same as the original paper's own workflow.
- **Episode reset is incomplete.** There's no equivalent of a full Gazebo world reset; the
  position-hold takeoff phase also targets a single point sampled once per episode while the
  platform keeps moving, so by the time RL control begins the platform has moved on.
- **Open-loop platform motion can drift.** The Gazebo model is driven by velocity commands with
  no pose feedback, so it can slowly diverge from the analytic ground-truth trajectory over a long
  run — uncorrected for now.
- **No real-hardware deployment.** Everything so far is simulation-only.
