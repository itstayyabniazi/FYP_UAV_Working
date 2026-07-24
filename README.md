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

## 4. What's left to be done

- **No real training run yet.** Everything above gets an episode running correctly; nobody has
  yet let it train for the hours needed to see `success_fraction` actually climb as epsilon
  decays. That's the immediate next step.
- **1D control only.** The agent currently only adjusts forward/backward velocity (`vx`); lateral
  (`vy`) and descent-rate control are fixed, not learned — matching the paper's own default
  scope, but short of the full landing problem.
- **No contact sensor.** Touchdown is inferred from altitude + horizontal offset + speed
  thresholds, not a real Gazebo contact event — there's no bridged contact-sensor plugin yet.
- **`vision_node` is an empty stub.** The platform's position is currently taken as ground truth
  from the simulator; there's no camera-based detection (`LandingTarget.msg` already exists as a
  placeholder for this).
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
