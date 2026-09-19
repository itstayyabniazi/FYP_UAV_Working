"""
Phase 2 entry point: camera-guided landing on a static platform.
The drone is NOT told where the platform is (the configured location is only
used to print an evaluation error at the end).

Run from workspace/uav_rl_landing, ROS 2 workspace sourced:
    python3 -m mission.vision_landing_main
"""
import rclpy

from mission.ros_io import RosMissionIO
from mission.vision_landing import VisionLander, VisionLandingConfig


def main():
    io = RosMissionIO()
    if not io.preflight():
        io.node.destroy_node()
        rclpy.shutdown()
        return

    sim = io.params.simulation_parameters
    expected = io.reset.platform_position_local()  # sim ground truth: evaluation only
    config = VisionLandingConfig(lost_timeout=sim.target_lost_timeout, expected_xy=expected)
    result = VisionLander(io, config, log=io.log).run()

    io.log(f"RESULT: {result['outcome']}")
    if result.get("marker_estimate") is not None:
        io.log(f"  camera placed the marker at ({result['marker_estimate'][0]:.2f}, "
               f"{result['marker_estimate'][1]:.2f}) NED; landed at "
               f"({result['final_xy'][0]:.2f}, {result['final_xy'][1]:.2f}) "
               f"-> {result['error_to_estimate']:.2f} m from that estimate")
    if "error_to_ground_truth" in result:
        error = result["error_to_ground_truth"]
        io.log(f"  {error:.2f} m from the configured platform centre "
               f"({'ON the platform' if error <= 0.75 else 'MISSED the platform'}; half-width 0.75 m)")

    io.node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
