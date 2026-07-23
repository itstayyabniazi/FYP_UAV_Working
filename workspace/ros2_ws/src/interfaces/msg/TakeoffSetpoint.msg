# Target pose for landing_controller's position-hold mode, used during the
# reset/takeoff phase of an episode, before the RL agent's velocity-based
# LandingCommand takes over. x, y, z are in PX4's local NED frame (z down
# positive) -- see reset_manager.py for the altitude-AGL -> NED conversion.
float64 x
float64 y
float64 z

float64 yaw
