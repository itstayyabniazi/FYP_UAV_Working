# Relative position (Platform - UAV)
float64 rel_x
float64 rel_y
float64 rel_z

# Relative velocity
float64 rel_vx
float64 rel_vy
float64 rel_vz

# UAV attitude
float64 roll
float64 pitch
float64 yaw

# Relative yaw (platform.yaw - uav.yaw, wrapped to [-pi, pi])
float64 rel_yaw

# Platform velocity
float64 platform_vx
float64 platform_vy
float64 platform_vz

# Distance to target
float64 distance

# Whether this observation's position/velocity comes from a currently-live
# reading of the platform. Ground truth (relative_state_node) is always
# "detected" by definition, so this is always true on the training path and
# only ever false on the vision path (vision_relative_state_node), when the
# ArUco marker has dropped out of the camera's view -- see termination.py's
# target-lost watchdog, which is the only consumer that actually branches on
# this (state_discretizer/reward don't need it).
bool detected
