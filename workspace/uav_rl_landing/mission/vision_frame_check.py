"""
vision_frame_check.py

Automates step 5 of vision_node/README.md ("verify the frame convention before
trusting it"). Flies to three KNOWN positions relative to the configured
platform location (sim ground truth) and compares what the camera pipeline
reports (/landing_target) with what it should:

    1. directly above the platform   -> rel ~ (0, 0, height)
    2. platform 2 m NORTH of the UAV -> rel ~ (+2, 0, height)
    3. platform 2 m EAST  of the UAV -> rel ~ (0, +2, height)

rel_x/rel_y are PX4-local NED offsets (north/east) of the marker from the UAV.
A swapped or sign-flipped axis points at CAMERA_TO_BODY in
vision_node/aruco_landing_target_node.py. Do this BEFORE the first vision
landing: a wrong sign makes the visual-servo loop fly AWAY from the marker.

Same setup as the vision landing (platform spawned + static at the configured
location, camera bridge, uav_state_node, landing_controller,
aruco_landing_target_node). Run from workspace/uav_rl_landing:
    python3 -m mission.vision_frame_check
"""
import rclpy

from mission.ros_io import RosMissionIO
from mission.vision_landing import VisionLander, VisionLandingConfig

HEIGHT = 3.0     # [m] hover height for the measurements
OFFSET = 2.0     # [m] horizontal offset for tests 2 and 3
TOLERANCE = 0.4  # [m]
SETTLE = 3.0     # [s] hold before sampling
SAMPLE = 1.5     # [s] sampling window


def diagnose(expected, measured):
    ex, ey = expected
    mx, my = measured
    if abs(mx - ex) <= TOLERANCE and abs(my - ey) <= TOLERANCE:
        return None
    hints = []
    if abs(mx - ey) <= TOLERANCE and abs(my - ex) <= TOLERANCE and (ex, ey) != (0.0, 0.0):
        hints.append("X and Y look SWAPPED")
    if ex and abs(mx + ex) <= TOLERANCE:
        hints.append("X sign looks FLIPPED")
    if ey and abs(my + ey) <= TOLERANCE:
        hints.append("Y sign looks FLIPPED")
    return ", ".join(hints) or "no simple swap/flip pattern -- check the camera mount pose and MARKER_SIZE_M"


def main():
    io = RosMissionIO()
    if not io.preflight():
        io.node.destroy_node()
        rclpy.shutdown()
        return

    platform = io.reset.platform_position_local()
    io.log(f"Platform (sim ground truth) at NED ({platform[0]:.2f}, {platform[1]:.2f}).")
    lander = VisionLander(io, VisionLandingConfig(search_altitude=HEIGHT), log=io.log)
    lander._t0 = io.now()

    x0, y0, _ = io.uav_position()
    io.start(x0, y0, HEIGHT)
    lander.sp = [x0, y0, HEIGHT]
    climb_deadline = io.now() + 40.0
    while abs(io.uav_position()[2] - HEIGHT) > 0.3:  # climb before travelling
        if io.now() > climb_deadline:
            io.log("Never reached the hover height (armed? offboard?) -- aborting.")
            io.land()
            io.node.destroy_node()
            rclpy.shutdown()
            return
        io.sleep(0.2)

    cases = [
        ("above the platform", (0.0, 0.0), (0.0, 0.0)),
        (f"platform {OFFSET:.0f} m NORTH of the UAV", (-OFFSET, 0.0), (OFFSET, 0.0)),
        (f"platform {OFFSET:.0f} m EAST of the UAV", (0.0, -OFFSET), (0.0, OFFSET)),
    ]
    failures = 0
    for name, uav_offset, expected in cases:
        tx, ty = platform[0] + uav_offset[0], platform[1] + uav_offset[1]
        io.log(f"--- {name}: flying to NED ({tx:.1f}, {ty:.1f}) at {HEIGHT} m")
        if not lander.goto(tx, ty, HEIGHT):
            io.log("Could not reach the point -- aborting the check.")
            failures += 1
            break
        io.sleep(SETTLE)
        io._detections.clear()
        io.sleep(SAMPLE)
        measurement = io.relative_measurement(SAMPLE)
        if measurement is None:
            io.log("  marker NOT detected here -- check the camera bridge / aruco node / marker texture.")
            failures += 1
            continue
        mx, my, mz, n = measurement
        hint = diagnose(expected, (mx, my))
        height_ok = abs(mz - (HEIGHT - 0.05)) <= TOLERANCE
        io.log(f"  expected rel ({expected[0]:+.1f}, {expected[1]:+.1f}, ~{HEIGHT - 0.05:.1f})  "
               f"measured ({mx:+.2f}, {my:+.2f}, {mz:.2f})  [{n} detections]")
        if hint is not None or not height_ok:
            failures += 1
            io.log(f"  FAIL: {hint or 'rel_z (height) is off -- check MARKER_SIZE_M vs the model'}")
        else:
            io.log("  OK")

    io.log("FRAME CHECK " + ("PASSED -- safe to run the vision landing." if failures == 0
                             else f"FAILED ({failures} problem(s)) -- do NOT run the vision landing yet."))
    io.land()
    io.wait_landed(30.0)
    io.node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
