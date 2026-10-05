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

### Real-Gazebo follow-up: reaching the 5 km/h hardware target on LINEAR motion

The real-hardware target (landing on a moving car's roof) needs a minimum of **5 km/h = 1.39 m/s**, well
above the 0.3 m/s validated above. The same `--fast` higher-bandwidth gain profile built for Phase 3b's
circular motion (see below) was pushed onto this straight-line platform too, via
`mission/circular_landing_main.py --no-curvature` (that script is motion-agnostic despite its name --
`moving_landing_main.py` has no `--fast` flag).

A real Gazebo run exposed a failure mode offline phase-sweep testing had hidden: `linear_state`'s
back-and-forth motion reverses velocity *instantly* at each end of travel (unlike circular motion, which
turns continuously and never has a discrete reversal event). If that reversal lands near the final blind
descent or the moment of contact, the control loop is working off a stale pre-reversal estimate for a
moment. An instrumented offline trace showed tracking error oscillating between near-zero (right as a
reversal is detected) and 3-5 m (moments later, chasing the wrong way) every half-period -- at a short
back-and-forth distance (6-10 m, reversing every 8.6-14.4 s) this starved the mission of any sustained
"locked long enough to descend" window before `mission_timeout`.

**Fix: lengthen the back-and-forth leg so reversals are rare relative to how long a lock-to-touchdown
sequence actually takes (~70-90 s observed once locked).** `travel_length=50` (reversing every ~72 s) was
offline-validated 10/10 at 1.39 m/s with the real measured 0.09 s latency, and **confirmed in real PX4 SITL
+ Gazebo Harmonic: 3/3 landed** by the trustworthy metric (`Contact at ... m from the predicted platform
position`: 0.09, 0.49, 0.04 m -- all well under the 0.75 m half-width). The one 0.49 m run coincided with a
reversal landing ~4 s before its touchdown phase -- the kind of occasional degraded-but-still-in-tolerance
case the offline sweep's 8-10/10 (not a clean 10/10) rate already predicted, not a new problem.

A subtlety worth recording: not every "long enough" travel_length is safe. `travel_length=30` and `=40`
both happened to put a reversal almost exactly at the same elapsed time as touchdown in this specific
setup (4x30 == 3x40 == 120, the same total distance at 1.39 m/s) -- a coincidence of this particular
geometry/timing, not a general rule, but a reminder to check the arithmetic rather than assume bigger is
automatically fine.

**True one-way (non-reversing) motion does not work with this project's patrol design, at any distance.**
Tested offline with the patrol box widened all the way to 100 m -- still 0/10, every run ending `NOT_FOUND`.
The patrol's `search_speed` (1.5 m/s) is only 0.11 m/s faster than a 1.39 m/s platform; once the platform
has any head start (and it always does -- it starts moving the instant the drone is airborne, before patrol
even reaches the relevant leg), the drone can never close the gap by flying toward a fixed corner. A
bounded, rarely-reversing leg is what actually works, not a literal one-way track.

The patrol box must be widened to match (`--corners`, north extent >= `travel_length + 2`) -- a platform
that travels further than the default 9 m square simply exits the patrol's reach, producing a spurious
`NOT_FOUND` unrelated to the control loop.

```bash
ros2 run ros_gz_sim create -world default -file $(ros2 pkg prefix moving_platform)/share/moving_platform/models/moving_platform/model.sdf -name moving_platform -x 10.0 -y 0.0 -z 0.025
ros2 run ros_gz_bridge parameter_bridge /model/moving_platform/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist
ros2 run moving_platform moving_platform_node --ros-args -p motion:=linear -p start_x:=10.0 -p start_y:=0.0 -p heading_deg:=90.0 -p speed:=1.39 -p travel_length:=50.0 -p wait_for_start:=true

cd /workspace/uav_rl_landing && python3 -m mission.circular_landing_main --start-platform --no-curvature --fast --camera-latency 0.09 --corners 0,0 0,9 52,9 52,0
```
(`--camera-latency 0.09` was this project's own measured value on this machine -- measure yours, do not
reuse this number blindly.) Full detail: `circular_landing_main.py`'s own docstring.

**A second real-Gazebo finding: run `moving_platform_node` on sim time, not wall time, at this
speed.** A real run showed the platform's reported velocity flipping sign every 5-10 s during an
otherwise-locked descent (far more often than a real reversal, which only happens every ~36 s at
`travel_length=50`) and stalling at one altitude for over two minutes as a result -- yet an offline
replay at the same noise level (0.2 m) landed clean in 15/15 tries, no stall. That mismatch points at
something the offline model can't capture: `moving_platform_node` defaults to *wall*-clock time, so a
momentary dip in Gazebo's real-time factor (host load, rendering) makes the physically-rendered
platform motion and the wall-clock-driven trajectory the node assumes drift apart *during that dip*,
which the camera sees as erratic platform velocity. The RTF NOTE already printed at touchdown in
every run this session (58-149% observed) is the same phenomenon measured end-to-end; this is just
its effect showing up mid-mission instead. Fix: bridge `/clock` and pass `-p use_sim_time:=true` to
`moving_platform_node` (same recipe as the simulation-speed section above, just not yet applied to any
of the 5 km/h runs before this) -- the mission still landed accurately in every run that stalled
(0.08, 0.06, 0.10 m from the predicted platform position), so this is a timing/smoothness issue, not
a correctness one, but it is the recommended default going forward, not an optional fix.

## Phase 3b quick path: landing on a moving platform (circular motion)

Same mission as Phase 3 above, on a platform moving on a **circle** instead of a straight line. The control
loop itself (`MovingPlatformLander._track`/`_recover`) needed no changes for this -- it only ever consumes
`TargetTracker.state()`'s position/velocity estimate and was never actually aware of the platform's motion
shape. The one real gap: `target_tracker.py`'s extrapolation used while the marker is out of view (the blind
final ~1 m of descent, or a camera dropout) fit a straight line to recent samples, which lags behind a curving
platform. Fixed with an opt-in constant-turn-rate (CTRV) extrapolation -- it tracks how fast the fitted
velocity vector's *heading* is rotating and extrapolates along that arc instead of a tangent line, reducing
to the exact same straight-line prediction as turn rate -> 0. Off by default (`MovingLandingConfig
.tracker_curvature = False`), so Phase 3's hardware-validated straight-line runs are unaffected byte-for-byte;
turned on by the new entry point below. Code: `workspace/uav_rl_landing/mission/target_tracker.py`,
`moving_landing.py` (one new config field), `circular_landing_main.py`.

**Status: offline-tested only** (`python3 -m tests.test_missions` from `workspace/uav_rl_landing`, no ROS
needed) -- **not yet run in real PX4 SITL + Gazebo Harmonic**, unlike Phase 3's straight-line motion above.
Treat this as implemented-and-simulated, not hardware-verified, until it has been.

**Does the platform stay in the camera's window?** Checked two ways, not just assumed:
- **Patrol (finding it):** the camera's usable footprint at the 5 m search altitude is `~2.25 m` east-west /
  `~2.9 m` north-south of the drone (`0.50 * alt - 0.25` / `0.63 * alt - 0.25`, the same formula behind the
  Phase 2 "~5 m x ~6.3 m usable footprint" note above). The demo circle below (`radius=1.5 m`, centred close
  to the default patrol's B->C leg at `east=9`) keeps the *entire* circle within that range continuously --
  worst-case east-west offset from the leg is `|9.5-9| + 1.5 = 2.0 m`, inside the `2.25 m` tolerance with
  margin -- so unlike the anchored-linear case, first sighting does not depend on timing luck.
- **Tracking (once locked):** the offline tests assert directly on this, not just on whether the mission
  landed -- once `LOCKED`, the platform stays inside the camera's visible range ~100% of the time above the
  blind-descent floor (`servo_min_altitude`), and no invisible streak there exceeds `lost_timeout` (see
  `tests/test_missions.py::test_circular`'s footprint-containment checks, which read the same visibility
  formula straight out of `tests/fake_world.py`'s camera model).

**Offline test results** (`test_circular()`): the demo circle (`radius=1.5 m`, `angular_speed=0.3 rad/s`,
`0.45 m/s` tangential -- comparable to the validated `0.3-0.4 m/s` linear speeds) lands 16/16 across a full
revolution of arrival-phase jitter. What actually stresses the curvature fix is **turn rate, not
translational speed** -- pushing the platform faster mostly just hits the same `~0.4-0.5 m/s` control-loop
speed ceiling documented for linear motion above, regardless of tracker. Holding speed at the validated
`~0.4 m/s` but tightening the radius (`radius=1.0 m`, `angular_speed=0.4 rad/s` -- a faster-rotating heading
at the same speed) makes the gap explicit: **0/12 landed with the plain straight-line tracker, 12/12 with the
curvature-aware one**, across the same phase sweep. An 8 s mid-descent dropout on the demo circle also shows
the difference directly (touchdown offset `0.91 m` without curvature vs `0.43 m` with it, both technically
"landed" but the curvature-aware one closer to the platform centre).

Setup: identical to Phase 3 above, except the platform node is started with `motion:=circular` and a centre
instead of a start point/heading (node defaults are left untouched -- this passes explicit overrides, exactly
like Phase 3 overrides `motion:=linear` on a node whose own default motion is circular):
```bash
ros2 run ros_gz_sim create -world default -file $(ros2 pkg prefix moving_platform)/share/moving_platform/models/moving_platform/model.sdf -name moving_platform -x 11.0 -y 3.0 -z 0.025
ros2 run ros_gz_bridge parameter_bridge /model/moving_platform/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist
ros2 run moving_platform moving_platform_node --ros-args -p motion:=circular -p center_x:=9.5 -p center_y:=3.0 -p radius:=1.5 -p angular_speed:=0.3 -p wait_for_start:=true
ros2 run ros_gz_bridge parameter_bridge /drone_camera@sensor_msgs/msg/Image@gz.msgs.Image /drone_camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo
ros2 run px4_bridge uav_state_node
ros2 run landing_controller landing_controller_node
ros2 run vision_node aruco_landing_target_node

cd /workspace/uav_rl_landing && python3 -m mission.circular_landing_main --start-platform
```
(spawn `-x/-y` = `center_x + radius, center_y` -- the circle's own `t=0` position, same spawn rule as any other
motion.) Pass `--no-curvature` to compare against the plain straight-line extrapolation on the same circular
platform. The same camera-latency and simulation-speed (`use_sim_time`) notes from Phase 3 above apply
unchanged -- neither is specific to the platform's motion shape.

### Real-Gazebo follow-up: a curvature-detector bug, and reaching the 5 km/h hardware target

The first real PX4 SITL + Gazebo Harmonic run of Phase 3b landed correctly on the demo circle
(0.45 m/s), but pushed to `radius=2.0, angular_speed=0.6` (1.2 m/s) the drone locked on and then
never converged, cycling LOCK -> lost -> RECOVER indefinitely. Traced with the offline harness, not
guessed: `_drop_old_motion_if_changed()` (the reversal detector in `target_tracker.py`, tuned only
for straight-line motion) was firing on ordinary curvature at this turn rate -- any short-vs-long
velocity-vector *magnitude* disagreement above `change_threshold` counted as a "change", and
ordinary curvature produces exactly that at a high enough turn rate, indistinguishable by magnitude
alone from a genuine reversal. Confirmed directly: 0 false triggers over 6.7 s on the demo circle,
6 on the failing one. **Fixed**: the detector now also requires the short-vs-long *heading* to have
flipped by more than 100 degrees (a real reversal) rather than just drifted (ordinary curvature) --
existing reversal-detection tests (tuned for the straight-line case, where a real reversal is a
~180 degree flip) still pass unchanged.

That fix alone does not make `radius=2.0, angular_speed=0.6` (1.2 m/s) land, though -- offline,
still 0/10, still TIMEOUT. Isolated why with a `TargetTracker.state()` monkeypatch that returns the
exact ground truth (removes tracking accuracy as a variable entirely): the **control law itself**
is the bottleneck, not the tracker -- 10/10 at 0.8 m/s, 0/10 (never converges) at 1.0 m/s and
above, regardless of motion shape, even with a perfect estimate. This matters because the intended
real-hardware demo (landing on a moving car's roof) needs a minimum of **5 km/h = 1.39 m/s** --
well past this ceiling.

Gain tuning alone closes it. A second, higher-bandwidth profile (`--fast` on
`circular_landing_main.py`): `kp=3.0` (was 1.0), `max_accel=5.0` (was 1.0), `max_speed=4.0` (was
2.5), `tracker_window=0.6` (was 1.2, shortened so the velocity fit stays locally valid over a
smaller arc at a fast turn rate). Offline, with the real (noisy, latency-affected) tracker: **10/10
landings at 1.39 m/s, error 0.17-0.21 m** -- and no regression at the demo circle (8/8, actually
tighter: 0.04-0.05 m vs 0.06-0.09 m with the original gains).

**The real cost.** `max_accel=1.0` was deliberately conservative -- see its comment in
`moving_landing.py` -- specifically to bound how much a slightly-wrong camera-latency estimate can
destabilise the lock. `--fast` trades most of that margin away.

```bash
python3 -m mission.circular_landing_main --start-platform --fast
```
(needs a faster/tighter circle to actually demand it, e.g. `-p radius:=2.0 -p angular_speed:=0.695`
on `moving_platform_node` for the 5 km/h target -- the demo circle's 0.45 m/s doesn't need `--fast`
at all.)

**Second real-Gazebo round.** The change-detector fix + first `--fast` cut above were then actually
run in Gazebo: `radius=2.0, angular_speed=0.6` (1.2 m/s, the original failing config) landed
correctly once the change-detector fix and `--fast` were both applied together, confirming the
offline prediction exactly. `0.8` and `1.0` m/s (measured real camera latency: 0.09 s, via
`measure_camera_latency.py`) also landed cleanly -- 0.06 m and 0.18 m from the predicted platform
position. But **5 km/h itself did not land**: it locked on, briefly started descending, then
oscillated in and out of "aligned" for the entire `mission_timeout` without settling, eventually
timing out.

Reproduced offline by raising detection noise to ~0.2 m (a fast-moving marker's plausible real
motion-blur/detection noise, vs the 0.04 m default) -- at 1.39 m/s this drops the first `--fast` cut
to 2/10 (TIMEOUT), matching the real symptom exactly. Root cause: `align_speed_tol` (0.3 m/s) and
`realign_tol` (0.5 m) -- the hysteresis around "aligned enough to descend" -- were tuned for the
original, less noisy regime and were too tight for this one, so the mission kept flipping between
"aligned, start descending" and "loose, stop descending" instead of settling. **Fixed**: loosened
to `align_speed_tol=0.6, realign_tol=0.8` as part of `--fast`. Offline: recovers 10/10 at every
speed from 0.45 to 1.39 m/s, under both normal and this noise stress, with no regression at the
lower speeds.

**A second, separate limit surfaced doing this properly**: what matters isn't just an
accurately-*calibrated* latency, but a *low absolute* latency. At 5 km/h under noise stress, a
0.4 s camera latency -- even **perfectly** compensated, zero calibration error -- still fails
(1/10, still TIMEOUT); a low latency (0.09-0.2 s tested) is fine (9-10/10) regardless of a small
calibration gap on top. 0.4 s of pure delay at 1.39 m/s alone means the tracker is always working
from where the platform was 0.56 m ago -- no calibration accuracy removes that. This session's own
measured latency (0.09 s) is comfortably in the safe range, but a slower real camera/compute
pipeline on different hardware would not be, independent of how well it's calibrated.

**Third real-Gazebo round -- a flight-safety bug, not a landing-accuracy one: the drone crashed.**
Retesting 5 km/h with the hysteresis fix above, the drone crashed mid-`LOCK` -- confirmed
`TELEMETRY_STALLED` (PX4/Gazebo stopped responding) right after the mission logged a platform
velocity **estimate of ~3 m/s, for a platform whose true max speed is 1.39 m/s.** Traced to a real
bug, not a tuning gap: `TargetTracker` was constructed with `c.max_speed` directly -- the *same*
field as the UAV's own flight-speed authority. `--fast` raises that to 4.0 m/s so the UAV has spare
speed to catch up, but this also raised the ceiling on what a noisy/bad camera fit is allowed to
*report* as "the platform's velocity," and the control loop trusts that estimate directly as
feedforward (`cmd = state.vx + kp*error`). A real PX4-controlled vehicle commanded to chase a
implausible, rapidly-changing ~3-4 m/s setpoint based on garbage data is a flight-safety problem,
not just a bad landing -- and this project's offline `FakeWorld` (a simplified first-order-lag
drone model) has no way to catch that: it can tell you whether the *mission logic* converges, not
whether a *real flight controller* can safely track whatever it's commanded.

Confirmed the mechanism offline by instrumenting `TargetTracker.state()` to record its peak
reported speed under harsh noise (0.5 m, 10 seeds): the old coupled clip let a bad fit reach
3.3-4.0 m/s; a mathematically identical run with the fix below never exceeded 2.5 m/s once,
regardless of noise. **Fixed**: a new `tracker_max_speed` field (default 2.5) now clips what the
tracker may report, independent of `max_speed` (the UAV's own limit) -- kept near the platform's
*actual* expected speed with headroom for noise, not the UAV's flight authority. `--fast` now sets
`tracker_max_speed=2.5` explicitly. No regression: still 10/10 at 5 km/h offline, under both normal
and noise-stress conditions.

**Status: 0.8 and 1.0 m/s are real-Gazebo-verified** (change-detector fix + original `--fast`,
0.06 m and 0.18 m accuracy). **5 km/h itself remains offline-tested only** -- the hysteresis fix and
this `tracker_max_speed` safety fix have not yet been retried in real Gazebo. Given the last attempt
crashed the vehicle, retest cautiously: confirm the environment/host is stable first (see the
`rotorVelocitySlowdownSim`/host-load note earlier in this project's own linear Phase 3 history for
an unrelated but similarly-presenting Gazebo/ODE physics crash), and watch the tracker's logged
`platform (...)` velocity numbers during the run -- they should now never exceed ~2.5 m/s for this
platform; if one does, that's a sign something is still wrong, not noise.

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
