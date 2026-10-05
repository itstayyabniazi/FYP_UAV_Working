"""
Offline tests for the vision missions (no ROS / PX4 / Gazebo needed).

    cd workspace/uav_rl_landing && python3 -m tests.test_missions

They exercise the state machines against tests/fake_world.py; they do NOT
replace running the real simulation (no real camera, no PX4 dynamics).
"""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "ros2_ws", "src", "moving_platform"))

from moving_platform.trajectories import circular_state, linear_state  # the same code the ROS node runs
from mission.moving_landing import MovingLandingConfig, MovingPlatformLander
from mission.target_tracker import PositionHistory, TargetTracker, fit_camera_latency
from mission.vision_landing import VisionLander, VisionLandingConfig
from tests.fake_world import FakeWorld

VERBOSE = "-v" in sys.argv
failures = []


def check(name, condition, detail=""):
    print(f"  {'PASS' if condition else 'FAIL'}  {name}{('  -- ' + detail) if detail else ''}")
    if not condition:
        failures.append(name)


def run_static(title, platform_ned, expect, **world_kw):
    """Phase 2 mission against a static platform at (north, east)."""
    print(f"\n[{title}]")
    world = FakeWorld(lambda t: (platform_ned[1], platform_ned[0], 0.0, 0.0), **world_kw)
    logs = []
    cfg = VisionLandingConfig(expected_xy=platform_ned)
    result = VisionLander(world, cfg, log=lambda m: logs.append(f"[{world.t:6.1f}s] {m}")).run()
    if VERBOSE:
        print("\n".join("    " + m for m in logs))
    return result, "\n".join(logs), world


def run_moving_jitter(title, platform_fn, n=16, jitter_step=1.5, **cfg_kw):
    """Same mission, run n times with the platform's clock offset by increasing amounts -- stands in for
    the unpredictable real-world delay between mission start and the platform actually starting to move
    (arming, takeoff time, discovery). A config that only lands at jitter=0 only works by coincidence."""
    print(f"\n[{title}] (jitter sweep, {n} x {jitter_step}s steps)")
    wins, misses = 0, []
    for i in range(n):
        jitter = i * jitter_step
        world = FakeWorld(lambda t, j=jitter: platform_fn(t + j))
        cfg = MovingLandingConfig(start_platform=True, mission_timeout=180, **cfg_kw)
        result = MovingPlatformLander(world, cfg, log=lambda m: None).run()
        off = result.get("offset_from_platform_centre", (99, 99))
        ok = result["outcome"] == "LANDED" and max(abs(off[0]), abs(off[1])) <= 0.75
        wins += ok
        if not ok:
            misses.append((round(jitter, 1), result["outcome"]))
    rate = wins / n
    print(f"  {wins}/{n} = {rate:.0%} landed on the platform" + (f"; misses at jitter={misses[:5]}" if misses else ""))
    return rate


def run_moving(title, platform_fn, cfg=None, **world_kw):
    print(f"\n[{title}]")
    world = FakeWorld(platform_fn, **world_kw)
    logs = []
    cfg = cfg or MovingLandingConfig(start_platform=True)
    result = MovingPlatformLander(world, cfg, log=lambda m: logs.append(f"[{world.t:6.1f}s] {m}")).run()
    if VERBOSE:
        print("\n".join("    " + m for m in logs))
    return result, "\n".join(logs), world


def platform_error(world):
    """Horizontal distance from the UAV to the platform centre right now."""
    n, e, _, _ = world.platform_ned(world.t)
    return math.hypot(world.p[0] - n, world.p[1] - e)


# ---------------------------------------------------------------- tracker

def test_tracker():
    print("\n[TargetTracker]")
    random.seed(3)
    tracker = TargetTracker()
    t = 0.0
    for _ in range(60):                       # 2 s at 30 Hz, platform at 0.4 m/s north
        t += 1 / 30
        tracker.update(t, 2.0 + 0.4 * t + random.gauss(0, 0.04), 10.0 + random.gauss(0, 0.04))
    s = tracker.state(t)
    check("velocity estimate within 0.06 m/s", abs(s.vx - 0.4) < 0.06 and abs(s.vy) < 0.06,
          f"v=({s.vx:.3f}, {s.vy:.3f})")
    check("position estimate within 0.05 m", abs(s.x - (2.0 + 0.4 * t)) < 0.05)
    s2 = tracker.state(t + 1.0)               # blind for 1 s: predicts forward
    check("predicts 1 s ahead within 0.1 m", abs(s2.x - (2.0 + 0.4 * (t + 1.0))) < 0.1)
    check("gives up after max_extrapolation", tracker.state(t + 10.0) is None)
    # reversal: 0.4 m/s north for 2 s, then 0.4 m/s south
    random.seed(4)
    tracker = TargetTracker()
    t, x, first_correct = 0.0, 0.0, None
    for i in range(120):
        t += 1 / 30
        if t <= 2.0:
            x += 0.4 / 30
        else:
            x -= 0.4 / 30
        tracker.update(t, x + random.gauss(0, 0.04), 10.0 + random.gauss(0, 0.04))
        st = tracker.state(t)
        if t > 2.0 and first_correct is None and st.vx < -0.25:
            first_correct = t - 2.0
    check("notices a velocity reversal within 0.8 s", first_correct is not None and first_correct <= 0.8,
          f"{first_correct:.2f} s" if first_correct is not None else "never")
    check("settles on the new velocity", abs(tracker.state(t).vx + 0.4) < 0.08, f"vx={tracker.state(t).vx:+.3f}")
    steady = TargetTracker()
    random.seed(5)
    tt = 0.0
    for _ in range(600):                      # 20 s of steady motion: no false change alarms
        tt += 1 / 30
        steady.update(tt, 0.4 * tt + random.gauss(0, 0.04), random.gauss(0, 0.04))
    check("no false change alarms over 20 s of steady motion", steady.changes_detected == 0,
          f"{steady.changes_detected} alarms")
    few = TargetTracker()
    few.update(0.0, 1.0, 1.0)
    few.update(0.05, 1.0, 1.0)
    check("too few samples -> velocity not valid, assumed stationary",
          not few.state(0.05).velocity_valid and few.state(0.05).vx == 0.0)


def test_position_history():
    print("\n[PositionHistory]")
    h = PositionHistory()
    check("empty -> None", h.at(1.0) is None)
    for i in range(11):
        h.add(i * 0.1, i * 1.0, -i * 2.0)         # moves (1, -2) per 0.1 s
    x, y = h.at(0.55)
    check("interpolates between samples", abs(x - 5.5) < 1e-9 and abs(y + 11.0) < 1e-9, f"({x:.2f}, {y:.2f})")
    check("clamps before the first sample", h.at(-5.0) == (0.0, 0.0))
    check("clamps after the last sample", h.at(99.0) == (10.0, -20.0))


# ---------------------------------------------------------------- camera latency

def test_latency_fit():
    print("\n[fit_camera_latency]")
    rng = random.Random(0)
    samples = []
    for i in range(600):                       # 20 s at 30 Hz, UAV swinging north-south at up to 1 m/s
        t = i / 30
        v = math.sin(t * 1.3)
        samples.append((t, 3.0 + 0.37 * v + rng.gauss(0, 0.04), 10.0 + rng.gauss(0, 0.04), v, 0.0))
    latency, r2, v_std = fit_camera_latency(samples)
    check("recovers a true latency of 0.37 s within 0.03 s", abs(latency - 0.37) < 0.03, f"{latency:.3f} s, R2 {r2:.2f}")
    still = [(i / 30, 3.0 + rng.gauss(0, 0.04), 10.0, 0.0, 0.0) for i in range(100)]
    check("refuses to fit when the UAV never moved", fit_camera_latency(still) is None)


def test_latency():
    """The bug found in the first Gazebo run: uncompensated camera latency corrupts the velocity estimate."""
    north = lambda t: linear_state(t, 10.0, 0.0, 90.0, 0.4, 0.0)
    cfg = MovingLandingConfig(start_platform=True, mission_timeout=120.0)
    for true_latency, assumed, expect_ok in ((0.4, 0.35, True), (0.4, 0.4, True), (0.4, 0.25, True),
                                             (0.4, 0.55, True), (0.5, 0.35, True), (0.3, 0.35, True),
                                             (0.5, 0.0, False)):
        result, log, world = run_moving(f"true latency {true_latency} s, mission assumes {assumed} s"
                                        f"{'  (UNCOMPENSATED: the field failure)' if assumed == 0 else ''}",
                                        north, cfg=cfg, latency=true_latency, assumed_latency=assumed)
        off = result.get("offset_from_platform_centre", (99, 99))
        landed = result["outcome"] == "LANDED" and max(abs(off[0]), abs(off[1])) <= 0.75
        if expect_ok:
            check("landed on the platform", landed,
                  f"{result['outcome']}, offset ({off[0]:+.2f}, {off[1]:+.2f}) m, {world.t:.0f} s")
        else:
            print(f"    (expected to fail) outcome {result['outcome']}, {world.t:.0f} s -- "
                  f"{'still landed' if landed else 'did not land on the platform'}")


# ---------------------------------------------------------------- phase 2 (static) regression

def test_static():
    result, log, _ = run_static("static platform (3,10): stops mid-leg B->C", (3.0, 10.0), None)
    check("landed on it", result["outcome"] == "LANDED" and result["error_to_ground_truth"] < 0.3,
          f"{result['outcome']}, {result.get('error_to_ground_truth', float('nan')):.2f} m")
    check("never reached corner C", "at point C" not in log and "Point D" not in log)

    result, log, _ = run_static("static platform far outside the square", (30.0, 30.0), None)
    check("NOT_FOUND", result["outcome"] == "NOT_FOUND")

    result, log, _ = run_static("static platform, camera north axis flipped", (3.0, 10.0), None, flip_north=True)
    check("aborts with a flipped-axis hint instead of following it",
          result["outcome"] == "ESTIMATE_MISMATCH" and "north (X) sign looks FLIPPED" in log)


# ---------------------------------------------------------------- phase 3 (moving)

def test_moving():
    """
    KEY FINDING (from a real Gazebo run + this fake world's takeoff timing corrected to match it, see the
    docstring at the top of this file's FakeWorld import): a one-way platform trajectory is fundamentally
    fragile here, AT ANY SPEED, because the total delay before the platform is even visible (takeoff to
    search altitude ~9s in real Gazebo, then however long the patrol takes to reach the right leg) is not
    precisely predictable -- a few seconds of real-world jitter (arming retries, discovery, scheduler
    noise) shifts where a one-way platform has gotten to by then, and a patrol only searches a fixed area
    once. The only structurally robust design found here is a platform that never leaves the vicinity of
    a patrol leg in the first place: a back-and-forth motion anchored ON that leg's line (matching its
    fixed coordinate exactly) can't escape by construction, independent of timing. That is the
    configuration recommended in vision_node/README.md.
    """
    north = lambda speed, length=0.0: (lambda t: linear_state(t, 10.0, 0.0, 90.0, speed, length))

    # These two happen to land at zero jitter (the mechanism works), but are NOT robust to timing --
    # see the jitter sweep below for the actual recommendation. Kept as a basic sanity check only.
    for speed in (0.2, 0.4):
        result, log, world = run_moving(f"linear north at {speed} m/s (single fixed timing, not jitter-tested)",
                                        north(speed))
        check("landed (at this specific timing)", result["outcome"] == "LANDED", result["outcome"])
        check("locked (matched its velocity) before descending", "LOCKED on the platform" in log)

    # ROBUST design: anchored to the B->C patrol leg (east=9 fixed; matches the leg's own coordinate, so
    # the platform is never more than a couple of the camera's east-west metres from being "on the line"
    # the drone actually flies). Verified across a 24 s spread of possible start-up delays.
    on_leg = lambda t: linear_state(t, 9.0, 1.5, 90.0, 0.3, 6.0)
    rate = run_moving_jitter("anchored to the B->C leg, north-south, 0.3 m/s, 6 m back-and-forth", on_leg)
    check("lands on the platform across a range of start-up delays", rate >= 0.85, f"{rate:.0%}")

    # Same idea, anchored to the A->B leg instead (north=0 fixed), testing EAST-WEST motion.
    on_ab_leg = lambda t: linear_state(t, 1.5, 0.0, 0.0, 0.3, 6.0)
    rate = run_moving_jitter("anchored to the A->B leg, east-west, 0.3 m/s, 6 m back-and-forth", on_ab_leg)
    check("lands on the platform across a range of start-up delays", rate >= 0.85, f"{rate:.0%}")

    # Informational only: un-anchored motion, faster or one-way, is NOT asserted on -- it is exactly the
    # class of configuration that misled an earlier version of this file (and the first real attempt).
    for speed, sy in ((0.8, -16.0), (1.0, -16.0)):
        result, _, world = run_moving(
            f"(informational, NOT timing-robust) {speed} m/s starting {-sy:.0f} m behind the square "
            "-- lands at exactly this timing, not others",
            lambda t, sp=speed, y0=sy: linear_state(t, 10.0, y0, 90.0, sp, 0.0))
    print("    (values above depend on exact start-up timing; see the jitter-swept anchored tests for what")
    print("     actually generalizes -- do not copy the informational start distances into real use.)")

    # Back-and-forth reversal timing (independent limitation from the search/catch-up one above): once
    # locked and descending, a reversal in the blind final ~1 m / touchdown phase can still be missed.
    wins = []
    for phase in [i * 0.5 for i in range(20)]:
        result, log, world = run_moving(f"back-and-forth (4 m, reverses every 10 s), phase {phase:.1f} s",
                                        lambda t, ph=phase: linear_state(t + ph, 10.0, 0.0, 90.0, 0.4, 4.0))
        off = result.get("offset_from_platform_centre", (99, 99))
        ok = result["outcome"] == "LANDED" and max(abs(off[0]), abs(off[1])) <= 0.75
        wins.append(ok)
        if not ok:
            print(f"    -> MISSED: {result['outcome']}, offset ({off[0]:+.2f}, {off[1]:+.2f}) m")
    rate = sum(wins) / len(wins)
    print(f"    KNOWN LIMITATION: {sum(wins)}/{len(wins)} = {rate:.0%} of reversal phases land on the platform "
          "(realistic takeoff timing makes the overall mission longer, so relatively more of it overlaps a "
          "reversal near touchdown than in the earlier, faster-takeoff measurement).")
    check("back-and-forth landing rate has not regressed below 10%", rate >= 0.10, f"{rate:.0%}")

    result, log, world = run_moving("2.5 s detection dropout while tracking", north(0.3), dropout=(30.0, 32.5))
    off = result.get("offset_from_platform_centre", (99, 99))
    check("rode out the dropout on the prediction and landed",
          result["outcome"] == "LANDED" and max(abs(off[0]), abs(off[1])) <= 0.75,
          f"{result['outcome']}, offset ({off[0]:+.2f}, {off[1]:+.2f}) m")

    result, log, world = run_moving("8 s detection dropout mid-descent (LOST -> RECOVER -> re-lock)",
                                    north(0.3), dropout=(28.0, 36.0))
    off = result.get("offset_from_platform_centre", (99, 99))
    check("recovered and landed", result["outcome"] == "LANDED" and "RECOVER" in log
          and max(abs(off[0]), abs(off[1])) <= 0.75,
          f"{result['outcome']}, recover={'RECOVER' in log}, offset ({off[0]:+.2f}, {off[1]:+.2f}) m")

    result, log, world = run_moving("moving platform never enters the search area",
                                    lambda t: linear_state(t, 40.0, 40.0, 90.0, 0.4, 0.0))
    check("NOT_FOUND", result["outcome"] == "NOT_FOUND")


def _locked_at(log):
    """Timestamp of the "LOCKED on the platform" log line, or None if it never locked. Lines look
    like "[  12.3s] LOCKED on the platform: ..." (run_moving's f"[{world.t:6.1f}s] {{m}}" format)."""
    for line in log.splitlines():
        if "LOCKED on the platform" in line:
            return float(line.split("s]")[0].strip("[ "))
    return None


def test_circular():
    """
    Phase 3b (circular motion). The control loop itself (MovingPlatformLander._track/_recover) is
    unaffected by the platform's motion shape -- it only ever reads TargetTracker.state(). The one
    thing that needs to change for a platform moving on a curve is the EXTRAPOLATION used while the
    marker is out of view (a straight-line prediction lags behind a curving platform); see
    target_tracker.py's curvature-aware constant-turn-rate (CTRV) extrapolation, opt-in via
    MovingLandingConfig.tracker_curvature (default False -- Phase 3's straight-line motion is
    hardware-validated and untouched by this flag).

    Demo circle: centre (9.5, 3.0) Gazebo ENU, radius 1.5 m, angular_speed 0.3 rad/s (0.45 m/s
    tangential -- comparable to the validated 0.3-0.4 m/s linear runs). Chosen so the whole circle
    stays inside camera range of the default patrol's B->C leg (NED east=9, vision_landing.py's
    default patrol_corners) -- checked below as plain arithmetic, not just assumed.
    """
    demo = lambda t: circular_state(t, 9.5, 3.0, 1.5, 0.3)
    demo_period = 2 * math.pi / 0.3

    # -- geometry: the circle-vs-camera-footprint containment argument, as plain arithmetic
    # (independent of the mission logic) so a future parameter change that breaks it fails
    # immediately and loudly, not as a mysterious drop in landing rate.
    search_altitude = MovingLandingConfig().search_altitude
    leg_east = 9.0                                      # vision_landing.py's default patrol B->C leg
    center_east, center_north, radius = 9.5, 3.0, 1.5
    de_tol = 0.50 * search_altitude - 0.25               # tests/fake_world.py's camera model
    worst_de = abs(center_east - leg_east) + radius
    check("demo circle stays within camera east-west range of the B->C leg",
          worst_de <= de_tol, f"worst case {worst_de:.2f} m vs {de_tol:.2f} m tolerance")
    check("demo circle's north extent sits inside the B->C leg's 0-9 m sweep",
          center_north - radius > 0.0 and center_north + radius < 9.0,
          f"north range [{center_north - radius:.1f}, {center_north + radius:.1f}]")

    # -- patrol/lock/landing across a full revolution's worth of arrival phase, curvature-aware
    rate = run_moving_jitter("circular, centre (9.5,3), r=1.5m, 0.3 rad/s (0.45 m/s)", demo,
                             n=16, jitter_step=demo_period / 16, tracker_curvature=True)
    check("lands on the circling platform across a full revolution of arrival phase", rate >= 0.85,
          f"{rate:.0%}")

    # -- stress circle: what actually stresses the extrapolation is TURN RATE, not translational
    # speed (a straight-line prediction's error grows with how fast the heading rotates, not with
    # how fast the platform moves) -- a raw "faster AND bigger" circle instead mostly stresses the
    # control loop's own speed limit (same ~0.4-0.5 m/s ceiling documented for Phase 3's linear
    # motion), which fails both trackers identically and proves nothing about curvature. So: same
    # ~0.4 m/s tangential speed as the demo circle (well inside the validated range), but a
    # tighter radius -> a much faster-rotating heading (centripetal accel 0.16 m/s^2, ~1.2x the
    # demo circle's). This is the executable evidence the fix does something.
    stress = lambda t: circular_state(t, 9.5, 3.0, 1.0, 0.4)
    stress_period = 2 * math.pi / 0.4
    rate_off = run_moving_jitter("stress circle r=1m 0.4rad/s (tight turn, 0.4 m/s), straight-line tracker",
                                 stress, n=12, jitter_step=stress_period / 12, tracker_curvature=False)
    rate_on = run_moving_jitter("stress circle r=1m 0.4rad/s (tight turn, 0.4 m/s), curvature-aware tracker",
                                stress, n=12, jitter_step=stress_period / 12, tracker_curvature=True)
    check("curvature-aware tracker lands more often than straight-line on the tight-turn circle",
          rate_on > rate_off, f"curvature on {rate_on:.0%} vs off {rate_off:.0%}")

    # -- long dropout, mirrors test_moving()'s 8 s linear-dropout check
    for label, curvature in (("straight-line", False), ("curvature-aware", True)):
        result, log, world = run_moving(f"circular, 8 s dropout mid-descent, {label} tracker", demo,
                                        cfg=MovingLandingConfig(start_platform=True, tracker_curvature=curvature),
                                        dropout=(28.0, 36.0))
        off = result.get("offset_from_platform_centre", (99, 99))
        print(f"    [{label}] outcome={result['outcome']}, offset ({off[0]:+.2f}, {off[1]:+.2f}) m")
        if curvature:
            check("curvature-aware tracker rides out an 8 s dropout on the circling platform",
                  result["outcome"] == "LANDED" and max(abs(off[0]), abs(off[1])) <= 0.75,
                  f"{result['outcome']}, offset ({off[0]:+.2f}, {off[1]:+.2f}) m")

    # -- FOV-containment, grounded in the actual simulated camera geometry (not just "it landed"):
    # once LOCKED, the platform should stay in view almost continuously above the blind-descent
    # floor. Scoped to AFTER lock-on -- the patrol/search phase before that is *supposed* to have
    # long gaps (that is what searching means), so asserting on the whole run would fail on the
    # search phase itself, not on anything wrong with tracking.
    result, log, world = run_moving("circular, footprint containment check", demo,
                                    cfg=MovingLandingConfig(start_platform=True, tracker_curvature=True))
    locked_t = _locked_at(log)
    if locked_t is None:
        check("locked on before checking footprint containment", False, result["outcome"])
    else:
        cfg = MovingLandingConfig()
        band = [row for row in world.footprint_log
                if row[0] >= locked_t and cfg.servo_min_altitude < row[1] <= 7.0]
        if not band:
            print("    (no camera ticks above the blind-descent floor after lock-on -- nothing to check)")
        else:
            visible_fraction = sum(1 for row in band if row[4]) / len(band)
            check("platform visible at least 90% of the time above the blind floor, once locked",
                  visible_fraction >= 0.90, f"{visible_fraction:.0%} over {len(band)} camera ticks")

            worst_streak, streak, prev_t = 0.0, 0.0, None
            for t, alt, dn, de, visible in band:
                dt = 0.0 if prev_t is None else t - prev_t
                if visible:
                    streak = 0.0
                else:
                    streak += dt
                    worst_streak = max(worst_streak, streak)
                prev_t = t
            check("no invisible streak above the blind floor exceeds lost_timeout, once locked",
                  worst_streak <= cfg.lost_timeout, f"worst streak {worst_streak:.1f}s vs {cfg.lost_timeout}s limit")

    # NOTE: the jitter-sweep checks below judge success against error_to_estimate (the mission's
    # own camera-based accuracy number), NOT offset_from_platform_centre / run_moving_jitter's
    # built-in pass criterion. offset_from_platform_centre compares the drone's final resting
    # position against a LATER /platform/state sample (taken after landing, once run() returns) --
    # fine for a slow platform, actively misleading for a fast one: a 1.2-1.39 m/s platform keeps
    # circling for the second or two between touchdown and that later sample, so the "offset" can
    # read several metres even for a landing the mission's own real-time report called accurate to
    # 0.1-0.2 m. Confirmed directly while writing this: several genuinely-LANDED runs at these
    # speeds showed a near-zero error_to_estimate but a multi-metre offset_from_platform_centre.

    def _jitter_sweep(platform_fn, period, n, **kw):
        # cfg_kw goes to MovingLandingConfig; world_kw (noise=, latency=, assumed_latency=) goes to
        # FakeWorld -- split by name so callers can pass either without the two colliding.
        world_keys = {"noise", "latency", "assumed_latency", "dropout", "flip_north", "seed", "uav_start"}
        world_kw = {k: v for k, v in kw.items() if k in world_keys}
        cfg_kw = {k: v for k, v in kw.items() if k not in world_keys}
        step = period / n
        wins, outcomes = 0, []
        for i in range(n):
            j = i * step
            fn = lambda t, jj=j: platform_fn(t + jj)
            world = FakeWorld(fn, **world_kw)
            cfg = MovingLandingConfig(start_platform=True, mission_timeout=180, **cfg_kw)
            r = MovingPlatformLander(world, cfg, log=lambda m: None).run()
            e2e = r.get("error_to_estimate", 99)
            ok = r["outcome"] == "LANDED" and e2e <= 0.75
            wins += ok
            outcomes.append(round(e2e, 2) if r["outcome"] == "LANDED" else r["outcome"])
        return wins / n, outcomes

    # --fast's full gain set, current as of the real-Gazebo follow-up below. tracker_max_speed is
    # deliberately NOT max_speed -- see MovingLandingConfig's own comment on tracker_max_speed.
    fast_gains = dict(tracker_curvature=True, kp=3.0, max_accel=5.0, max_speed=4.0, tracker_window=0.6,
                      align_speed_tol=0.6, realign_tol=0.8, tracker_max_speed=2.5)

    # -- regression: the exact config a real Gazebo run first failed on (radius=2.0m,
    # angular_speed=0.6rad/s, 1.2 m/s tangential) -- default gains cycled LOCK -> lost -> RECOVER
    # forever, traced to _drop_old_motion_if_changed() false-firing on ordinary curvature at this
    # turn rate (confirmed separately: 0 false triggers/6.7s on the demo circle, 6 on this one,
    # before the angle-based fix). The fix alone is NOT enough here -- 1.2 m/s is already past what
    # the DEFAULT control gains can track at all (see the --fast profile below); this only lands
    # with --fast gains too. Both pieces are tested together because that combination is what the
    # real run needs.
    original_bug_config = lambda t: circular_state(t, 9.5, 3.0, 2.0, 0.6)
    rate, outs = _jitter_sweep(original_bug_config, 2 * math.pi / 0.6, 10, **fast_gains)
    print(f"\n[regression: r=2m 0.6rad/s, fixed detector + --fast gains] {rate:.0%}  {outs}")
    check("the originally-failing config now lands reliably (was: endless LOCK/lost/RECOVER)",
          rate >= 0.85, f"{rate:.0%}")
    # ... and confirm DEFAULT gains genuinely still can't handle this speed (not a bug -- a real,
    # now-understood control-law ceiling; --fast exists because of exactly this).
    rate_default, outs_default = _jitter_sweep(original_bug_config, 2 * math.pi / 0.6, 6, tracker_curvature=True)
    print(f"[same config, DEFAULT gains (expected to still fail)] {rate_default:.0%}  {outs_default}")
    check("default gains still can't track 1.2 m/s (confirms --fast is necessary, not optional)",
          rate_default < 0.5, f"{rate_default:.0%}")

    # -- the real-hardware target: 5 km/h = 1.39 m/s, --fast profile. radius=2.0m gives
    # angular_speed=1.39/2.0 rad/s for that tangential speed.
    target_omega = 1.39 / 2.0
    fivekph = lambda t: circular_state(t, 9.5, 3.0, 2.0, target_omega)
    rate, outs = _jitter_sweep(fivekph, 2 * math.pi / target_omega, 10, **fast_gains)
    print(f"[5 km/h target (r=2m, 1.39 m/s tangential), --fast profile] {rate:.0%}  {outs}")
    check("reaches the 5 km/h real-hardware target with --fast", rate >= 0.85, f"{rate:.0%}")

    # -- regression #2: a SECOND real Gazebo run at 5 km/h, with the change-detector fix and the
    # first cut of --fast (kp/max_accel/max_speed/tracker_window only, no hysteresis change) and
    # correctly-measured latency, still didn't land -- it locked on, then oscillated in and out of
    # "aligned" for the whole mission_timeout without ever staying converged long enough to finish
    # the descent. Reproduced offline by raising detection noise to 0.2 m (plausible real
    # motion-blur/detection noise for a fast-moving marker, vs the 0.04 m default): the first --fast
    # cut drops to 2/10 under this stress, matching the real symptom. The fix: align_speed_tol
    # (0.3->0.6 m/s) and realign_tol (0.5->0.8 m) -- the hysteresis around "aligned enough to
    # descend" -- were tuned for the original, less noisy regime and were too tight for this one.
    rate_first_cut, outs_first_cut = _jitter_sweep(
        fivekph, 2 * math.pi / target_omega, 10, noise=0.2,
        tracker_curvature=True, kp=3.0, max_accel=5.0, max_speed=4.0, tracker_window=0.6)
    print(f"[5 km/h, noise stress (0.2m), FIRST --fast cut (no hysteresis change) -- "
          f"expected to still struggle] {rate_first_cut:.0%}  {outs_first_cut}")
    check("first --fast cut (pre-hysteresis-fix) genuinely struggles under detection-noise stress "
          "(confirms the real Gazebo symptom, not a fluke)", rate_first_cut < 0.5, f"{rate_first_cut:.0%}")
    # IMPORTANT: matters which latency BASELINE this runs at, not just whether it's matched.
    # FakeWorld's own default (true=0.4s, assumed=0.35s) is the "well-calibrated" baseline used
    # throughout the rest of this file (inherited from the original Phase 3's real measured
    # latency on this project's dev machine) -- but it is NOT this session's actual measured value
    # (0.09s, from a real Gazebo run's `measure_camera_latency.py`). Tested both explicitly below:
    # a LOW baseline (<=0.2s, matching this user's real measurement) handles the noise stress fine
    # even with the hysteresis fix's earlier version; a HIGH baseline (0.4s) does not, EVEN WITH
    # PERFECT calibration (assumed==true, zero gap) -- 0.4s of latency at 1.39 m/s alone means the
    # estimate is always chasing where the platform was 0.56 m ago, and no amount of calibration
    # accuracy fixes that. This is a real, separate limit from the calibration-gap one above:
    # --fast at 5 km/h needs a LOW absolute camera latency, not just an accurately-measured one.
    rate_stress, outs_stress = _jitter_sweep(fivekph, 2 * math.pi / target_omega, 10, noise=0.2,
                                             latency=0.09, assumed_latency=0.09, **fast_gains)
    print(f"[5 km/h, noise stress (0.2m), LOW latency baseline (0.09s, this session's measured value), "
          f"current --fast] {rate_stress:.0%}  {outs_stress}")
    check("current --fast holds up under noise stress at 5 km/h, at a low (real, measured) latency baseline",
          rate_stress >= 0.85, f"{rate_stress:.0%}")
    rate_high_baseline, outs_high_baseline = _jitter_sweep(
        fivekph, 2 * math.pi / target_omega, 10, noise=0.2, latency=0.4, assumed_latency=0.4, **fast_gains)
    print(f"[5 km/h, noise stress (0.2m), HIGH latency baseline (0.4s, PERFECTLY calibrated), "
          f"current --fast -- expected to still struggle] {rate_high_baseline:.0%}  {outs_high_baseline}")
    check("current --fast still struggles at 5 km/h under noise stress with a high latency baseline, "
          "even PERFECTLY calibrated (documents this as a separate, real limit -- not fixed by the "
          "hysteresis change, and not a calibration problem)", rate_high_baseline < 0.5, f"{rate_high_baseline:.0%}")
    # No regression at the other validated speeds under the same stress, at the low (real) baseline.
    for v, radius in ((0.45, 1.5), (0.8, 2.0), (1.0, 2.0)):
        omega = v / radius
        fn = lambda t, r=radius, w=omega: circular_state(t, 9.5, 3.0, r, w)
        rate_v, outs_v = _jitter_sweep(fn, 2 * math.pi / omega, 8, noise=0.2,
                                       latency=0.09, assumed_latency=0.09, **fast_gains)
        check(f"current --fast holds up under noise stress at {v} m/s too (no regression)",
              rate_v >= 0.85, f"{rate_v:.0%}  {outs_v}")

    # -- FLIGHT SAFETY regression, not just landing accuracy: a real Gazebo run at 5 km/h crashed
    # the drone mid-LOCK, right after the tracker reported a platform velocity of ~3 m/s -- more
    # than double this platform's actual max speed (1.39 m/s). Root cause: TargetTracker was
    # constructed with c.max_speed directly, the SAME field as the UAV's own flight-speed
    # authority. --fast raises that to 4.0 m/s (so the UAV has spare speed to catch up), which
    # ALSO raised the ceiling on what a noisy/bad camera fit is allowed to report as "the
    # platform's velocity" -- a real PX4-controlled vehicle then trusted that implausible estimate
    # as feedforward and, per the crash, could not handle it. Fixed by decoupling: a new
    # tracker_max_speed field clips the ESTIMATE separately from max_speed (the UAV's own limit).
    # Confirmed directly (instrumenting TargetTracker.state() to record its peak reported speed
    # under harsh noise, 0.5 m, 10 seeds): the old coupled clip let estimates reach 3.3-4.0 m/s;
    # the new one holds every single one at exactly 2.5 m/s. This must never regress -- an
    # implausible velocity estimate reaching the control loop is a real-hardware safety issue, not
    # just a bad landing.
    def _peak_estimate_speed(radius, omega, noise, seed, **cfg_kw):
        fn = lambda t: circular_state(t, 9.5, 3.0, radius, omega)
        cfg = MovingLandingConfig(start_platform=True, mission_timeout=180, tracker_curvature=True, **cfg_kw)
        world = FakeWorld(fn, noise=noise, seed=seed)
        lander = MovingPlatformLander(world, cfg, log=lambda m: None)
        peak = [0.0]
        orig_state = lander.tracker.state
        def wrapped(now):
            st = orig_state(now)
            if st is not None:
                peak[0] = max(peak[0], math.hypot(st.vx, st.vy))
            return st
        lander.tracker.state = wrapped
        lander.run()
        return peak[0]

    true_max_speed = 2.0 * target_omega  # this platform's actual max speed, 1.39 m/s
    peaks = [_peak_estimate_speed(2.0, target_omega, 0.5, seed, kp=3.0, max_accel=5.0, max_speed=4.0,
                                  tracker_window=0.6, align_speed_tol=0.6, realign_tol=0.8,
                                  tracker_max_speed=2.5)
             for seed in range(1, 11)]
    print(f"\n[flight safety: peak tracker velocity ESTIMATE under harsh noise, current --fast] "
          f"max over 10 seeds = {max(peaks):.2f} m/s (platform's real max {true_max_speed:.2f} m/s)")
    check("tracker_max_speed reliably caps the velocity estimate, even under harsh noise "
          "(prevents feeding an implausible feedforward command to the flight controller)",
          max(peaks) <= 2.5 + 1e-6, f"peak {max(peaks):.2f} m/s vs 2.5 m/s cap")

    # -- the cost of --fast: latency-sensitivity. --fast trades away most of the margin
    # max_accel=1.0 was deliberately chosen for (see MovingLandingConfig's own comment on
    # max_accel). Confirm both sides of this so it's a documented, tested tradeoff, not a surprise:
    # matched latency lands reliably, a 0.1s mismatch in either direction does not.
    print("\n[--fast latency sensitivity at 5 km/h]")
    for assumed_latency, expect_ok in ((0.35, True), (0.25, False), (0.55, False)):
        wins = 0
        n = 6
        step = (2 * math.pi / target_omega) / n
        for i in range(n):
            j = i * step
            fn = lambda t, jj=j: circular_state(t + jj, 9.5, 3.0, 2.0, target_omega)
            world = FakeWorld(fn, latency=0.4, assumed_latency=assumed_latency)
            cfg = MovingLandingConfig(start_platform=True, mission_timeout=180, **fast_gains)
            r = MovingPlatformLander(world, cfg, log=lambda m: None).run()
            wins += r["outcome"] == "LANDED" and r.get("error_to_estimate", 99) <= 0.75
        rate = wins / n
        label = "matched (0.05s gap, same as everywhere else in this project)" if assumed_latency == 0.35 \
            else f"mismatched by {abs(assumed_latency - 0.4):.2f}s"
        print(f"  assumed_latency={assumed_latency} ({label}): {wins}/{n} = {rate:.0%}")
        if expect_ok:
            check(f"--fast lands reliably at 5 km/h with correctly-calibrated latency ({assumed_latency}s)",
                  rate >= 0.75, f"{rate:.0%}")
        else:
            check(f"--fast genuinely fails (not gracefully) on a {abs(assumed_latency-0.4):.2f}s latency "
                  "mismatch -- documents the real cost, not a silent regression risk",
                  rate < 0.5, f"{rate:.0%}")


if __name__ == "__main__":
    test_tracker()
    test_position_history()
    test_static()
    test_latency_fit()
    test_latency()
    test_moving()
    test_circular()
    print("\n" + ("ALL TESTS PASSED" if not failures else f"FAILED: {failures}"))
    sys.exit(1 if failures else 0)
