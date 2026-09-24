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
logic, `ros_io.py` = ROS wrapper + preflight, `vision_landing_main.py` = the entry point).

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

**Live camera view** (any time the camera bridge is up):
```bash
ros2 run rqt_image_view rqt_image_view /drone_camera                  # raw feed
ros2 run rqt_image_view rqt_image_view /landing_target/debug_image    # detection drawn on it + rel N/E/D
```
The debug image is only produced while something is subscribed to it. If `rqt_image_view` can't open a
window, use Gazebo's own GUI instead (top-right menu -> *Image Display* -> topic `drone_camera`).

**Camera intrinsics.** `aruco_landing_target_node` needs the camera's intrinsics and waits for
`/drone_camera/camera_info`. If none arrives within 2 s of the first image it logs a WARNING and uses
the ideal pinhole model for the SDF's 80 degree FOV (Gazebo's cameras are ideal pinholes, so this is
what `camera_info` would say). This exists because the node used to wait silently: the ROS topic
`/drone_camera/camera_info` stayed empty even though `gz topic -l` lists it, so nothing was
ever detected and nothing said why (cause not established -- if the fallback warning appears for you,
the bridge is not delivering `camera_info`; the fallback is exact for Gazebo's ideal cameras, so
detection still works). The vision mission's preflight also refuses to
arm unless `/landing_target` is actually producing messages.

Then, from `/workspace/uav_rl_landing`, one script:
```bash
python3 -m mission.vision_landing_main
```
It takes off to 5 m and flies the corners of a square, A -> B -> C -> D (default `0,0  0,9  9,9  9,0`,
PX4 local NED north,east metres from the spawn point), hovering 2 s at each. **The moment the marker is
confirmed -- mid-leg or at a corner -- the patrol stops** and the drone centres over it, descends and
lands. It prints progress every 5 s while flying a leg, so a long leg doesn't look like a hang.

```bash
python3 -m mission.vision_landing_main --corners 0,0 0,9 9,9 9,0 --altitude 5   # your own square / altitude
python3 -m mission.vision_landing_main --no-ground-truth   # platform moved without updating parameters.py
```
The camera only "sees" the marker within ~2 m east-west and ~3 m north-south of the flight path at 5 m
(the UAV's own rotor arms and props block the outer ~130 px on each side of the 640 px image), so pick
corners whose edges pass close enough to where the platform might be. The default square is placed so its
B -> C leg passes the sim platform at north 3, east 10.

**Built-in camera check (replaces the old separate frame-check script).** In the sim the configured
platform location (`platform_world_x/y` in `parameters.py`) is used only as ground truth, never to
steer. When the marker is first confirmed the mission prints the measured relative position, the
estimated marker position, and how far that is from the ground truth. If it is more than 1 m off it
prints a `MISMATCH` line -- with a swapped/flipped-axis hint when the pattern is recognisable -- and
**lands where it is instead of following the estimate** (a wrong sign would otherwise fly the drone
away from the marker). Either fix `CAMERA_TO_BODY`, or, if you moved the platform on purpose, update
`parameters.py` or pass `--no-ground-truth`.

The preflight refuses to arm if the camera bridge, `/uav/state` or `/landing_target` are missing, if
more than one node publishes `/landing_target`, or if the aruco node is silent.

Mission states: **PATROL** (square corners as above; marker must be confirmed in 3 detections within
1 s) -> **TRACK** (centre on the marker at up to 1.5 m/s, descend at 0.35 m/s only while within 0.25 m
of centre, pause above 0.5 m; below 1 m the marker leaves the camera's field of view, so it keeps
descending on the last estimate) -> **LAND** (PX4 `AUTO.LAND` from 0.5 m). If the marker is lost for 5 s
above 1 m it climbs back to 5 m over the last known spot (**RECOVER**); if it still can't see it, it
restarts the patrol. If the square finishes without a sighting, or the 300 s mission timeout hits, it
lands where it is. Tunables: the `VisionLandingConfig` dataclass in `vision_landing.py`.

The mission's search/track/recover logic is also exercised offline against a fake drone + camera
(footprint geometry, noise, no detection below 0.7 m, dropouts); that does not replace the
simulator run, it only means the state machine itself is sound.

## Phase 3 quick path: landing on a moving platform (straight-line motion)

Same idea as Phase 2, but the platform moves. Once the marker is confirmed the drone **locks on**: it
estimates the marker's velocity (least-squares fit over the last ~1.2 s of absolute marker positions; a
change-point check reacts to a reversal in ~0.6 s), flies in velocity mode at `v_platform + Kp * position error`
(the feed-forward is what makes it move *with* the platform), descends only while aligned in both position and
velocity, keeps going on a constant-velocity prediction once the marker leaves the camera's view below ~1 m,
and keeps matching the platform's velocity all the way to **contact** (vertical speed drops to ~0 while still
commanding descent) before handing over to `AUTO.LAND` only to disarm. (An `AUTO.LAND` hand-off at 0.3 m left the
UAV stopped in the air for ~1 s while the platform slid on: 0.25 m of drift at 0.4 m/s but ~0.6 m at 1 m/s, against a
0.75 m half-width. Contact under velocity matching: ~0.05-0.1 m at 0.4-1.0 m/s in the offline tests.) Code: `workspace/uav_rl_landing/mission/` (`target_tracker.py`,
`moving_landing.py`, `moving_landing_main.py`).

**Status: verified in real PX4 SITL + Gazebo Harmonic (4/4 landings, 0.02-0.08 m touchdown accuracy)**, plus
offline against a fake drone/camera/platform (`python3 -m tests.test_missions` from `workspace/uav_rl_landing`,
no ROS needed). Getting a real landing took several rounds of real-Gazebo debugging that the offline tests alone
did not catch, each now covered by a test or a runtime check: a camera-latency bug that stalled the lock for
~90 s (below); a Gazebo/ODE physics crash unrelated to this code (raised `rotorVelocitySlowdownSim` and reduced
host load fixed it); a platform escaping the patrol's one-shot search at any speed given real (not assumed)
takeoff timing (fixed by anchoring its motion to a patrol leg, below); and a real-time-factor mismatch that made
several accurate landings look like misses (the mission now flags its own ground-truth comparison as unreliable
when this happens, rather than reporting a false miss).

**Camera latency (important).** The camera's measurement of the marker is old by the time it arrives (Gazebo
render + bridge + DDS + node + callbacks, ~0.35-0.5 s in Gazebo). The marker's world position is built as
*UAV position + measurement*, so it must use the UAV position **from when the image was taken**; using the
current one leaves a term `latency x UAV velocity` in the estimate, which looks like platform motion whenever the
drone accelerates. The drone then commands that "velocity", accelerates more, and the lock never settles -- exactly
what the first Gazebo run showed (velocity estimates of +-2 m/s for a 0.4 m/s platform, no lock for 90 s). The mission
now compensates with `io.camera_latency` (default 0.35 s), rate-limits its velocity command (1 m/s^2) so a slightly
wrong value cannot destabilise it, and gives up a lock attempt after 25 s. Measure your latency once (static
marker, the Phase 2 setup, platform node **not** running):
```bash
cd /workspace/uav_rl_landing && python3 -m mission.measure_camera_latency
python3 -m mission.moving_landing_main --start-platform --camera-latency 0.37     # use what it prints
```

**Simulation speed.** PX4 SITL with a rendered camera often runs below real time (real-time factor < 1). The
Gazebo platform is commanded in metres per *simulation* second, but the platform node's ground-truth trajectory
used *wall* time, so the two drift apart -- at RTF 0.9 and 0.4 m/s that is 4.8 m after two minutes, which is why the
first Gazebo run reported "touched down 4.77 m from the platform centre" while it had actually followed the real
platform (the camera-derived tracker measured 0.33-0.36 m/s, not 0.4). Check the RTF in the Gazebo GUI's bottom bar.
If it is below ~0.98, run the platform node on sim time:
```bash
ros2 run ros_gz_bridge parameter_bridge /clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock     # own terminal
ros2 topic echo /clock --once                                                            # must print a time
ros2 run moving_platform moving_platform_node --ros-args -p use_sim_time:=true -p motion:=linear ...   # add to the usual args
```
(Only enable `use_sim_time` while `/clock` is publishing, otherwise the node's timers never fire.)

Setup differs from Phase 2 in one way: the platform node **does** run (it moves the platform), started with
`wait_for_start:=true`. Each in its own terminal, sourced as usual, after rebuilding
`colcon build --packages-select moving_platform` and re-sourcing:
```bash
ros2 run ros_gz_sim create -world default -file $(ros2 pkg prefix moving_platform)/share/moving_platform/models/moving_platform/model.sdf -name moving_platform -x 10.0 -y 0.0 -z 0.025
ros2 run ros_gz_bridge parameter_bridge /model/moving_platform/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist
ros2 run moving_platform moving_platform_node --ros-args -p motion:=linear -p start_x:=10.0 -p start_y:=0.0 -p heading_deg:=90.0 -p speed:=0.4 -p wait_for_start:=true
ros2 run ros_gz_bridge parameter_bridge /drone_camera@sensor_msgs/msg/Image@gz.msgs.Image /drone_camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo
ros2 run px4_bridge uav_state_node
ros2 run landing_controller landing_controller_node
ros2 run vision_node aruco_landing_target_node

cd /workspace/uav_rl_landing && python3 -m mission.moving_landing_main --start-platform
```
(`--start-platform` sends the start signal once the drone is airborne at the search altitude.) The preflight refuses
to arm unless exactly one node publishes `/platform/state` -- kill any stale `moving_platform_node` first.
**Important: a one-way platform trajectory is fragile here, AT ANY SPEED -- use a platform ANCHORED to a patrol
leg instead.** The patrol only searches its fixed square once (it does not loop), and the delay before the
platform even starts moving is not exactly predictable in the real world (arming, PX4's own takeoff time --
seen as ~9 s in Gazebo vs ~2 s assumed by an earlier version of this mission's own offline tests -- discovery,
scheduler jitter). A platform travelling one-way from a fixed start point has, by the time the drone gets
there, gone however far that unpredictable delay let it go -- which is exactly what happened on a real run: a
platform started 8 m behind the square at 1.0 m/s was found and caught in the offline tests (fast, ~2 s
takeoff assumed), but in Gazebo (~9 s takeoff) it had already driven straight through and out the far side
before the patrol ever got there.

The fix that is actually robust to this, not just re-tuned around one timing: **anchor the platform's motion
to a patrol leg's own coordinate**, so it can never end up somewhere the patrol doesn't look, independent of
timing. Back-and-forth motion (`travel_length`) along a line that matches a leg's fixed coordinate (e.g. the
B->C leg is `east = 9`) keeps the platform within the camera's reach of that leg for its entire run:

**Use sim time -- do this by default, not only if you notice a problem.** Every real run so far on this
project's dev machine has shown a real-time factor well under 1 (28-91%), and `moving_platform_node`
defaults to WALL-clock time: at RTF 45%, one wall-clock second only advances the simulation 0.45 s, so the
node's own `/platform/state` position report -- computed from wall time -- runs consistently AHEAD of where
the physical Gazebo model actually is, always in the direction of travel. This showed up in two real runs as
a ~1.2-1.6 m "MISSED the platform" verdict in the SAME direction both times, despite the mission's own
`Contact at ... m from the predicted platform position` line (measured against what the camera actually saw,
immune to this) reading 0.06 m and 0.02 m -- i.e. the landings were accurate; only the ground-truth
COMPARISON used to grade them was wrong. Bridge `/clock` and pass `use_sim_time:=true` so the two stay in
sync:
```bash
ros2 run ros_gz_bridge parameter_bridge /clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock
ros2 topic echo /clock --once        # must print a time before the node below will actually use it
ros2 run ros_gz_sim create -world default -file $(ros2 pkg prefix moving_platform)/share/moving_platform/models/moving_platform/model.sdf -name moving_platform -x 9.0 -y 1.5 -z 0.025
ros2 run moving_platform moving_platform_node --ros-args -p use_sim_time:=true -p motion:=linear -p start_x:=9.0 -p start_y:=1.5 -p heading_deg:=90.0 -p speed:=0.30 -p travel_length:=6.0 -p wait_for_start:=true
python3 -m mission.moving_landing_main --start-platform
```
This moves the platform back and forth along `east = 9` (matching the B->C leg exactly) between `north = 1.5`
and `north = 7.5` -- a 12 m round trip, clearly visible motion, and landed on in the offline jitter sweep (a
range of simulated start-up delays) 16/16 times (`tests/test_missions.py`'s `run_moving_jitter`). The same
pattern anchored to the A->B leg instead (`north = 0` fixed, east-west motion) landed 14/16. Faster anchored
motion was tried and found LESS reliable, not more (0.5 m/s dropped to 13/20, 0.6 m/s and above failed
entirely -- the lock-on control loop has its own speed limit) -- 0.3 m/s is the validated speed, not just a
cautious default.

If the mission still prints `NOTE: ... the simulation runs at ~NN% of real time`, `use_sim_time` did not
take (check `/clock` is actually publishing before the node starts -- a node that starts before the bridge
is up silently keeps using wall time) and the final "offset from platform centre" is still unreliable; the
touchdown itself, against the live camera, is unaffected either way.

A one-way or faster platform is still possible to catch at exactly one timing (an un-anchored, un-swept
single run in the offline tests lands, e.g., 0.8 or 1.0 m/s starting 16 m behind the square) -- but that
specific distance was fit to this fake world's particular delay and is not a recipe to copy into a real run;
treat any one-way configuration as informational only, not something to expect to work reliably.

Known limits (measured in the offline tests, with takeoff timing corrected to match the real ~9 s Gazebo
climb; a non-reversing platform is the case actually verified in Gazebo -- see Status above): below ~1 m the
marker leaves the camera's field of view (0.5 m
marker, 80 deg FOV, rotor arms blocking the image edges), so the last ~2 s of descent to contact are blind. A
platform that reverses direction *during that window* is missed by 1 m or more; with a 10 s half-period about
1 in 5 reversal phases miss in the fake world under the corrected timing (4/20 land -- worse than the 15/20
measured before the timing fix, because the now-longer overall mission overlaps a reversal near touchdown
more often). This is the price of touching down under velocity matching, which is far more accurate on a
steadily moving platform than an `AUTO.LAND` hand-off. A smaller nested marker inside the current one, visible
closer to the ground, is the intended fix for both the blind-window and the anchored-motion speed limit.

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
