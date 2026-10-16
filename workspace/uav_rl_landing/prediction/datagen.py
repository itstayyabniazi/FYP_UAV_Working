"""
Synthetic training / evaluation data for the platform-motion predictor.

A sample is what the drone has at the moment it stops seeing the marker: the last ~2 s of NOISY, delayed, patchy
detections, plus a horizon H (how far into the future we want the position), and the truth to learn: where the
platform actually is H seconds after the newest observation, as a displacement in the heading-aligned frame
(see features.py).

Motion families (all from moving_platform.trajectories, the same code the Gazebo platform node runs):
  random    smooth chain of straight/arc segments (random_state) -- the case the predictor is for
  circular  constant turn rate (circular_state)                   -- validated before, must not regress
  linear    back and forth at constant speed (linear_state)       -- validated before, must not regress

Regimes:
  train / val   the same parameter ranges, DIFFERENT seeds
  heldout       speed, turn rate and noise all OUTSIDE the training ranges (extrapolation test)

Run `python3 -m prediction.datagen` for a quick self-check (no torch needed).
"""
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "ros2_ws", "src", "moving_platform"))
from moving_platform import trajectories as traj  # noqa: E402
from moving_platform.trajectories import circular_state, linear_state, random_state  # noqa: E402

from prediction.features import SCALE, build_features, to_frame  # noqa: E402

FAMILIES = ("random", "circular", "linear")
REGIMES = {
    #            speed [m/s]   turn [rad/s]  noise [m]
    "train":   dict(speed=(0.2, 1.4), turn=(0.3, 1.2), noise=(0.03, 0.20)),
    "val":     dict(speed=(0.2, 1.4), turn=(0.3, 1.2), noise=(0.03, 0.20)),
    "heldout": dict(speed=(1.4, 1.8), turn=(1.2, 1.8), noise=(0.20, 0.30)),
}
SEED_BASE = {"train": 0, "val": 10_000_000, "heldout": 20_000_000}
H_RANGE = (0.3, 4.0)       # [s] prediction horizons
HISTORY = 2.6              # [s] of detections generated before the cut (the feature window is 2 s)
CUTS_PER_TRACK = 3
HORIZONS_PER_CUT = 3


def make_track(rng, family, regime, ranges=None):
    """One platform track: returns (truth_fn(t) -> (x, y), speed, noise, info). `ranges` overrides REGIMES[regime]
    entries (e.g. fixed speed) for targeted evaluation."""
    r = dict(REGIMES[regime])
    r.update(ranges or {})
    speed = rng.uniform(*r["speed"])
    noise = rng.uniform(*r["noise"])
    if family == "random":
        turn = rng.uniform(*r["turn"])
        seg_min = rng.uniform(1.0, 4.0)
        seg_max = seg_min + rng.uniform(1.0, 5.0)
        min_half = 2.5 * speed / turn                           # the arena must be able to turn the platform around
        if rng.random() < 0.5:                                  # mission-like arena (the Gazebo demo one, widened if needed)
            cx, cy = 9.5, 6.0
            hx, hy = max(rng.uniform(1.5, 3.0), min_half), max(rng.uniform(5.0, 7.0), min_half)
        else:
            cx, cy = rng.uniform(-20, 20), rng.uniform(-20, 20)
            hx = hy = min_half + rng.uniform(2.0, 30.0)
        seed = int(rng.integers(0, 2**31))

        def truth(t):
            x, y, _, _ = random_state(t, cx, cy, hx, hy, speed, seed, turn, seg_min, seg_max)
            return x, y
        return truth, speed, noise, dict(turn=turn)
    if family == "circular":
        omega_max = rng.uniform(*r["turn"])
        radius = max(speed / omega_max, 1.0)
        omega = (speed / radius) * rng.choice([-1.0, 1.0])
        cx, cy = rng.uniform(-10, 10), rng.uniform(-10, 10)

        def truth(t):
            x, y, _, _ = circular_state(t, cx, cy, radius, omega)
            return x, y
        return truth, speed, noise, dict(turn=abs(omega))
    sx, sy = rng.uniform(-10, 10), rng.uniform(-10, 10)
    heading = rng.uniform(0, 360)
    length = rng.uniform(20.0, 50.0)

    def truth(t):
        x, y, _, _ = linear_state(t, sx, sy, heading, speed, length)
        return x, y
    return truth, speed, noise, dict(turn=0.0)


def observe(rng, truth, t_cut, noise):
    """The detections the drone would hold at t_cut: arrays (ts, xs, ys), oldest first, or None. Mimics the real
    pipeline: 10-30 Hz, random dropouts, sometimes a gap, sometimes a short history (platform just acquired), a
    small residual camera-latency error, and Gaussian noise."""
    rate = rng.choice([10.0, 15.0, 30.0])
    span = HISTORY if rng.random() > 0.1 else rng.uniform(0.8, HISTORY)
    ts = t_cut - np.arange(int(span * rate) + 1) / rate
    keep = rng.random(ts.size) > rng.uniform(0.0, 0.3)
    keep[0] = True                                              # the newest sample is the one we cut at
    if rng.random() < 0.2:
        g0 = rng.uniform(0.3, span - 0.5)
        keep &= ~((ts < t_cut - g0) & (ts > t_cut - g0 - rng.uniform(0.3, 0.8)))
    ts = ts[keep][::-1]
    if ts.size < 4:
        return None
    delta = rng.uniform(-0.05, 0.05)                            # residual camera-latency error
    pts = np.array([truth(t + delta) for t in ts])
    return ts, pts[:, 0] + rng.normal(0, noise, ts.size), pts[:, 1] + rng.normal(0, noise, ts.size)


def _chunk(args):
    n_tracks, seed, regime, family_p, ranges, keep_raw = args
    rng = np.random.default_rng(seed)
    traj._RANDOM_PATHS.clear()
    out = dict(seq=[], H=[], y=[], theta=[], family=[], speed=[], noise=[], turn=[], raw=[], p_ref=[], t_ref=[])
    for _ in range(n_tracks):
        family = FAMILIES[rng.choice(len(FAMILIES), p=family_p)]
        truth, speed, noise, info = make_track(rng, family, regime, ranges)
        for _ in range(CUTS_PER_TRACK):
            t_cut = rng.uniform(8.0, 90.0)
            obs = observe(rng, truth, t_cut, noise)
            feats = build_features(*obs) if obs else None
            if feats is None:
                continue
            seq, theta0, p_ref, t_ref = feats
            for _ in range(HORIZONS_PER_CUT):
                H = rng.uniform(*H_RANGE)
                fx, fy = truth(t_ref + H)
                u, v = to_frame(fx - p_ref[0], fy - p_ref[1], theta0)
                out["seq"].append(seq)
                out["H"].append(H)
                out["y"].append((u, v))
                out["theta"].append(theta0)
                out["family"].append(FAMILIES.index(family))
                out["speed"].append(speed)
                out["noise"].append(noise)
                out["turn"].append(info["turn"])
                out["p_ref"].append(p_ref)
                out["t_ref"].append(t_ref)
                if keep_raw:
                    out["raw"].append(obs)
    return out


def make_dataset(n_tracks, regime="train", seed=0, family_p=(0.6, 0.2, 0.2), ranges=None, workers=None, keep_raw=False):
    """About n_tracks * CUTS_PER_TRACK * HORIZONS_PER_CUT samples as a dict of numpy arrays (seq, H, y, theta, family,
    speed, noise, turn; plus `raw` when keep_raw). Deterministic for a given (n_tracks, regime, seed, ranges)."""
    workers = workers or min(16, os.cpu_count() or 1)
    per = max(1, math.ceil(n_tracks / (workers * 4)))
    jobs, left, k = [], n_tracks, 0
    while left > 0:
        m = min(per, left)
        jobs.append((m, SEED_BASE[regime] + seed * 1000 + k, regime, family_p, ranges, keep_raw))
        left -= m
        k += 1
    if workers == 1 or len(jobs) == 1:
        chunks = [_chunk(j) for j in jobs]
    else:
        with ProcessPoolExecutor(workers) as pool:
            chunks = list(pool.map(_chunk, jobs))
    data = {}
    for key in chunks[0]:
        if key == "raw":
            data[key] = [item for c in chunks for item in c[key]]
        else:
            data[key] = np.concatenate([np.asarray(c[key]) for c in chunks if len(c[key])], axis=0)
    for key in ("seq", "H", "y", "theta"):
        data[key] = data[key].astype(np.float32)
    return data


if __name__ == "__main__":
    import time
    t0 = time.time()
    d = make_dataset(300, "val", seed=1, workers=1)
    print(f"{len(d['H'])} samples in {time.time() - t0:.1f} s; seq {d['seq'].shape}, y {d['y'].shape}")
    a = make_dataset(40, "train", seed=3, workers=1)
    b = make_dataset(40, "train", seed=3, workers=1)
    print("deterministic:", np.array_equal(a["seq"], b["seq"]) and np.array_equal(a["y"], b["y"]))
    # In the heading frame a straight-moving platform is predicted by speed*H along +x: check the target scale.
    for fam in range(3):
        sel = d["family"] == fam
        disp = np.hypot(d["y"][sel, 0], d["y"][sel, 1]) * SCALE
        print(f"  {FAMILIES[fam]:8s} n={sel.sum():4d}  displacement median {np.median(disp):.2f} m  "
              f"(speed*H median {np.median(d['speed'][sel] * d['H'][sel]):.2f} m)")
