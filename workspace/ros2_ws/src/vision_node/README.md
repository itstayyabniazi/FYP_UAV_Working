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

## Phase 2 quick path: camera-guided landing on a static platform

The drone is **not told where the platform is**: it takes off, searches with the camera, and lands
on the ArUco marker it finds. This is a scripted mission (like Phase 1's `takeoff_and_land.py`), not
the RL agent -- at epsilon=1.0 the RL agent just flies randomly, so don't use `agent.q_learning` to
test perception. Code: `workspace/uav_rl_landing/mission/` (`vision_landing.py` = search/track/land
logic, `ros_io.py` = ROS wrapper + preflight, `vision_landing_main.py`, `vision_frame_check.py`).

Needs: PX4 SITL + Micro-XRCE-DDS Agent + GCS heartbeat (as always), the platform spawned and left
still (do NOT run `moving_platform_node` -- nothing here needs it, and a stale one caused a wrong
landing in Phase 1), the x500 camera patch (section 2 below, done once), and these nodes, each in its
own terminal with `source /opt/ros/humble/setup.bash && source /workspace/ros2_ws/install/setup.bash`:

```bash
# platform, anywhere you like (the drone does not know this); keep parameters.py's
# platform_world_x/y equal to it so the final "error to ground truth" line is meaningful
ros2 run ros_gz_sim create -world default -file $(ros2 pkg prefix moving_platform)/share/moving_platform/models/moving_platform/model.sdf -name moving_platform -x 10.0 -y 3.0 -z 0.025

ros2 run ros_gz_bridge parameter_bridge /drone_camera@sensor_msgs/msg/Image@gz.msgs.Image /drone_camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo
ros2 run px4_bridge uav_state_node
ros2 run landing_controller landing_controller_node
ros2 run vision_node aruco_landing_target_node
```
Not needed for this mission: `vision_relative_state_node`, `relative_state_node`,
`moving_platform_node`, the cmd_vel bridge.

Then, from `/workspace/uav_rl_landing`:
```bash
python3 -m mission.vision_frame_check     # once: proves the camera axes/signs are right
python3 -m mission.vision_landing_main    # the mission
```
`vision_frame_check` flies to three known points around the platform (above it, 2 m south of it,
2 m west of it) and compares `/landing_target` with the expected offsets, printing a swapped/flipped-
axis hint on failure. Run it first: a sign error makes the visual-servo loop fly *away* from the
marker.

Both scripts refuse to arm if the camera bridge, `/uav/state` or `/landing_target` are missing, or if
more than one node publishes `/landing_target`.

Mission states: **SEARCH** (expanding-square spiral at 5 m, ~8.4x6.3 m camera footprint, 5 m legs, up
to 30 m out; the marker must be confirmed in 3 detections within 1 s) -> **TRACK** (centre on the
marker at up to 1.5 m/s, descend at 0.35 m/s only while within 0.25 m of centre, pause above 0.5 m;
below 1 m the marker leaves the camera's field of view, so it keeps descending on the last estimate)
-> **LAND** (PX4 `AUTO.LAND` from 0.5 m). If the marker is lost for 5 s above 1 m it climbs to 5 m over
the last known spot (**RECOVER**); if it still can't see it, it restarts the search. If the whole
spiral finds nothing, or the 300 s mission timeout hits, it lands where it is. Tunables are the
`VisionLandingConfig` dataclass in `vision_landing.py`.

The mission's search/track/recover logic is also exercised offline against a fake drone + camera
(footprint geometry, noise, no detection below 0.7 m, dropouts); that does not replace the
simulator run, it only means the state machine itself is sound.

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
tree). Patch it directly. Note this patches `x500_base/model.sdf`, not
`x500/model.sdf` -- the latter is just a thin wrapper
(`<include merge='true'><uri>model://x500_base</uri></include>`) around the
former, which is where the actual airframe (`base_link` and everything else)
lives (confirmed against a real PX4 v1.14+ checkout):

```bash
cd /workspace/ros2_ws/src/vision_node/scripts
python3 patch_x500_camera.py
```

With no argument it searches the standard PX4-Autopilot layout under `$HOME`
and `/workspace`; pass the path explicitly if it can't find it:

```bash
python3 patch_x500_camera.py /path/to/PX4-Autopilot/Tools/simulation/gz/models/x500_base/model.sdf
```

Safe to re-run (checks for the sensor by name first) and backs up the
original as `model.sdf.orig` the first time. This inserts a camera sensor
pointed straight down (publishing to the Gazebo Transport topic
`drone_camera`), the standard PX4/Gazebo downward-camera mount convention.

If it can't find a `base_link` to attach to, it prints every link name it
actually found in the file -- re-run with `--link <name>` picking the one
that represents the vehicle's main body (PX4 versions have named this
differently across releases):

```bash
python3 patch_x500_camera.py --link <name from the error message>
```

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
