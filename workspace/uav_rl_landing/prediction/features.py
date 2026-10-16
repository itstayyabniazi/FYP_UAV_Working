"""
Turns the camera's noisy platform detections into the fixed-size input of the motion predictor, and the predictor's
output back into world coordinates. Pure numpy: the same code builds the training set and runs inside the mission.

Frame: a right-handed 2-D frame with x = EAST and y = NORTH (Gazebo ENU, the same as moving_platform.trajectories).
The mission's NED tracker must swap (north, east) -> (x=east, y=north) before calling in here: NED vs ENU is a
reflection, and a reflection turns a left turn into a right turn.

Why not feed raw positions: the network would learn where the arena is instead of how the platform moves. So
  * positions are taken relative to the NEWEST observation (the reference point `p_ref`),
  * and rotated into the platform's recent heading, so "ahead" is always +x. A left turn is then always +y.
The prediction is a displacement from p_ref at `H` seconds after the reference time, in that same frame.
"""
import math

import numpy as np

DT = 0.1             # [s] spacing of the resampled grid
L = 20               # grid length: 2 s of history
HEADING_WINDOW = 1.0  # [s] of the newest samples used to fit the heading
SCALE = 2.0          # [m] positions and targets are divided by this before the network (keeps values near 1)
MIN_VALID_BINS = 4   # fewer valid bins than this -> no prediction
MIN_SPEED = 0.05     # [m/s] below this the heading is noise; the frame stays aligned with the world axes
FEATURES = 3         # per step: dx, dy (scaled, rotated), valid-flag


def heading_of(ts, xs, ys):
    """Heading (rad) of the least-squares velocity over the newest HEADING_WINDOW seconds, or 0.0 if the platform
    is (nearly) still or there are too few samples."""
    ts, xs, ys = np.asarray(ts, float), np.asarray(xs, float), np.asarray(ys, float)
    keep = ts >= ts[-1] - HEADING_WINDOW
    if keep.sum() < 4 or ts[keep][-1] - ts[keep][0] < 0.4:
        return 0.0
    t = ts[keep] - ts[keep][-1]
    vx = np.polyfit(t, xs[keep], 1)[0]
    vy = np.polyfit(t, ys[keep], 1)[0]
    return math.atan2(vy, vx) if math.hypot(vx, vy) > MIN_SPEED else 0.0


def build_features(ts, xs, ys):
    """Detections (capture times, east, north) in time order -> (seq, theta0, p_ref, t_ref), or None if there is
    too little data.

    seq     (L, FEATURES) float32: per 0.1 s bin ending at the newest sample, the bin-mean position relative to the
            newest bin, rotated by -theta0 and divided by SCALE, plus a flag that is 0 where the bin had no sample
            (those are filled by interpolation so the network never sees a hole as a jump).
    theta0  heading used for the rotation.
    p_ref   (x, y) mean position of the newest bin, and t_ref its mean time: predictions are relative to these.
    """
    ts, xs, ys = np.asarray(ts, float), np.asarray(xs, float), np.asarray(ys, float)
    if ts.size < 3:
        return None
    t_end = ts[-1]
    idx = np.floor((t_end - ts) / DT + 1e-9).astype(int)          # 0 = newest bin
    keep = idx < L
    if not keep.any():
        return None
    bx = np.full(L, np.nan)
    by = np.full(L, np.nan)
    bt = np.full(L, np.nan)
    for k in range(L):
        sel = keep & (idx == k)
        if sel.any():
            j = L - 1 - k
            bx[j], by[j], bt[j] = xs[sel].mean(), ys[sel].mean(), ts[sel].mean()
    valid = ~np.isnan(bx)
    if valid.sum() < MIN_VALID_BINS or not valid[-1]:
        return None
    pos = np.arange(L)
    bx = np.interp(pos, pos[valid], bx[valid])                      # holes: straight line between neighbours
    by = np.interp(pos, pos[valid], by[valid])
    p_ref = (float(bx[-1]), float(by[-1]))
    t_ref = float(bt[-1])
    theta0 = heading_of(ts, xs, ys)
    c, s = math.cos(-theta0), math.sin(-theta0)
    rx, ry = bx - p_ref[0], by - p_ref[1]
    seq = np.stack([(c * rx - s * ry) / SCALE, (s * rx + c * ry) / SCALE, valid.astype(float)], axis=1)
    return seq.astype(np.float32), theta0, p_ref, t_ref


def to_frame(dx, dy, theta0):
    """World displacement -> network frame (rotated by -theta0, scaled)."""
    c, s = math.cos(-theta0), math.sin(-theta0)
    return (c * dx - s * dy) / SCALE, (s * dx + c * dy) / SCALE


def to_world(u, v, theta0):
    """Network-frame displacement (scaled) -> world displacement in metres."""
    c, s = math.cos(theta0), math.sin(theta0)
    return c * u * SCALE - s * v * SCALE, s * u * SCALE + c * v * SCALE
