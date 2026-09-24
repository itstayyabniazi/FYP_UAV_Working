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


if __name__ == "__main__":
    test_tracker()
    test_position_history()
    test_static()
    test_latency_fit()
    test_latency()
    test_moving()
    print("\n" + ("ALL TESTS PASSED" if not failures else f"FAILED: {failures}"))
    sys.exit(1 if failures else 0)
