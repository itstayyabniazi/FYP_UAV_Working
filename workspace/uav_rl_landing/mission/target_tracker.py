"""
target_tracker.py

Estimates a moving marker's position AND velocity from the camera's stream of
absolute position samples (UAV position at detection time + the camera's
relative measurement), so the drone can lock onto a moving platform and match
its motion instead of chasing where it was.

Model: constant velocity over a short sliding window, fitted by least squares.
For a platform moving in a straight line this is exact; the noise of the slope
falls quickly with the window length (0.04 m sample noise, 1.2 s window at 30 Hz
=> about 0.02 m/s).

Change detection: after a reversal, turn or speed change, a long window keeps
averaging old and new motion for a full window length. So the newest 0.5 s of
samples are also fitted on their own (noisier, ~0.07 m/s); if that disagrees
with the long fit by more than `change_threshold`, the older samples are
dropped and the estimate follows the recent motion. This cuts the reaction time
to a reversal from ~1.5 s to ~0.6 s.

Curvature (opt-in, `curvature=True`): a platform moving on a curve (e.g. circular) turns its
velocity vector over time, so extrapolating the constant-velocity fit forward lags behind the
true path -- worst during a blind stretch with no fresh detections. When enabled, the tracker
also estimates the fitted velocity's own turn rate (low-pass filtered across calls to `update()`)
and extrapolates along a constant-turn-rate (CTRV) arc instead of a straight line. This is a
strict superset of the constant-velocity model: it reduces to the exact same straight-line
extrapolation as turn rate -> 0, so a straight-moving platform is unaffected. Off by default --
existing (linear-motion, hardware-validated) callers are unaffected either way.

Pure logic (numpy only), no ROS.
"""
import math
from collections import deque
from dataclasses import dataclass

import numpy as np


@dataclass
class TargetState:
    x: float               # estimated position NOW (extrapolated from the last fit)
    y: float
    vx: float              # estimated velocity (0 while velocity_valid is False)
    vy: float
    velocity_valid: bool   # enough samples over enough time to trust the slope
    samples: int           # samples in the fit window
    age: float             # [s] since the newest sample (0 = a detection just arrived)
    turn_rate: float = 0.0  # [rad/s] estimated turn rate used for this extrapolation (0 unless curvature=True)


class TargetTracker:

    def __init__(self, window=1.2, min_samples=8, min_span=0.5,
                 max_speed=3.0, max_extrapolation=6.0,
                 short_window=0.5, short_min_samples=6, change_threshold=0.3,
                 reversal_angle_threshold=100.0,
                 curvature=False, max_turn_rate=1.0, turn_rate_tau=0.5, min_turn_speed=0.05):
        self.window = window                  # [s] samples older than this (vs the newest) are dropped
        self.min_samples = min_samples
        self.min_span = min_span              # [s] the samples must cover at least this much time
        self.max_speed = max_speed            # [m/s] velocity estimates are clipped to this
        self.max_extrapolation = max_extrapolation  # [s] give up predicting past the last sample
        self.short_window = short_window      # [s] recent-motion window for change detection
        self.short_min_samples = short_min_samples
        self.change_threshold = change_threshold  # [m/s] short-vs-long velocity disagreement = a change
        # [deg] short-vs-long HEADING disagreement required, on top of change_threshold, to call it
        # a genuine reversal/change rather than ordinary curvature. Curvature turns the fitted
        # velocity vector steadily (a curving platform's short-window fit legitimately differs from
        # its long-window fit -- more so the faster it turns -- with no real "change" happening);
        # a reversal flips it abruptly. Magnitude alone can't tell those apart once the turn rate is
        # fast enough that curvature's own disagreement exceeds change_threshold (confirmed: 0 false
        # triggers/6.7s on a slow demo circle, 6 false triggers/6.7s on a fast one, before this).
        self.reversal_angle_threshold = math.radians(reversal_angle_threshold)
        self.curvature = curvature            # extrapolate along a turning arc instead of a straight line
        self.max_turn_rate = max_turn_rate    # [rad/s] clip a noisy/spurious turn-rate estimate to this
        self.turn_rate_tau = turn_rate_tau    # [s] low-pass time constant for the turn-rate estimate
        self.min_turn_speed = min_turn_speed  # [m/s] below this, a heading estimate is too noisy to trust
        self._samples = deque()               # (t, x, y)
        self._last_received = None
        self.changes_detected = 0
        self._prev_bx = self._prev_by = self._prev_slope_t = None  # last fitted velocity, for turn-rate
        self._turn_rate = 0.0
        self._turn_rate_valid = False

    def reset(self):
        self._samples.clear()
        self._last_received = None
        self._prev_bx = self._prev_by = self._prev_slope_t = None
        self._turn_rate = 0.0
        self._turn_rate_valid = False

    def update(self, t, x, y, received=None):
        """t = when the marker was SEEN (capture time); received = when the sample arrived (defaults to t).
        Freshness is judged on `received`: capture time is always older than that by the camera latency, so
        using it would make every sample look stale once the latency approaches the freshness limit."""
        self._last_received = t if received is None else received
        self._samples.append((t, x, y))
        # Keep only the last `window` seconds -- but never prune below min_samples: after a gap in detections
        # (marker briefly hidden, or the last metre of descent) the first few new samples must not erase the
        # good history and leave nothing to fit a velocity to. Ancient samples still go after 4 windows.
        cutoff = t - self.window
        hard_cutoff = t - 4.0 * self.window
        while self._samples and (self._samples[0][0] < hard_cutoff or
                                 (self._samples[0][0] < cutoff and len(self._samples) > self.min_samples)):
            self._samples.popleft()
        self._drop_old_motion_if_changed()
        self._update_turn_rate()

    @staticmethod
    def _slope(samples):
        t = np.array([s[0] for s in samples]) - samples[-1][0]
        bx = np.polyfit(t, [s[1] for s in samples], 1)[0]
        by = np.polyfit(t, [s[2] for s in samples], 1)[0]
        return bx, by

    def _drop_old_motion_if_changed(self):
        samples = list(self._samples)
        if len(samples) < self.min_samples:
            return
        t_last = samples[-1][0]
        recent = [x for x in samples if x[0] >= t_last - self.short_window]
        if (len(recent) < self.short_min_samples or len(recent) == len(samples)
                or recent[-1][0] - recent[0][0] < 0.6 * self.short_window):
            return
        long_vx, long_vy = self._slope(samples)
        short_vx, short_vy = self._slope(recent)
        mag_disagreement = np.hypot(short_vx - long_vx, short_vy - long_vy) > self.change_threshold
        # Require the HEADING to have actually flipped, not just moved -- see
        # reversal_angle_threshold's comment above. min_turn_speed reuses the same "too slow to
        # trust a heading" floor the turn-rate estimator uses, so a near-stationary platform's
        # noisy heading can't falsely read as a reversal either.
        long_speed, short_speed = math.hypot(long_vx, long_vy), math.hypot(short_vx, short_vy)
        if long_speed > self.min_turn_speed and short_speed > self.min_turn_speed:
            angle_disagreement = abs(math.atan2(short_vy, short_vx) - math.atan2(long_vy, long_vx))
            angle_disagreement = min(angle_disagreement, 2 * math.pi - angle_disagreement)
            is_reversal = angle_disagreement > self.reversal_angle_threshold
        else:
            is_reversal = True  # too slow to judge heading -- fall back to the old magnitude-only rule
        if mag_disagreement and is_reversal:
            self._samples = deque(recent)
            self.changes_detected += 1
            # A reversal/turn/speed change invalidates the old turn-rate estimate (it was fitted
            # across motion that no longer applies) -- fall back to the safe default (straight
            # line) until enough post-change samples have accumulated to re-estimate it.
            self._prev_bx = self._prev_by = self._prev_slope_t = None
            self._turn_rate = 0.0
            self._turn_rate_valid = False

    def _update_turn_rate(self):
        """Low-pass estimate of how fast the fitted velocity vector's HEADING is rotating
        (rad/s), from consecutive calls to this method. A no-op unless curvature=True. A platform
        moving in a straight line has a heading that doesn't rotate, so this settles near 0 and
        state()'s extrapolation below falls back to the plain constant-velocity line anyway --
        this only matters once the platform is genuinely turning."""
        if not self.curvature:
            return
        samples = list(self._samples)
        if len(samples) < self.min_samples:
            return
        t_last = samples[-1][0]
        bx, by = self._slope(samples)
        speed = math.hypot(bx, by)
        if (self._prev_bx is not None and speed > self.min_turn_speed
                and math.hypot(self._prev_bx, self._prev_by) > self.min_turn_speed):
            dt = t_last - self._prev_slope_t
            if dt > 0.02:                      # ignore back-to-back calls with ~no time elapsed
                dtheta = math.atan2(by, bx) - math.atan2(self._prev_by, self._prev_bx)
                dtheta = math.atan2(math.sin(dtheta), math.cos(dtheta))  # wrap to (-pi, pi]
                raw = max(-self.max_turn_rate, min(self.max_turn_rate, dtheta / dt))
                alpha = 1.0 - math.exp(-dt / self.turn_rate_tau)
                self._turn_rate = (1.0 - alpha) * self._turn_rate + alpha * raw
                self._turn_rate_valid = True
        self._prev_bx, self._prev_by, self._prev_slope_t = bx, by, t_last

    def has_data(self):
        return bool(self._samples)

    def last_sample_time(self):
        return self._samples[-1][0] if self._samples else None

    def fresh(self, now, max_age):
        """True if a sample ARRIVED within the last `max_age` seconds."""
        return bool(self._samples) and self._last_received is not None and now - self._last_received <= max_age

    def state(self, now):
        """The target's estimated state at time `now`, or None if there is no
        data or the newest sample is older than max_extrapolation."""
        if not self._samples:
            return None
        t_last = self._samples[-1][0]
        age = now - t_last
        if age > self.max_extrapolation:
            return None

        t = np.array([s[0] for s in self._samples]) - t_last   # <= 0, newest = 0
        px = np.array([s[1] for s in self._samples])
        py = np.array([s[2] for s in self._samples])
        n = len(t)
        span = float(t[-1] - t[0])

        if n >= self.min_samples and span >= self.min_span:
            bx, ax = np.polyfit(t, px, 1)
            by, ay = np.polyfit(t, py, 1)
            speed = float(np.hypot(bx, by))
            if speed > self.max_speed:
                bx, by = bx * self.max_speed / speed, by * self.max_speed / speed
            w = self._turn_rate if (self.curvature and self._turn_rate_valid) else 0.0
            if abs(w) > 1e-3 and age > 0.0:
                # Constant-turn-rate (CTRV) extrapolation: the fitted velocity vector's heading
                # rotates at the estimated constant rate w instead of staying fixed, so a curving
                # platform's predicted position follows the arc instead of the tangent line.
                # Exact for true circular motion; reduces to the line below as w -> 0.
                speed2 = math.hypot(bx, by)
                heading0 = math.atan2(by, bx)
                heading1 = heading0 + w * age
                px_now = ax + (speed2 / w) * (math.sin(heading1) - math.sin(heading0))
                py_now = ay - (speed2 / w) * (math.cos(heading1) - math.cos(heading0))
                vx_now, vy_now = speed2 * math.cos(heading1), speed2 * math.sin(heading1)
                return TargetState(px_now, py_now, vx_now, vy_now, True, n, age, w)
            return TargetState(ax + bx * age, ay + by * age, float(bx), float(by), True, n, age, 0.0)

        # Not enough history for a slope: position only, assume stationary.
        return TargetState(float(np.mean(px)), float(np.mean(py)), 0.0, 0.0, False, n, age)


class PositionHistory:
    """Recent UAV (t, x, y) samples, so a camera measurement can be combined with
    where the UAV WAS when the image was taken instead of where it is when the
    result arrives. Without this, marker_estimate = uav_now + measurement contains
    the UAV's own motion during the camera latency (about v_uav x latency), and
    feeding that back into a velocity controller can go unstable."""

    def __init__(self, maxlen=600):
        self._h = deque(maxlen=maxlen)

    def add(self, t, x, y):
        self._h.append((t, x, y))

    def at(self, t):
        """UAV position at time t (linear interpolation; clamped to the ends), or None if empty."""
        if not self._h:
            return None
        if t <= self._h[0][0]:
            return self._h[0][1], self._h[0][2]
        prev = None
        for entry in reversed(self._h):
            if entry[0] <= t:
                prev = entry
                break
            nxt = entry
        if prev is None:
            return self._h[0][1], self._h[0][2]
        if prev is self._h[-1]:
            return prev[1], prev[2]
        f = (t - prev[0]) / (nxt[0] - prev[0]) if nxt[0] > prev[0] else 0.0
        return prev[1] + f * (nxt[1] - prev[1]), prev[2] + f * (nxt[2] - prev[2])


def fit_camera_latency(samples):
    """Fit the camera latency from a flight over a STATIC marker.

    samples: (time, est_x, est_y, uav_vx, uav_vy), where est is the UNCOMPENSATED marker estimate (UAV position at
    receipt + measurement). Since the measurement is `latency` seconds old, est = marker + latency * uav_velocity, so
    the least-squares slope of est against velocity (means removed) is the latency.
    Returns (latency_s, r_squared, uav_velocity_std) or None if the UAV barely moved."""
    data = np.array(samples, dtype=float)
    vx, vy = data[:, 3], data[:, 4]
    est_x, est_y = data[:, 1], data[:, 2]
    v = np.concatenate([vx - vx.mean(), vy - vy.mean()])
    y = np.concatenate([est_x - est_x.mean(), est_y - est_y.mean()])
    if np.dot(v, v) < 1e-6:
        return None
    latency = float(np.dot(v, y) / np.dot(v, v))
    residual = y - latency * v
    r2 = 1.0 - float(np.dot(residual, residual) / np.dot(y, y)) if np.dot(y, y) > 0 else 0.0
    return latency, r2, float(np.std(np.concatenate([vx, vy])))
