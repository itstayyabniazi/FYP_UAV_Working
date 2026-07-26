# vision_node

ArUco marker-based vision perception for the moving-platform landing target.
This is the **deployment/demo path**, not the training path: RL training
still runs against ground truth (`relative_state` package,
`/platform/state`) exactly as before -- that's what `q_learning.py` has
actually been validated against. This package exists to drive the same
downstream pipeline (`/rl_observation` -> `landing_controller`) from a real
camera instead, for demonstrating the open-world "land on a moving car"
scenario -- the reference paper only ever validated indoors against a Vicon
motion-capture rig, and never used any onboard perception at all.

## Architecture

```
camera (Gazebo sensor / real camera)
  -> aruco_landing_target_node   (ArUco detection + solvePnP -> LandingTarget)
    -> vision_relative_state_node (LandingTarget + /uav/state -> /rl_observation)
      -> (everything downstream is unchanged: state_discretizer, reward,
          termination, landing_controller, q_learning.py)
```

Run `vision_relative_state_node` **instead of** `relative_state_node`, not
alongside it -- both publish `/rl_observation`, so running both would just
have them race each other. `moving_platform_node` still needs to run either
way (it's what actually drives the platform's physical motion in Gazebo);
only its ground-truth `PlatformState` publication goes unused on this path.

## 1. Generate the marker image

The platform model (`../moving_platform/models/moving_platform/model.sdf`)
already has a visual referencing this file; it just needs to exist:

```bash
cd /workspace/ros2_ws/src/moving_platform/scripts
python3 generate_aruco_marker.py
```

Writes `../models/moving_platform/materials/textures/aruco_marker.png`
(DICT_4X4_50, marker id 0 -- keep this in sync with
`aruco_landing_target_node.py`'s `ARUCO_DICT`/`MARKER_ID` if you ever change
either).

## 2. Add a downward camera to the UAV

The x500 model lives inside your PX4-Autopilot checkout, not in this repo
(same reason `workspace/px4/` is gitignored -- it's a multi-GB vendored
tree). Patch it directly:

```bash
cd /workspace/ros2_ws/src/vision_node/scripts
python3 patch_x500_camera.py
```

With no argument it searches the standard PX4-Autopilot layout under `$HOME`
and `/workspace`; pass the path explicitly if it can't find it:

```bash
python3 patch_x500_camera.py /path/to/PX4-Autopilot/Tools/simulation/gz/models/x500/model.sdf
```

Safe to re-run (checks for the sensor by name first) and backs up the
original as `model.sdf.orig` the first time. This inserts a camera sensor
pointed straight down (publishing to the Gazebo Transport topic
`drone_camera`), the standard PX4/Gazebo downward-camera mount convention.

If the bridged image later comes through black/empty with no errors, check
that the PX4 SITL world file loads the Sensors system plugin (PX4's default
worlds normally already do, since other PX4 vehicle models use cameras/depth
sensors too):

```xml
<plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
  <render_engine>ogre2</render_engine>
</plugin>
```

## 3. Bridge the camera into ROS 2

Once PX4 SITL + Gazebo are running with the patched model:

```bash
ros2 run ros_gz_bridge parameter_bridge \
  /drone_camera@sensor_msgs/msg/Image@gz.msgs.Image \
  /drone_camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo
```

## 4. Run the vision pipeline

In place of `relative_state_node` in your usual multi-terminal launch:

```bash
ros2 run vision_node aruco_landing_target_node
ros2 run vision_node vision_relative_state_node
```

Everything else (`px4_bridge`'s `uav_state_node`, `landing_controller`,
`moving_platform_node`, `q_learning.py`) stays exactly the same.

## 5. Verify the frame convention before trusting it

`aruco_landing_target_node.py` rotates the camera-frame marker pose into the
same world/NED-consistent `rel_x`/`rel_y`/`rel_z` convention the
ground-truth path already uses, via one fixed camera-mount assumption
(`CAMERA_TO_BODY` in that file) composed with the UAV's live attitude. This
has NOT been empirically verified against real sensor data yet -- do this
before trusting it for training or a demo:

1. Hover the UAV directly above the marker at a known height with
   ~zero roll/pitch/yaw.
2. Echo `/rl_observation` (or `/landing_target` directly) and confirm
   `rel_x`/`rel_y` are near 0 and `rel_z` is near the known height.
3. Translate/rotate the UAV and sanity-check the signs match what you'd
   expect (e.g. flying north should move `rel_x` in a consistent direction).

If X/Y come out swapped or sign-flipped, that's `CAMERA_TO_BODY` (or the
marker's assumed mounting orientation in the patched sensor `<pose>`)
needing a one-line fix -- not a bug in the attitude-rotation math itself.

## Target-lost handling

`vision_relative_state_node` always publishes `/rl_observation` once the
marker has been seen at least once -- it never goes silent -- but sets
`RLObservation.detected = false` while the marker is out of view, holding
the last known relative pose rather than snapping to (0,0,0).
`termination.py`'s watchdog (`simulation_parameters.target_lost_timeout`,
default 5s) ends the episode/flight as outcome `"target_lost"` once the loss
persists that long, the same watchdog pattern the reference
"Vision-based-UAV-autonomous-landing" repo uses (its `Main.py`: 10s of no
helipad detection before falling back). This is a no-op on the ground-truth
training path -- `relative_state_node` always sets `detected = true`.

## Known limitations

- **No filtering.** Relative velocity is raw finite-difference between
  consecutive detections -- noisier than the ground-truth path's analytic
  velocity. A Kalman/complementary filter would help if this turns out to
  matter for training stability; not attempted here to keep the first
  version simple.
- **`relative_yaw` is approximate and unvalidated** (see the docstring in
  `aruco_landing_target_node.py`) -- not currently consumed by the RL
  pipeline's 1D observation set anyway (`config/parameters.py`'s
  `observation_msg_strings` only uses `rel_x`/`rel_vx`).
- **Monocular scale relies on `MARKER_SIZE_M` being accurate.** If you
  change the marker's physical size (in `model.sdf` or on a real printed
  marker), update `MARKER_SIZE_M` in `aruco_landing_target_node.py` to
  match, or every distance estimate scales off proportionally.
