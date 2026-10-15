"""
Platform trajectories as pure functions of elapsed time (no ROS imports, so they
can be unit-tested anywhere). All in Gazebo world coordinates (ENU: x = east,
y = north); each returns (x, y, vx, vy).
"""
import bisect
import math
import random


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


# ---------------------------------------------------------------------------------------------------
# Random motion: a chain of constant-speed segments, each a straight line or a circular arc, with the
# heading continuous across segments (only the TURN RATE steps, never the velocity direction), confined
# to an elliptical arena. Smooth and car-like: no instant reversals (those broke lock-on in the linear
# back-and-forth tests), and every segment has a closed-form integral so there is no drift.
# ---------------------------------------------------------------------------------------------------

_RANDOM_PATHS = {}


def _wrap(angle):
    return math.atan2(math.sin(angle), math.cos(angle))


def _advance(x0, y0, th0, w, v, tau):
    """Position and heading after tau seconds at speed v and constant turn rate w (rad/s, CCW positive)."""
    if abs(w) < 1e-9:
        return x0 + v * math.cos(th0) * tau, y0 + v * math.sin(th0) * tau, th0
    th = th0 + w * tau
    return (x0 + (v / w) * (math.sin(th) - math.sin(th0)),
            y0 - (v / w) * (math.cos(th) - math.cos(th0)), th)


class _RandomPath:
    EDGE = 0.7    # normalized arena radius beyond which segments steer back toward the centre
    LIMIT = 1.1   # normalized arena radius no segment is allowed to leave

    def __init__(self, cx, cy, hx, hy, speed, seed, max_turn_rate, seg_min, seg_max):
        self.cx, self.cy, self.hx, self.hy = cx, cy, hx, hy
        self.speed, self.max_turn_rate = speed, max_turn_rate
        self.seg_min, self.seg_max = seg_min, seg_max
        self.rng = random.Random(seed)
        self.x, self.y = cx, cy
        self.th = self.rng.uniform(-math.pi, math.pi)
        self.t_end = 0.0
        self.starts = []   # segment start times, for bisect
        self.segs = []     # (t0, x0, y0, th0, w, dur)

    def _radius(self, x, y):
        return math.hypot((x - self.cx) / self.hx, (y - self.cy) / self.hy)

    def _arc_inside(self, x, y, th, w, dur):
        steps = max(2, int(dur / 0.25))
        for i in range(1, steps + 1):
            px, py, _ = _advance(x, y, th, w, self.speed, dur * i / steps)
            if self._radius(px, py) > self.LIMIT:
                return False
        return True

    def _stays_inside(self, w, dur):
        """The segment stays in the arena AND ends somewhere the platform can still turn back toward the
        centre inside it -- otherwise a segment that ends at the edge pointing outward would leave."""
        if not self._arc_inside(self.x, self.y, self.th, w, dur):
            return False
        x, y, th = _advance(self.x, self.y, self.th, w, self.speed, dur)
        to_centre = _wrap(math.atan2(self.cy - y, self.cx - x) - th)
        turn = math.copysign(self.max_turn_rate, to_centre)
        return self._arc_inside(x, y, th, turn, min(abs(to_centre), math.pi) / self.max_turn_rate + 0.5)

    def _add_segment(self):
        rng, wmax = self.rng, self.max_turn_rate
        to_centre = _wrap(math.atan2(self.cy - self.y, self.cx - self.x) - self.th)
        steer_back = self._radius(self.x, self.y) > self.EDGE and abs(to_centre) > 0.25
        for attempt in range(8):
            dur = rng.uniform(self.seg_min, self.seg_max) * (0.7 ** attempt)
            if steer_back:
                w = math.copysign(wmax * rng.uniform(0.7, 1.0), to_centre)
            elif rng.random() < 0.35:
                w = 0.0
            else:
                w = rng.choice((-1.0, 1.0)) * wmax * rng.uniform(0.3, 1.0)
            if self._stays_inside(w, dur):
                break
        else:   # nothing fit: tightest turn toward the centre, briefly
            w, dur = math.copysign(wmax, to_centre), 1.0
        self.starts.append(self.t_end)
        self.segs.append((self.t_end, self.x, self.y, self.th, w, dur))
        self.x, self.y, self.th = _advance(self.x, self.y, self.th, w, self.speed, dur)
        self.t_end += dur

    def extend_to(self, t):
        while self.t_end <= t or not self.segs:
            self._add_segment()


def random_state(t, center_x, center_y, half_x, half_y, speed, seed,
                 max_turn_rate=0.6, seg_min=3.0, seg_max=8.0):
    """Random but smooth motion at constant `speed` inside the ellipse centred on (center_x, center_y) with
    half-axes half_x (east) and half_y (north); starts AT the centre, initial heading drawn from `seed`.

    The path is a seeded chain of segments, each a straight line (about a third of them) or an arc with
    turn rate up to `max_turn_rate` rad/s, lasting seg_min..seg_max seconds. Near the arena edge the next
    segment turns back toward the centre, and a segment is shortened until it stays inside. The minimum
    turning radius is speed / max_turn_rate, so keep the arena's smaller half-axis above ~2.5x that, or
    the platform cannot turn around inside it. Same `seed` and arguments give the same path.
    """
    if speed <= 0.0:
        return center_x, center_y, 0.0, 0.0
    key = (center_x, center_y, half_x, half_y, speed, seed, max_turn_rate, seg_min, seg_max)
    path = _RANDOM_PATHS.get(key)
    if path is None:
        if len(_RANDOM_PATHS) > 256:
            _RANDOM_PATHS.clear()
        path = _RANDOM_PATHS[key] = _RandomPath(*key)
    t = max(0.0, t)
    path.extend_to(t)
    t0, x0, y0, th0, w, _ = path.segs[bisect.bisect_right(path.starts, t) - 1]
    x, y, th = _advance(x0, y0, th0, w, speed, t - t0)
    return x, y, speed * math.cos(th), speed * math.sin(th)
