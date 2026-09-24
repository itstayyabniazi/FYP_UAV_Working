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

Pure logic (numpy only), no ROS.
"""
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


class TargetTracker:

    def __init__(self, window=1.2, min_samples=8, min_span=0.5,
                 max_speed=3.0, max_extrapolation=6.0,
                 short_window=0.5, short_min_samples=6, change_threshold=0.3):
        self.window = window                  # [s] samples older than this (vs the newest) are dropped
        self.min_samples = min_samples
        self.min_span = min_span              # [s] the samples must cover at least this much time
        self.max_speed = max_speed            # [m/s] velocity estimates are clipped to this
        self.max_extrapolation = max_extrapolation  # [s] give up predicting past the last sample
        self.short_window = short_window      # [s] recent-motion window for change detection
        self.short_min_samples = short_min_samples
        self.change_threshold = change_threshold  # [m/s] short-vs-long velocity disagreement = a change
        self._samples = deque()               # (t, x, y)
        self._last_received = None
        self.changes_detected = 0

    def reset(self):
        self._samples.clear()
        self._last_received = None

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
        if np.hypot(short_vx - long_vx, short_vy - long_vy) > self.change_threshold:
            self._samples = deque(recent)
            self.changes_detected += 1

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
            return TargetState(ax + bx * age, ay + by * age, float(bx), float(by), True, n, age)

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
