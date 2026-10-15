"""
Offline evaluation of platform-motion predictors on identical synthetic samples (prediction/datagen.py).

Baselines run the mission's real TargetTracker on the same noisy detections:
  cv    constant velocity   (tracker, curvature off, the --fast window 0.6 s and the default 1.2 s)
  ctrv  constant turn rate  (tracker, curvature on)
The learned model is added by train.py / this file's `main` once weights exist.

    cd workspace/uav_rl_landing && python3 -m prediction.evaluate            # baselines only (no torch)
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from mission.target_tracker import TargetTracker  # noqa: E402
from prediction.datagen import FAMILIES, make_dataset  # noqa: E402
from prediction.features import SCALE, to_world  # noqa: E402

BASELINES = {
    "cv  w1.2":  dict(window=1.2, curvature=False),
    "cv  w0.6":  dict(window=0.6, curvature=False),
    "ctrv w1.2": dict(window=1.2, curvature=True),
    "ctrv w0.6": dict(window=0.6, curvature=True),
}


def baseline_prediction(raw, t_ref, H, **kw):
    """Predicted displacement (world metres) of the tracker at t_ref+H, relative to the last-bin mean position it is
    scored against is done by the caller; this returns the absolute predicted (x, y)."""
    ts, xs, ys = raw
    tr = TargetTracker(window=kw["window"], curvature=kw["curvature"], max_speed=3.0, max_extrapolation=10.0)
    for t, x, y in zip(ts, xs, ys):
        tr.update(float(t), float(x), float(y))
    st = tr.state(t_ref + H)
    return None if st is None else (st.x, st.y)


def baseline_errors(data, name):
    """Euclidean error [m] of baseline `name` per sample (nan where the tracker had no estimate)."""
    kw = BASELINES[name]
    err = np.full(len(data["H"]), np.nan)
    for i, raw in enumerate(data["raw"]):
        pred = baseline_prediction(raw, data["t_ref"][i], float(data["H"][i]), **kw)
        if pred is None:
            continue
        # truth = p_ref + world displacement of the target
        dx, dy = to_world(float(data["y"][i, 0]), float(data["y"][i, 1]), float(data["theta"][i]))
        tx, ty = data["p_ref"][i][0] + dx, data["p_ref"][i][1] + dy
        err[i] = np.hypot(pred[0] - tx, pred[1] - ty)
    return err


def table(title, data, columns):
    """columns: {name: error array}. Prints median / 90th percentile by family and horizon band."""
    print(f"\n{title}  ({len(data['H'])} samples)")
    bands = [(0.3, 1.5), (1.5, 2.5), (2.5, 4.0)]
    print(f"  {'':10s}{'':14s}" + "".join(f"{n:>16s}" for n in columns))
    for fam in range(len(FAMILIES)):
        for lo, hi in bands:
            sel = (data["family"] == fam) & (data["H"] >= lo) & (data["H"] < hi)
            if not sel.any():
                continue
            cells = []
            for e in columns.values():
                v = e[sel]
                v = v[~np.isnan(v)]
                cells.append(f"{np.median(v):5.2f} / {np.percentile(v, 90):5.2f}" if v.size else "      -")
            print(f"  {FAMILIES[fam]:10s}H {lo:.1f}-{hi:.1f} s   " + "".join(f"{c:>16s}" for c in cells))


def mdn_outputs(data, predictor, draws=256, seed=0):
    """Run the numpy MDN on every sample. Returns (err_mean, err_best, spread, u) per sample, all in metres except u:
    err_mean/err_best  error of the mixture mean / of the highest-weight mode
    spread             sqrt(trace(total covariance))
    u                  calibration score: the fraction of draws from the predicted mixture that lie closer to the
                       mixture mean than the truth does. A calibrated model gives u ~ Uniform(0, 1)."""
    from prediction.mdn_numpy import mixture_stats
    rng = np.random.default_rng(seed)
    n = len(data["H"])
    err_mean, err_best, spread, u = (np.empty(n) for _ in range(4))
    for i in range(n):
        pi, mu, sg, rho = predictor.forward(data["seq"][i], float(data["H"][i]))
        mean, cov = mixture_stats(pi, mu, sg, rho)
        y = data["y"][i].astype(float)
        err_mean[i] = SCALE * np.hypot(*(mean - y))
        err_best[i] = SCALE * np.hypot(*(mu[int(np.argmax(pi))] - y))
        spread[i] = SCALE * np.sqrt(np.trace(cov))
        k = rng.choice(len(pi), size=draws, p=pi)
        z1, z2 = rng.standard_normal(draws), rng.standard_normal(draws)
        dx = mu[k, 0] + sg[k, 0] * z1
        dy = mu[k, 1] + sg[k, 1] * (rho[k] * z1 + np.sqrt(1 - rho[k] ** 2) * z2)
        u[i] = np.mean(np.hypot(dx - mean[0], dy - mean[1]) <= np.hypot(*(mean - y)))
    return err_mean, err_best, spread, u


def calibration_report(title, data, err, spread, u):
    print(f"\n{title}")
    print(f"  coverage (a calibrated model gives 0.50 / 0.90): "
          f"truth inside the predicted 50% region {np.mean(u <= 0.5):.2f}, 90% region {np.mean(u <= 0.9):.2f}")
    ranks = lambda a: np.argsort(np.argsort(a))
    print(f"  rank correlation of predicted spread vs actual error: {np.corrcoef(ranks(spread), ranks(err))[0, 1]:.2f} "
          "(0 = spread says nothing, 1 = perfect)")
    order = np.argsort(spread)
    third = len(order) // 3
    for name, sel in (("most confident third", order[:third]), ("middle third", order[third:2 * third]),
                      ("least confident third", order[2 * third:])):
        print(f"  {name:22s} spread {np.median(spread[sel]):5.2f} m -> median error {np.median(err[sel]):5.2f} m, "
              f"90th pct {np.percentile(err[sel], 90):5.2f} m")


def main():
    weights = os.path.join(os.path.dirname(__file__), "weights", "mdn_v2.npz")
    predictor = None
    if os.path.exists(weights):
        from prediction.mdn_numpy import MDNPredictor
        predictor = MDNPredictor.load(weights)
    for regime, n in (("val", 400), ("heldout", 300)):
        data = make_dataset(n, regime, seed=7, keep_raw=True)
        cols = {name: baseline_errors(data, name) for name in BASELINES}
        if predictor is not None:
            em, eb, spread, u = mdn_outputs(data, predictor)
            cols["MDN mean"], cols["MDN best mode"] = em, eb
        table(f"regime={regime}: median / 90th-percentile position error [m]", data, cols)
        if predictor is not None:
            calibration_report(f"MDN calibration, regime={regime}", data, em, spread, u)


if __name__ == "__main__":
    main()
