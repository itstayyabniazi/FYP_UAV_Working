"""
measure_camera_latency.py

Measures the delay between a camera image being taken and its detection reaching
the mission code (Gazebo rendering + ros_gz_bridge + DDS + the aruco node +
this process's callbacks). The landing on a MOVING platform needs it: the marker's
world position is UAV-position + camera-measurement, and the measurement is that
many seconds old, so the UAV position must be the one from then. A wrong value
(or none) leaves a term `latency x UAV velocity` in the estimate that fakes a
platform velocity -- that is what made the first moving-platform run in Gazebo
never lock on.

How: fly over a STATIC marker, move back and forth to get some velocity and
acceleration, and fit   estimate = marker + latency x UAV_velocity   over the
samples (the estimate here is deliberately uncompensated).

Setup = Phase 2's: platform spawned and NOT moving, at the location in
parameters.py (platform_world_x/y, default Gazebo (10, 3)); camera bridge,
uav_state_node, landing_controller, aruco_landing_target_node running. Do NOT
run moving_platform_node. Then, from workspace/uav_rl_landing:

    python3 -m mission.measure_camera_latency

and pass the result to the landing:  --camera-latency 0.37
"""
import rclpy

from mission.ros_io import RosMissionIO
from mission.target_tracker import fit_camera_latency
from mission.vision_landing import VisionLander, VisionLandingConfig

ALTITUDE = 4.0     # [m] the marker stays in view over +-1.5 m north-south here
SWING = 1.5        # [m]
SPEED = 1.0        # [m/s]
CYCLES = 3


def main():
    io = RosMissionIO()
    if not io.preflight():
        io.node.destroy_node()
        rclpy.shutdown()
        return
    north, east = io.reset.platform_position_local()
    io.log(f"Static marker assumed at NED ({north:.2f}, {east:.2f}) (parameters.py). Take off to {ALTITUDE} m and hover above it.")

    lander = VisionLander(io, VisionLandingConfig(search_altitude=ALTITUDE), log=io.log)
    lander._t0 = io.now()
    x0, y0, _ = io.uav_position()
    io.start(x0, y0, ALTITUDE)
    lander.sp = [x0, y0, ALTITUDE]
    deadline = io.now() + 40.0
    while abs(io.uav_position()[2] - ALTITUDE) > 0.3 and io.now() < deadline:
        io.sleep(0.2)
    lander.goto(north, east, ALTITUDE)
    io.sleep(3.0)
    if not io.confirmed(3, 1.0):
        io.log("The marker is not being detected from here -- is the platform spawned at the location in "
               "parameters.py, and is the aruco node running? Aborting.")
        io.land()
        io.wait_landed(30.0)
        io.node.destroy_node()
        rclpy.shutdown()
        return

    io.log(f"Marker in view. Swinging +-{SWING} m north-south at {SPEED} m/s, {CYCLES} times, collecting samples.")
    io._raw.clear()
    for _ in range(CYCLES):
        lander.goto(north + SWING, east, ALTITUDE, hspeed=SPEED)
        lander.goto(north - SWING, east, ALTITUDE, hspeed=SPEED)
    lander.goto(north, east, ALTITUDE)

    samples = list(io._raw)
    result = fit_camera_latency(samples) if len(samples) >= 30 else None
    if result is None:
        io.log(f"Only {len(samples)} usable samples -- the marker was lost during the swing. Try again.")
    else:
        latency, r2, v_std = result
        io.log(f"{len(samples)} samples, UAV velocity std {v_std:.2f} m/s.")
        io.log(f"MEASURED CAMERA LATENCY: {latency:.2f} s (fit R^2 = {r2:.2f}).")
        if v_std < 0.3 or r2 < 0.3 or not (0.0 <= latency <= 1.5):
            io.log("  ...but the fit looks unreliable (little motion, poor fit or an implausible value). "
                   "Repeat the run, or keep the default.")
        else:
            io.log(f"  use:  python3 -m mission.moving_landing_main --start-platform --camera-latency {latency:.2f}")

    io.land()
    io.wait_landed(30.0)
    io.node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
