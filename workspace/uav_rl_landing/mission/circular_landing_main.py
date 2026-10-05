"""
Phase 3b: camera-guided landing on a MOVING platform (circular motion) -- one script.

Same mission as `moving_landing_main.py` (Phase 3, straight-line motion): takes off, patrols the
corners of a square at the search altitude, and the moment the ArUco marker is confirmed it stops,
LOCKS onto the platform (estimates its velocity and flies along with it), descends while aligned,
and lands on it. The drone is not told where the platform is or how fast it moves.

The only thing that changes for a platform moving on a circle instead of a straight line is the
prediction used while the marker is out of view (the blind final descent, or a camera dropout): a
plain constant-velocity extrapolation lags behind a curving platform, so `MovingLandingConfig`'s
`tracker_curvature` flag is turned on here (see `mission/target_tracker.py`'s module docstring for
the constant-turn-rate extrapolation this enables). The control loop itself
(`MovingPlatformLander._track()`) is unchanged and unaware of the platform's motion shape -- it
only ever consumes the tracker's position/velocity estimate.

Default platform: centred at Gazebo ENU (9.5, 3.0), radius 1.5 m, angular_speed 0.3 rad/s (so a
0.45 m/s tangential speed, comparable to the validated 0.3-0.4 m/s linear runs). Chosen so the
whole circle stays within camera detection range of the default patrol's B->C leg (PX4 local NED
`east=9`) with margin: worst-case cross-track offset from that leg is |9.5-9| + 1.5 = 2.0 m,
against a 2.25 m camera de-tolerance at the 5 m search altitude (`0.50 * altitude - 0.25`, see
`tests/fake_world.py`'s `_camera()` -- the same formula the real vision_node's ~80 deg FOV minus
rotor-arm occlusion approximates). The circle's north extent (1.5-4.5 m) sits well inside the
leg's 0-9 m sweep. Node defaults are left untouched (they are relied on elsewhere, e.g. the
uav_rl_landing RL spawn command) -- this mission passes explicit `-p` overrides instead, exactly
like the linear mission overrides `motion:=linear` on a node whose own default motion is circular.

Status: offline-tested only (`tests/test_missions.py::test_circular`), not yet run in real
PX4 SITL + Gazebo Harmonic -- unlike Phase 3's straight-line motion (4/4 real landings, see the
top-level README). Treat this as implemented-and-simulated, not hardware-verified.

--- --fast: a second, faster profile, for the real-hardware target (landing on a car roof, min.
    5 km/h = 1.39 m/s) -----------------------------------------------------------------------

The default gains above (kp=1.0, max_accel=1.0, max_speed=2.5, tracker_window=1.2, align_speed_tol
=0.3, realign_tol=0.5) are the same ones the linear Phase 3 was hardware-validated with, and they
have a hard, confirmed ceiling: with a PERFECT tracker (offline test, no noise/latency at all), the
control law itself never converges above ~0.8-1.0 m/s, on any motion shape -- this is not a
tracking-accuracy problem, it is the control law's own bandwidth. `--fast` switches to a profile
that raises it past 5 km/h: kp=3.0, max_accel=5.0, max_speed=4.0, tracker_window=0.6,
align_speed_tol=0.6, realign_tol=0.8 -- offline: 10/10 landings at every speed from 0.45 to
1.39 m/s (the last is the 5 km/h target: radius 2.0 m, angular_speed ~0.7 rad/s), 0.17-0.21 m
error, no regression at the default 0.45 m/s circle (actually slightly tighter: 0.04-0.05 m vs
0.06-0.09 m).

The last two (align_speed_tol, realign_tol -- the hysteresis around "aligned enough to descend")
were added after a real Gazebo run at 5 km/h with the first --fast cut (kp/max_accel/max_speed/
window only) locked on but never settled: tracking error oscillated between "aligned" and "loose"
for the entire mission_timeout without ever staying converged long enough to complete the descent.
Reproduced offline by raising detection noise to ~0.2 m (a fast-moving marker's plausible real
motion-blur/detection noise, vs the 0.04 m default) -- at 1.39 m/s this alone drops the original
--fast to 2/10 (TIMEOUT), matching the real symptom. Loosening the hysteresis (0.3->0.6 m/s,
0.5->0.8 m) recovers 10/10 at every speed, under both normal and this noise stress, and is also
meaningfully more tolerant of a small camera-latency calibration error (a real measurement, e.g.
from measure_camera_latency.py, is never exactly the true value).

Three remaining costs, all confirmed directly, not assumed:
- --fast still trades away most of the latency-robustness margin max_accel=1.0 was deliberately
  chosen for (see MovingLandingConfig's own comment on max_accel in moving_landing.py) -- a LARGE
  latency mismatch (~0.15 s or more) still fails outright, just no longer a small (~0.02-0.05 s)
  realistic measurement error on top of real-world noise.
- What matters is not just an accurately-CALIBRATED latency, but a LOW absolute latency to begin
  with. At 5 km/h, a 0.4 s camera latency -- PERFECTLY compensated, zero calibration error -- still
  fails under noise stress (confirmed: 1/10, still TIMEOUT). 0.4 s of pure delay at 1.39 m/s alone
  means the tracker is always working from where the platform was 0.56 m ago; no calibration
  accuracy fixes that. A low latency (this project's own measured values have ranged 0.09-0.5 s
  depending on the machine/render load) is comfortably fine (10/10 up to ~0.2 s tested); a slow
  camera pipeline is a real, separate limit `--fast` does not remove.
- A FLIGHT-SAFETY issue, found from an actual Gazebo crash: TargetTracker used to be constructed
  with max_speed directly -- the SAME field as the UAV's own flight-speed authority. --fast raises
  that to 4.0 m/s so the UAV has spare speed to catch up, but this also raised the ceiling on what
  a noisy/bad camera fit is allowed to report as "the platform's velocity" -- confirmed offline
  (harsh noise, 10 seeds): the old coupled clip let a bad fit report 3.3-4.0 m/s for a platform
  that never exceeds ~1.4-2 m/s, and a real PX4-controlled vehicle trusting that as feedforward
  crashed. **Fixed**: `tracker_max_speed` (default 2.5, independent of max_speed) now clips what
  the tracker is allowed to report, kept near the platform's real expected speed regardless of how
  much flight authority the UAV itself has -- confirmed to hold the estimate at exactly 2.5 m/s
  even under the same harsh noise that let the old code reach 4.0.

Measure your real camera's latency with `python3 -m mission.measure_camera_latency` and pass it via
--camera-latency before trusting --fast on real hardware; do not guess it, and do not assume a low
value carries over from one machine/setup to another. If your platform's real speed changes
meaningfully, update --fast's tracker_max_speed to match (comfortably above the real speed, well
below max_speed) rather than leaving it at this default. Also validate incrementally in real Gazebo
(e.g. 0.8 -> 1.0 -> 1.39 m/s) rather than jumping straight to 5 km/h -- circular motion's --fast has
not been run against real PX4 SITL + Gazebo at 5 km/h yet, only offline (0.8 and 1.0 m/s have, with
a 0.09 s measured latency, both landing accurately: 0.06 m and 0.18 m from the predicted platform
position respectively).

--- --fast on LINEAR (back-and-forth) motion -- real-Gazebo validated at 5 km/h, with one real gap
    found and fixed along the way -------------------------------------------------------------

This script is fully motion-agnostic, so it is also what was used to push the hardware-validated
linear Phase 3 (`moving_landing_main.py`'s straight-line platform, which lacks a --fast flag) up to
5 km/h: run with `--no-curvature` and the platform node's `motion:=linear`.

A real Gazebo run surfaced something the offline (phase-averaged) testing hid: `linear_state`'s
back-and-forth motion reverses velocity INSTANTLY at each end of its travel. If that reversal lands
near the final blind TOUCHDOWN phase or near the moment of contact, the control loop is working off
a stale pre-reversal estimate for a moment -- a qualitatively different failure than circular
motion's continuous curvature, which never has a discrete reversal event at all. Confirmed directly
(instrumented offline trace): tracking error oscillates between near-zero (right as a reversal is
detected) and 3-5 m (moments later, chasing the platform the wrong way), repeating every half-period
-- at short travel_length (6-10 m, period 8.6-14.4 s) this starves the mission of any sustained
"aligned enough to descend" window before mission_timeout.

Fix: lengthen travel_length so reversals are rare relative to how long a lock-to-touchdown sequence
actually takes (~70-90 s observed in real Gazebo once locked). travel_length=50 m (period ~72 s)
offline-validated 10/10 at 1.39 m/s with the real measured 0.09 s latency; confirmed in real
PX4 SITL + Gazebo Harmonic, 3/3 landed by the trustworthy metric (0.09, 0.49, 0.04 m from the
predicted platform position -- all well under the 0.75 m half-width; the one 0.49 m run coincided
with a reversal landing ~4 s before its touchdown phase, the kind of occasional degraded-but-still-
in-tolerance case the offline sweep's 8-10/10 (not 10/10) rate already predicted). NOT every
travel_length that "looks long enough" is safe: travel_length=30 m and =40 m both put a reversal
almost exactly at the same elapsed time as touchdown in this setup (4x30 == 3x40 == 120, the same
total distance at this speed/timing) -- a coincidence specific to this geometry, not a general rule,
but a reminder to check the arithmetic rather than assume "bigger is always fine."

The patrol box must be widened to match (`--corners`, north extent >= travel_length + 2): a
platform that travels further than the default 9 m square can simply exit the patrol's reach,
producing spurious NOT_FOUND unrelated to the control loop. True one-way (non-reversing,
travel_length=0) motion was tried and does NOT work with this patrol design at any length tested
(confirmed offline up to a 100 m patrol box, still 0/10): the patrol's search_speed (1.5 m/s) is
only 0.11 m/s faster than a 1.39 m/s platform, so once the platform has any head start -- and it
always does, since it starts moving the instant the drone is airborne, before patrol even reaches
the right leg -- the drone can never close the gap by flying toward a fixed corner. A bounded,
rarely-reversing back-and-forth leg is what actually works, not a literal one-way track.

Setup: as for the linear Phase 3 (vision_node README), except with `motion:=linear`,
`speed:=1.39`, `travel_length:=50.0`, and a widened patrol box:

    ros2 run moving_platform moving_platform_node --ros-args -p motion:=linear -p start_x:=10.0 -p start_y:=0.0 -p heading_deg:=90.0 -p speed:=1.39 -p travel_length:=50.0 -p wait_for_start:=true

    python3 -m mission.circular_landing_main --start-platform --no-curvature --fast --camera-latency 0.09 --corners 0,0 0,9 52,9 52,0

(--camera-latency 0.09 was this project's own measured value on this machine -- measure yours,
do not reuse this number blindly.)

Setup for CIRCULAR motion: as for the linear Phase 3 (vision_node README), except the platform node is started with
`motion:=circular` and the circle's own centre instead of a start point/heading:

    ros2 run ros_gz_sim create -world default -file $(ros2 pkg prefix moving_platform)/share/moving_platform/models/moving_platform/model.sdf -name moving_platform -x 11.0 -y 3.0 -z 0.025
    ros2 run ros_gz_bridge parameter_bridge /model/moving_platform/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist
    ros2 run moving_platform moving_platform_node --ros-args -p motion:=circular -p center_x:=9.5 -p center_y:=3.0 -p radius:=1.5 -p angular_speed:=0.3 -p wait_for_start:=true

(spawn `-x/-y` = `center_x + radius, center_y` = the circle's t=0 position, per
`moving_platform`'s own spawn rule -- see its README.)

then, from workspace/uav_rl_landing with the ROS 2 workspace sourced:

    python3 -m mission.circular_landing_main --start-platform

--start-platform makes the platform begin moving once the drone is airborne (the node was started
with wait_for_start:=true), so every run starts the same way. Pass --no-curvature to compare
against the plain straight-line extrapolation (Phase 3's original model) on the same circular
platform.
"""
import argparse

import rclpy

from mission.moving_landing import MovingLandingConfig, MovingPlatformLander
from mission.ros_io import RosMissionIO


def parse_corner(text):
    try:
        north, east = (float(v) for v in text.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError(f"corner must look like NORTH,EAST (e.g. 0,9), got {text!r}")
    return north, east


def main():
    defaults = MovingLandingConfig()
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--corners", nargs="+", type=parse_corner, metavar="N,E",
                        default=list(defaults.patrol_corners),
                        help="patrol corners in order, PX4 local NED north,east metres "
                             f"(default: {' '.join(f'{n:g},{e:g}' for n, e in defaults.patrol_corners)}). "
                             "The default square's B->C leg (east=9) is what keeps the default circle "
                             "(centre 9.5,3, radius 1.5) inside camera range -- widen/move both together.")
    parser.add_argument("--altitude", type=float, default=defaults.search_altitude,
                        help="patrol altitude in metres (default %(default)s)")
    parser.add_argument("--start-platform", action="store_true",
                        help="publish /moving_platform/start once airborne (platform node run with wait_for_start:=true)")
    parser.add_argument("--camera-latency", type=float, default=None, metavar="SECONDS",
                        help="delay from image capture to detection (default 0.35). The camera measurement is this old "
                             "when it arrives; the estimate uses where the UAV WAS then. Measure yours with "
                             "python3 -m mission.measure_camera_latency")
    parser.add_argument("--no-curvature", action="store_true",
                        help="use the plain straight-line (constant-velocity) tracker extrapolation instead of the "
                             "turning-arc one -- for comparing against Phase 3's original linear-motion model on "
                             "this same circular platform")
    parser.add_argument("--fast", action="store_true",
                        help="higher-bandwidth control profile (kp=3.0, max_accel=5.0, max_speed=4.0, "
                             "tracker_window=0.6, align_speed_tol=0.6, realign_tol=0.8, tracker_max_speed=2.5) "
                             "for platform speeds above ~0.8-1.0 m/s, e.g. the 5 km/h (1.39 m/s) real-hardware "
                             "target -- see this module's docstring for the offline results and the "
                             "camera-latency sensitivity this trades in for it. Offline-tested only, not yet "
                             "run in real Gazebo at 5 km/h (0.8 and 1.0 m/s have).")
    parser.add_argument("--no-ground-truth", action="store_true",
                        help="don't cross-check the camera against /platform/state or report the final offset")
    args = parser.parse_args()

    io = RosMissionIO()
    if args.camera_latency is not None:
        io.camera_latency = args.camera_latency
    io.log(f"Camera latency compensation: {io.camera_latency:.2f} s"
           + (" -- MEASURE THIS for real hardware with --fast, do not guess it" if args.fast else ""))
    io.log(f"Tracker: {'straight-line (--no-curvature)' if args.no_curvature else 'turning-arc (curvature-aware)'}")
    if args.fast:
        io.log("Control profile: --fast (kp=3.0, max_accel=5.0, max_speed=4.0, tracker_window=0.6, "
               "align_speed_tol=0.6, realign_tol=0.8, tracker_max_speed=2.5) -- offline-validated to "
               "5 km/h with an accurately-calibrated camera_latency; not yet run in real Gazebo at "
               "5 km/h. If the platform's real speed is well above ~2 m/s, raise tracker_max_speed "
               "to match -- it caps what the tracker is allowed to report, separately from max_speed.")
    if not io.preflight(require_platform=(not args.no_ground_truth) or args.start_platform):
        io.node.destroy_node()
        rclpy.shutdown()
        return

    truth = io.platform_truth()
    if truth is not None:
        io.log(f"Sim ground truth (evaluation only, never used to steer): platform at NED "
               f"({truth[0]:.2f}, {truth[1]:.2f}), moving ({truth[2]:+.2f} N, {truth[3]:+.2f} E) m/s.")
        if args.start_platform and (truth[2] or truth[3]):
            io.log("Note: the platform is ALREADY moving -- start moving_platform_node with "
                   "-p wait_for_start:=true so it waits for --start-platform.")

    # tracker_max_speed is deliberately NOT raised to max_speed: max_speed is the UAV's own flight
    # authority (how fast it's allowed to fly to catch up), tracker_max_speed is a sanity clip on
    # what the CAMERA FIT is allowed to report as "the platform's velocity" -- kept near the
    # platform's actual expected speed so a noisy/bad fit can't produce a wildly implausible
    # estimate that the control loop then trusts as feedforward. See MovingLandingConfig's own
    # comment on tracker_max_speed in moving_landing.py.
    fast_kwargs = dict(kp=3.0, max_accel=5.0, max_speed=4.0, tracker_window=0.6,
                       align_speed_tol=0.6, realign_tol=0.8, tracker_max_speed=2.5) if args.fast else {}
    config = MovingLandingConfig(
        patrol_corners=tuple(args.corners),
        search_altitude=args.altitude,
        lost_timeout=io.params.simulation_parameters.target_lost_timeout,
        start_platform=args.start_platform,
        use_ground_truth=not args.no_ground_truth,
        tracker_curvature=not args.no_curvature,
        **fast_kwargs,
    )
    result = MovingPlatformLander(io, config, log=io.log).run()

    io.log(f"RESULT: {result['outcome']}")
    if result["outcome"] == "ESTIMATE_MISMATCH":
        io.log("  stopped and landed where it was: the camera estimate disagreed with /platform/state "
               "-- see the MISMATCH line above.")
    offset = result.get("offset_from_platform_centre")
    if result["outcome"] == "LANDED" and offset is not None:
        worst = max(abs(offset[0]), abs(offset[1]))
        if result.get("ground_truth_unreliable"):
            io.log(f"  touched down {offset[0]:+.2f} m north / {offset[1]:+.2f} m east of /platform_state's "
                   "reported centre -- NOT a reliable verdict (see the earlier NOTE: the simulation was not "
                   "running at real time, so this reference had already drifted from the real platform). "
                   f"The 'Contact at ... from the predicted platform position' line above, against what the "
                   "camera actually saw, is the number to trust for this run.")
        else:
            io.log(f"  touched down {offset[0]:+.2f} m north / {offset[1]:+.2f} m east of the platform centre "
                   f"({'ON the platform' if worst <= 0.75 else 'MISSED the platform'}; half-width 0.75 m)")
            if args.fast and worst > 0.75:
                io.log("  NOTE: at this speed the platform can cover real distance in just the couple of "
                       "seconds between touchdown and this report sampling /platform/state again -- a large "
                       "number here does not necessarily mean a bad landing. The 'Contact at ... from the "
                       "predicted platform position' line above (measured at the moment of contact, against "
                       "what the camera actually tracked) is the number to trust.")

    io.node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
