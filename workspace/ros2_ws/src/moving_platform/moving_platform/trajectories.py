"""
Platform trajectories as pure functions of elapsed time (no ROS imports, so they
can be unit-tested anywhere). All in Gazebo world coordinates (ENU: x = east,
y = north); each returns (x, y, vx, vy).
"""
import math


def circular_state(t, center_x, center_y, radius, angular_speed):
    """Counter-clockwise circle; at t=0 the platform is at (center_x + radius, center_y)."""
    omega = angular_speed
    x = center_x + radius * math.cos(omega * t)
    y = center_y + radius * math.sin(omega * t)
    vx = -radius * omega * math.sin(omega * t)
    vy = radius * omega * math.cos(omega * t)
    return x, y, vx, vy


def linear_state(t, start_x, start_y, heading_deg, speed, travel_length):
    """Straight-line motion at constant speed from (start_x, start_y).

    heading_deg is the direction of travel measured counter-clockwise from east
    (+x): 0 = east, 90 = north, 180 = west.

    travel_length <= 0: one-way, forever. travel_length > 0: back and forth
    between the start and start + travel_length along the heading, reversing
    instantly at each end (constant speed, velocity flips sign).
    """
    ux = math.cos(math.radians(heading_deg))
    uy = math.sin(math.radians(heading_deg))
    if travel_length > 0.0 and speed > 0.0:
        along = speed * t
        cycle = 2.0 * travel_length
        m = along % cycle
        if m <= travel_length:
            distance, direction = m, 1.0
        else:
            distance, direction = cycle - m, -1.0
    else:
        distance, direction = speed * t, 1.0
    return (start_x + ux * distance, start_y + uy * distance,
            ux * speed * direction, uy * speed * direction)
