"""
Phase 3: camera-guided landing on a MOVING platform (straight-line motion) -- one script.

Takes off, patrols the corners of a square at the search altitude, and the
moment the ArUco marker is confirmed it stops, LOCKS onto the platform (estimates
its velocity and flies along with it), descends while aligned, and lands on it.
The drone is not told where the platform is or how fast it moves. The platform's
ground truth (/platform/state) is used only to cross-check the camera and to
report where the drone ended up relative to the platform centre.

Setup: as for Phase 2 (vision_node README), except the platform node DOES run
here, because it is what moves the platform:

    ros2 run ros_gz_sim create -world default -file $(ros2 pkg prefix moving_platform)/share/moving_platform/models/moving_platform/model.sdf -name moving_platform -x 10.0 -y 0.0 -z 0.025
    ros2 run ros_gz_bridge parameter_bridge /model/moving_platform/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist
    ros2 run moving_platform moving_platform_node --ros-args -p motion:=linear -p start_x:=10.0 -p start_y:=0.0 -p heading_deg:=90.0 -p speed:=0.4 -p wait_for_start:=true

then, from workspace/uav_rl_landing with the ROS 2 workspace sourced:

    python3 -m mission.moving_landing_main --start-platform

--start-platform makes the platform begin moving once the drone is airborne (the
node was started with wait_for_start:=true), so every run starts the same way.
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
                             "A moving platform can leave a small square before the patrol reaches it -- "
                             "enlarge it for faster platforms.")
    parser.add_argument("--altitude", type=float, default=defaults.search_altitude,
                        help="patrol altitude in metres (default %(default)s)")
    parser.add_argument("--start-platform", action="store_true",
                        help="publish /moving_platform/start once airborne (platform node run with wait_for_start:=true)")
    parser.add_argument("--camera-latency", type=float, default=None, metavar="SECONDS",
                        help="delay from image capture to detection (default 0.35). The camera measurement is this old "
                             "when it arrives; the estimate uses where the UAV WAS then. Measure yours with "
                             "python3 -m mission.measure_camera_latency")
    parser.add_argument("--no-ground-truth", action="store_true",
                        help="don't cross-check the camera against /platform/state or report the final offset")
    args = parser.parse_args()

    io = RosMissionIO()
    if args.camera_latency is not None:
        io.camera_latency = args.camera_latency
    io.log(f"Camera latency compensation: {io.camera_latency:.2f} s")
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

    config = MovingLandingConfig(
        patrol_corners=tuple(args.corners),
        search_altitude=args.altitude,
        lost_timeout=io.params.simulation_parameters.target_lost_timeout,
        start_platform=args.start_platform,
        use_ground_truth=not args.no_ground_truth,
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
            # Seen for real: the drone landed 0.02-0.06 m from what the camera predicted (accurate) while this
            # ground-truth comparison read 1.2-1.6 m off (a real-time-factor drift artefact, not a bad landing) --
            # don't call it a miss on a yardstick already flagged as broken earlier in this run.
            io.log(f"  touched down {offset[0]:+.2f} m north / {offset[1]:+.2f} m east of /platform_state's "
                   "reported centre -- NOT a reliable verdict (see the earlier NOTE: the simulation was not "
                   "running at real time, so this reference had already drifted from the real platform). "
                   f"The 'Contact at ... from the predicted platform position' line above, against what the "
                   "camera actually saw, is the number to trust for this run.")
        else:
            io.log(f"  touched down {offset[0]:+.2f} m north / {offset[1]:+.2f} m east of the platform centre "
                   f"({'ON the platform' if worst <= 0.75 else 'MISSED the platform'}; half-width 0.75 m)")

    io.node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
