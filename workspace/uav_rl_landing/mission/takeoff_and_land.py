"""
takeoff_and_land.py

Scripted (non-RL) mission: take off, hold above the hard-coded landing platform
(simulation_parameters.platform_world_x/y), descend straight down onto it, then
hand the last stretch to PX4's own AUTO.LAND and report how far from the
platform centre the UAV ended up.

Reuses the existing pipeline unchanged: ResetManager publishes the position
setpoints, landing_controller (position mode) flies them, and /uav/state
provides feedback. Needs px4_bridge + landing_controller running, but NOT
relative_state or moving_platform_node -- the platform is static here.

Run from workspace/uav_rl_landing, with the ROS 2 workspace sourced:
    python3 -m mission.takeoff_and_land
"""
import time

import numpy as np
import rclpy
from rclpy.node import Node

from config.parameters import Parameters
from environment.reset_manager import ResetManager

HOLD_TIMEOUT = 30.0        # [s] max time to reach + settle above the platform
HANDOFF_ALTITUDE = 0.5     # [m] AGL at which PX4's AUTO.LAND takes over
LANDING_WAIT = 20.0        # [s] max time to wait for touchdown after handoff
TOUCHDOWN_ALTITUDE = 0.3   # [m] AGL below which we count the UAV as landed
DESCENT_PERIOD = 0.1       # [s] between descending setpoint updates


def main():
    rclpy.init()
    node = Node("takeoff_and_land")
    params = Parameters()
    sim = params.simulation_parameters
    reset = ResetManager(node, params)

    def spin_for(duration):
        end = time.time() + duration
        while (remaining := end - time.time()) > 0:
            rclpy.spin_once(node, timeout_sec=remaining)

    log = node.get_logger().info

    while reset._uav_state is None:
        log("Waiting for /uav/state (is px4_bridge running?)...")
        spin_for(1.0)

    pose = reset.generate_initial_pose()
    log(f"Platform (Gazebo ENU) = ({sim.platform_world_x}, {sim.platform_world_y}) "
        f"-> PX4 local NED target = ({pose['x']}, {pose['y']}), hover {pose['z']} m")

    # 1. Take off and hold above the platform.
    reset.start_takeoff(pose)
    start = time.time()
    while not reset.is_at_target(pose):
        if time.time() - start > HOLD_TIMEOUT:
            log("Never settled above the platform within the timeout -- aborting.")
            rclpy.shutdown()
            return
        spin_for(0.2)
    log("Hovering above the platform. Descending...")

    # 2. Controlled descent: slide the position target down at the configured
    #    descent rate, holding x/y on the platform the whole way.
    descent_rate = sim.initial_action_values["vz"]  # [m/s]
    z = pose["z"]
    while z > HANDOFF_ALTITUDE:
        z = max(HANDOFF_ALTITUDE, z - descent_rate * DESCENT_PERIOD)
        reset.update_takeoff_target({"x": pose["x"], "y": pose["y"], "z": z})
        spin_for(DESCENT_PERIOD)
    state = reset._uav_state
    log(f"At {HANDOFF_ALTITUDE} m target altitude, horizontal error "
        f"{np.hypot(state.x - pose['x'], state.y - pose['y']):.2f} m. Handing off to AUTO.LAND.")

    # 3. PX4's own land + disarm sequence.
    reset.land_and_disarm()
    start = time.time()
    while time.time() - start < LANDING_WAIT:
        spin_for(0.2)
        state = reset._uav_state
        if -state.z <= TOUCHDOWN_ALTITUDE and np.linalg.norm([state.vx, state.vy, state.vz]) < 0.1:
            break

    state = reset._uav_state
    error = float(np.hypot(state.x - pose["x"], state.y - pose["y"]))
    log(f"Landed at NED ({state.x:.2f}, {state.y:.2f}), altitude {-state.z:.2f} m; "
        f"{error:.2f} m from the platform centre "
        f"({'ON the platform' if error <= 0.75 else 'MISSED the platform'} -- platform half-width is 0.75 m).")

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
