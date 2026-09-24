"""
A fake drone + camera + platform implementing the `io` interface of
mission/vision_landing.py and mission/moving_landing.py, so the mission logic can
be tested without ROS, PX4 or Gazebo.

Kept deliberately simple but with the properties that matter:
  * drone: first-order lag toward the position setpoint (tau 0.7 s) in position
    mode, toward the velocity command (tau 0.5 s) in velocity mode; AUTO.LAND
    brakes horizontally (tau 0.3 s) and sinks at 0.5 m/s
  * camera: 30 Hz, only sees the marker if it is fully inside the USABLE
    footprint (rotor arms/props block the outer ~130 px east-west), between
    0.7 m and 7 m altitude, with 0.04 m noise and a true latency of 0.4 s (as seen
    in Gazebo). The estimate combines the measurement with the UAV position at
    (receipt - assumed_latency), like ros_io; assumed_latency=0 is the
    uncompensated version that failed in the first Gazebo run
  * platform: any function t -> (x_east, y_north, v_east, v_north) in Gazebo ENU
    (e.g. moving_platform.trajectories.linear_state), converted to NED here
"""
import math
import random
from collections import deque


class FakeWorld:

    def __init__(self, platform_fn, start_after_airborne=False, dropout=None, flip_north=False,
                 latency=0.4, assumed_latency=0.35, noise=0.04, seed=1, uav_start=(0.0, 0.0)):
        random.seed(seed)
        self.platform_fn = platform_fn
        self.platform_started_at = None if start_after_airborne else 0.0
        self.dropout, self.flip_north = dropout, flip_north
        # `latency` is the TRUE camera->result delay; `assumed_latency` is what the mission is configured with
        # (ros_io.camera_latency). 0.0 = uncompensated, which is what broke the first Gazebo run.
        self.latency, self.assumed_latency, self.noise = latency, assumed_latency, noise
        self.t = 0.0
        self.p = [uav_start[0], uav_start[1], 0.0]      # north, east, altitude
        self.v = [0.0, 0.0, 0.0]
        self.mode = "position"
        self.sp = list(self.p)
        self.cmd = [0.0, 0.0, 0.0]                       # north, east, DOWN
        self.landing = False
        self.detections = deque(maxlen=400)              # (t, est_n, est_e, rel_n, rel_e, alt)
        self.pending = []
        self.history = deque(maxlen=200)                 # (t, n, e, alt)
        self.velocity_commands = 0

    # -- platform ---------------------------------------------------------

    def platform_ned(self, t):
        """(north, east, v_north, v_east) at world time t."""
        if self.platform_started_at is None or t < self.platform_started_at:
            x, y, _, _ = self.platform_fn(0.0)
            return y, x, 0.0, 0.0
        x, y, vx, vy = self.platform_fn(t - self.platform_started_at)
        return y, x, vy, vx

    # -- io: time / state ---------------------------------------------------

    def now(self):
        return self.t

    def uav_position(self):
        return tuple(self.p)

    def uav_velocity(self):
        return (self.v[0], self.v[1], -self.v[2])       # NED: down positive

    def start(self, x, y, a):
        self.mode, self.sp = "position", [x, y, a]

    def command(self, x, y, a):
        self.sp = [x, y, a]

    def enter_velocity_mode(self):
        self.mode = "velocity"
        self.cmd = [0.0, 0.0, 0.0]

    def command_velocity(self, n, e, d):
        assert self.mode == "velocity", "velocity command while not in velocity mode"
        self.cmd = [n, e, d]
        self.velocity_commands += 1

    def start_platform(self):
        if self.platform_started_at is None:
            self.platform_started_at = self.t

    def land(self):
        self.landing = True

    def wait_landed(self, timeout):
        while self.p[2] > 0.0:
            self.sleep(0.1)
        return tuple(self.p)

    def platform_truth(self):
        n, e, vn, ve = self.platform_ned(self.t)
        return (n, e, vn, ve)

    # -- io: vision -----------------------------------------------------------

    def confirmed(self, count, window):
        return sum(1 for d in self.detections if self.t - d[0] <= window) >= count

    def estimate(self):
        recent = [d for d in self.detections if self.t - d[0] <= 0.5][-5:]
        if not recent:
            return None
        return (sum(d[1] for d in recent) / len(recent), sum(d[2] for d in recent) / len(recent))

    def relative_measurement(self, window):
        recent = [d for d in self.detections if self.t - d[0] <= window]
        if not recent:
            return None
        n = len(recent)
        return (sum(d[3] for d in recent) / n, sum(d[4] for d in recent) / n,
                sum(d[5] for d in recent) / n, n)

    def drain_samples(self):
        out, self.pending = self.pending, []
        return out

    # -- simulation step ---------------------------------------------------------

    def sleep(self, dt):
        substeps = 10
        h = dt / substeps
        for _ in range(substeps):
            self._advance(h)

    def _advance(self, h):
        self.t += h
        old = list(self.p)
        if self.landing:
            for i in (0, 1):
                self.v[i] += (0.0 - self.v[i]) * min(1.0, h / 0.3)
                self.p[i] += self.v[i] * h
            self.p[2] = max(0.0, self.p[2] - 0.5 * h)
            self.v[2] = -0.5 if self.p[2] > 0.0 else 0.0
        elif self.mode == "position":
            # Altitude climbs much slower than a real PX4 vehicle's horizontal repositioning -- a first
            # version of this fake world used one 0.7 s time constant for all three axes, reaching 5 m in
            # ~2 s, when a real Gazebo takeoff took ~9 s (see the "Airborne" timestamp in an actual log).
            # That let an earlier offline test pass while a platform designed against it was, in the real
            # timing, already gone by the time the patrol got anywhere -- tuned from that real log (tau
            # solved so error < 0.3 m at t = 9 s from a 5 m climb).
            for i in (0, 1):
                k = min(1.0, h / 0.7)
                self.p[i] += (self.sp[i] - self.p[i]) * k
                self.v[i] = (self.p[i] - old[i]) / h
            kz = min(1.0, h / 3.2)
            self.p[2] += (self.sp[2] - self.p[2]) * kz
            self.v[2] = (self.p[2] - old[2]) / h
        else:
            k = min(1.0, h / 0.5)
            target = [self.cmd[0], self.cmd[1], -self.cmd[2]]   # altitude rate is up-positive
            for i in range(3):
                self.v[i] += (target[i] - self.v[i]) * k
                self.p[i] += self.v[i] * h
            if self.p[2] <= 0.0:                      # resting on the platform: no further descent
                self.p[2] = 0.0
                self.v[2] = max(0.0, self.v[2])
        self.history.append((self.t, *self.p))
        if int(self.t * 30) != int((self.t - h) * 30):
            self._camera()

    def _uav_at(self, t):
        for entry in reversed(self.history):
            if entry[0] <= t:
                return entry[1:]
        return tuple(self.p)

    def _camera(self):
        if self.dropout and self.dropout[0] <= self.t <= self.dropout[1]:
            return
        tc = self.t - self.latency
        un, ue, ualt = self._uav_at(tc)
        pn, pe, _, _ = self.platform_ned(tc)
        dn, de = pn - un, pe - ue
        if not (0.7 < ualt <= 7.0 and abs(dn) <= 0.63 * ualt - 0.25 and abs(de) <= 0.50 * ualt - 0.25):
            return
        rel_n = (-dn if self.flip_north else dn) + random.gauss(0, self.noise)
        rel_e = de + random.gauss(0, self.noise)
        # Like ros_io: combine the measurement with the UAV position at the ASSUMED capture time.
        captured = self.t - self.assumed_latency
        un_a, ue_a, _ = self._uav_at(captured)
        est_n, est_e = un_a + rel_n, ue_a + rel_e
        self.detections.append((self.t, est_n, est_e, rel_n, rel_e, ualt))
        self.pending.append((captured, est_n, est_e, self.t))
