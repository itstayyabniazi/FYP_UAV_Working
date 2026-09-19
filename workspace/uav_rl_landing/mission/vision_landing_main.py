"""
Camera-guided landing on a static platform -- one script.

Takes off, flies the corners of a square (A -> B -> C -> D) at the search
altitude, hovering briefly at each, and the moment the ArUco marker is detected
-- mid-leg or at a corner -- stops the patrol, centres over the marker,
descends and lands on it. The drone is NOT told where the platform is: the
configured location (parameters.py platform_world_x/y) is only used to print
how far the camera's estimate and the final landing are from the sim ground
truth, and to hint at swapped/flipped camera axes if they disagree.

Setup (see vision_node/README.md): PX4 SITL + XRCE agent + GCS heartbeat, the
platform spawned and left still, camera bridge, uav_state_node,
landing_controller, aruco_landing_target_node. Run from workspace/uav_rl_landing
with the ROS 2 workspace sourced:

    python3 -m mission.vision_landing_main
    python3 -m mission.vision_landing_main --corners 0,0 0,9 9,9 9,0 --altitude 5
    python3 -m mission.vision_landing_main --no-ground-truth   # platform moved, parameters.py not updated

Corners are PX4 local NED "north,east" metres from where the UAV spawned.
"""
import argparse

import rclpy

from mission.ros_io import RosMissionIO
from mission.vision_landing import VisionLander, VisionLandingConfig


def parse_corner(text):
    try:
        north, east = (float(v) for v in text.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError(f"corner must look like NORTH,EAST (e.g. 0,9), got {text!r}")
    return north, east


def main():
    defaults = VisionLandingConfig()
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--corners", nargs="+", type=parse_corner, metavar="N,E",
                        default=list(defaults.patrol_corners),
                        help="patrol corners in order, PX4 local NED north,east metres "
                             f"(default: {' '.join(f'{n:g},{e:g}' for n, e in defaults.patrol_corners)})")
    parser.add_argument("--altitude", type=float, default=defaults.search_altitude,
                        help="patrol altitude in metres (default %(default)s; the 0.5 m marker "
                             "gets small above ~6 m)")
    parser.add_argument("--no-ground-truth", action="store_true",
                        help="don't cross-check the camera against parameters.py's platform location "
                             "(use when you moved the platform without updating it). By default the "
                             "mission LANDS IMMEDIATELY instead of following a camera estimate that "
                             "disagrees with the ground truth by > 1 m.")
    args = parser.parse_args()

    io = RosMissionIO()
    if not io.preflight():
        io.node.destroy_node()
        rclpy.shutdown()
        return

    sim = io.params.simulation_parameters
    expected = io.reset.platform_position_local()  # sim ground truth: evaluation only
    io.log(f"Sim ground truth (evaluation only, never used to steer): platform at NED "
           f"({expected[0]:.2f}, {expected[1]:.2f}).")
    config = VisionLandingConfig(
        patrol_corners=tuple(args.corners),
        search_altitude=args.altitude,
        lost_timeout=sim.target_lost_timeout,
        expected_xy=None if args.no_ground_truth else expected,
    )
    result = VisionLander(io, config, log=io.log).run()

    io.log(f"RESULT: {result['outcome']}")
    if result.get("marker_estimate") is not None:
        io.log(f"  camera placed the marker at ({result['marker_estimate'][0]:.2f}, "
               f"{result['marker_estimate'][1]:.2f}) NED; landed at "
               f"({result['final_xy'][0]:.2f}, {result['final_xy'][1]:.2f}) "
               f"-> {result['error_to_estimate']:.2f} m from that estimate")
    if result["outcome"] == "ESTIMATE_MISMATCH":
        io.log("  stopped and landed where it was because the camera estimate disagreed with the "
               "sim ground truth -- see the MISMATCH line above.")
    if result["outcome"] == "LANDED" and "error_to_ground_truth" in result:
        error = result["error_to_ground_truth"]
        io.log(f"  {error:.2f} m from the configured platform centre "
               f"({'ON the platform' if error <= 0.75 else 'MISSED the platform'}; half-width 0.75 m)")

    io.node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
