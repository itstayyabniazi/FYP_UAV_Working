"""
takeoff_and_land.py

Scripted (non-RL) mission: take off, hold above the hard-coded landing platform
(simulation_parameters.platform_world_x/y), descend straight down onto it, then
hand the last stretch to PX4's own AUTO.LAND and report how far from the
platform centre the UAV ended up.

The landing target is taken from the platform's ground-truth /platform/state,
so moving_platform_node must be running -- configured to hold the platform
STILL at the spot it was spawned (see the command below), which also keeps
/platform/state consistent with the real Gazebo model. The hard-coded
platform_world_x/y is only used to cross-check that (a mismatch is warned
about, not silently ignored).

Reuses the existing pipeline unchanged: ResetManager publishes the position
setpoints, landing_controller (position mode) flies them, and /uav/state
provides feedback. Needs px4_bridge + landing_controller running (not
relative_state).

    ros2 run moving_platform moving_platform_node --ros-args \\
        -p center_x:=5.0 -p center_y:=0.0 -p radius:=0.0 -p angular_speed:=0.0

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
PLATFORM_TIMEOUT = 10.0    # [s] max wait for /platform/state


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

    start = time.time()
    while reset._platform_state is None:
        if time.time() - start > PLATFORM_TIMEOUT:
            log("No /platform/state received -- start moving_platform_node "
                "(static, see this file's docstring). Aborting.")
            rclpy.shutdown()
            return
        log("Waiting for /platform/state (is moving_platform_node running?)...")
        spin_for(1.0)

    # Refuse to fly at a target we can't trust. Give DDS discovery a moment so
    # a second publisher (typically a stale moving_platform_node from an
    # earlier run, still publishing its own trajectory on the same topic)
    # is actually counted before we decide.
    spin_for(1.0)
    plat = reset._platform_state
    problems = []
    n_publishers = node.count_publishers("/platform/state")
    if n_publishers > 1:
        problems.append(
            f"{n_publishers} nodes are publishing /platform/state (expected 1) -- almost "
            "certainly a stale moving_platform_node from an earlier run; kill it "
            "(pkill -f moving_platform_node) and start a single static one")
    if plat.vx != 0.0 or plat.vy != 0.0:
        problems.append(
            f"the platform is reported moving (v=({plat.vx:.2f}, {plat.vy:.2f}) m/s); start "
            "moving_platform_node with radius:=0.0 angular_speed:=0.0")
    if np.hypot(plat.x - sim.platform_world_x, plat.y - sim.platform_world_y) > 0.1:
        problems.append(
            f"/platform/state says ({plat.x:.2f}, {plat.y:.2f}) but the configured platform "
            f"location is ({sim.platform_world_x}, {sim.platform_world_y}) -- make the node's "
            "center_x/center_y (and the Gazebo spawn -x/-y) agree")
    if problems:
        for problem in problems:
            log(f"ABORTING, not taking off: {problem}.")
        node.destroy_node()
        rclpy.shutdown()
        return

    north, east = reset.platform_position_local(plat.x, plat.y)
    pose = {"x": float(north), "y": float(east), "z": float(sim.init_altitude)}
    log(f"Platform (Gazebo ENU) = ({plat.x:.2f}, {plat.y:.2f}) "
        f"-> PX4 local NED target = ({pose['x']:.2f}, {pose['y']:.2f}), hover {pose['z']} m")

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
