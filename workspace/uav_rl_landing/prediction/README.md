# prediction/ — LSTM-MDN platform-motion predictor (Phase 4)

**Status: offline only.** Nothing here has been flown in Gazebo. Results below are from `tests/fake_world.py`, which is
not PX4 physics. Off by default: without `--mdn` every mission behaves exactly as before.

## What it does and why

Below about 1 m the marker leaves the camera view, so the last 2-3.5 s of a landing fly a *prediction* of where the
platform is. The tracker predicts a straight line or a constant turn rate fitted to the last 0.6-1.2 s; on a randomly
turning platform that misses by up to a metre or two. This package replaces that prediction (only in the blind stretch,
only with `--mdn`) with a small LSTM whose head outputs a **mixture of K=5 bivariate Gaussians**: "50% it keeps going,
25% it turns left, 25% right" is something one Gaussian or a line cannot say.

| File | Role |
|---|---|
| `features.py` | detections -> network input: positions relative to the newest one, rotated into the platform's heading frame, 0.1 s bins over 2 s. Pure numpy, shared by training and the mission. **ENU in** (x east, y north); the lander swaps from NED. |
| `datagen.py` | unlimited synthetic tracks from `random_state` / `circular_state` / `linear_state` with camera noise 0.03-0.2 m, 10-30 Hz, dropouts, gaps, latency error. Regimes: `train`, `val` (other seeds), `heldout` (speed, turn rate and noise all outside the training ranges). |
| `train.py` | LSTM-MDN in torch (needs `~/venvs/atlas-ml`), fresh data every epoch, exports `weights/mdn_v2.npz`. |
| `mdn_numpy.py` | mission-time inference: pure numpy, no torch. Mixture mean, top-weight mode and densest point ("peak"), plus the whole mixture's spread. |
| `evaluate.py` | MDN vs constant-velocity and the tracker's CTRV on identical samples, with calibration. |
| `weights/` | `mdn_v2.npz` (shipped, 1 MB) and `reference_v2.npz` (torch outputs used by the torch-free parity test). |

## Results (all offline)

**Prediction error** (`python3 -m prediction.evaluate`), median / 90th percentile [m], validation regime, horizon 1.5-2.5 s,
which is the blind stretch:

| Motion | constant velocity (1.2 s) | tracker CTRV (1.2 s) | MDN mean | MDN top mode |
|---|---|---|---|---|
| random | 0.95 / 2.32 | 0.66 / 1.62 | **0.49 / 1.30** | 0.49 / 1.41 |
| circular | 1.36 / 2.71 | 0.93 / 1.73 | 0.47 / 1.20 | **0.38 / 1.18** |
| linear back-and-forth | **0.20 / 0.60** | 0.29 / 0.74 | 0.32 / 0.86 | 0.18 / 1.10 |

Calibration on the validation regime is good (the truth falls inside the predicted 50% / 90% region 49% / 90% of the
time). On the held-out ranges the model's errors are still lower than CTRV's, but it is **over-confident**
(5% / 56% coverage), so its reported spread must not be trusted outside the training ranges.

**Whole missions** (FakeWorld, camera noise 0.1 m, latency 0.09 s, judged on the TRUE offset at contact, identical seeds):

| Case | tracker | MDN (`peak`) |
|---|---|---|
| random 1.0 m/s, turn rate 0.6 rad/s, `--fast --kz 3.0`, n=60 | 32/60 within 0.75 m, 19/60 within 0.45 m, median 0.70 m | 56/60, 43/60, median 0.18 m |
| random 1.0 m/s, turn rate 0.6, camera noise 0.2 m, n=48 | 16/48, 7/48, median 1.11 m | 32/48, 25/48, median 0.42 m |
| random 0.5 m/s, turn rate 0.6, defaults + `--kz 3.0`, n=48 | 38/48, 20/48, median 0.46 m | 44/48, 37/48, median 0.24 m |
| random 5 km/h (1.39 m/s), turn rate 1.0, n=48 | 3/48, 1/48, median 2.68 m | 16/48, 12/48, median 1.14 m (**still mostly misses**) |
| random 1.0 m/s, **turn rate 1.0** (radius 1 m, the real-Gazebo launch), `--window 1.0`, noise 0.1 m, n=48 | 13/48, 8/48, median 1.15 m | 35/48, 27/48, median 0.37 m |
| same, camera noise 0.2 m, n=48 | 11/48, 7/48, median 1.75 m | 25/48, 13/48, median 0.66 m |
| circular 0.8 m/s, n=24 | 20/24, 13/24, median 0.42 m | 23/24 within 0.45 m, median 0.19 m |
| linear 5 km/h back-and-forth over 50 m, n=18 | 14/18, 5/18, median 0.58 m | 18/18 within 0.45 m, median 0.09 m |

## Real Gazebo so far

Launch for all runs: random platform, 1.0 m/s, turn rate 1.0, `--fast --kz 3.0 --window 1.0`, platform node on sim time.

| Date | Run | Result (ground truth at contact) |
|---|---|---|
| 2026-10-15 | 2x `--mdn` | `TELEMETRY_STALLED` (Gazebo ODE abort) while still at 5 m, before the predictor is used |
| 2026-10-15 | 3x no `--mdn` | 0.40 m, 1.56 m, timeout after about ten failed lock attempts |
| 2026-10-16 | `--mdn` | landed, **0.84 m** |
| 2026-10-16 | `--mdn` | `TELEMETRY_STALLED` at 3.5 m (Gazebo, MDN not yet active) |
| 2026-10-16 | `--mdn` | landed, **0.80 m** |
| 2026-10-16 | no `--mdn` | landed, 1.02 m |
| 2026-10-16/17 | 4x `--mdn` | landed, 0.88 / 0.17 / 0.77 / 0.33 m |
| 2026-10-16/17 | 2x no `--mdn` | landed, 0.45 / 0.61 m |

So far (same launch, turn rate 1.0): `--mdn` landings 0.17 / 0.33 / 0.77 / 0.80 / 0.84 / 0.88 m (median 0.79 m, n=6) against
tracker-only 0.40 / 0.45 / 0.61 / 1.02 / 1.56 m (median 0.61 m, n=5). **The MDN has not shown a benefit in real Gazebo**;
offline it was expected to have a median of 0.37 m against 1.15 m.

**Why (from the contact diagnostic, 4 `--mdn` runs):** the MDN's prediction was 0.27-0.43 m from the true platform centre
at contact (mean 0.36 m), the tracker's own extrapolation in the same runs 0.27-0.48 m (mean 0.36 m): equally good. The
offline tracker extrapolation error was about 1.5 m, so the real blind stretch is much shorter than the fake world's 2 s
(the real camera appears to keep the marker to a lower altitude), leaving the MDN little to improve. The other half of the
miss is the UAV not reaching its own target (0.08-0.42 m from the prediction at contact). The mission now also logs
`The marker was last detected N s before contact, at X m altitude` to measure the real blind stretch. Each run now logs
`Distance to the ground-truth platform centre at contact`: UAV, tracker extrapolation and MDN prediction, so one `--mdn`
run shows whether the predictor itself was right.

**Lock-on is the dominant real-world problem.** The tilt log (`Marker dropped out of view ... UAV tilt N deg`) shows the
marker leaving the image at 17-26 deg of tilt in every logged dropout (median ~23 deg), even at 0.2-1 m/s. At 5 m, 24 deg
of tilt swings the fixed downward camera's view by 5 m x tan(24 deg) = 2.2 m, about the whole half-width of the field
of view (2.25 m). The detector's position estimate is already tilt-corrected (`aruco_landing_target_node` rotates by
roll/pitch), so this is the marker physically leaving the image. The fake world has no attitude, so it cannot show it.

## Choices that matter

- **`--mdn-point peak` (default).** The mixture *mean* is best on turning paths but sits in the empty middle between
  "keeps going" and "reverses" on a back-and-forth platform (linear 5 km/h: 0/18 within 0.45 m). The top-weight mode is
  weaker on random paths. The densest point of the mixture was the one that never lost to the tracker on any of the
  three motion types.
- **The uncertainty gate does not help (negative result).** `--mdn-gate SIGMA` pauses the descent just above the blind
  floor while the predicted spread is large. Offline, thresholds that ever paused (1.0-1.15 m at 1 m/s) gave equal or
  worse landings and cost 10-15 s; looser ones never triggered (measured with the first, smaller model v1; not repeated with v2). Reason: at a fixed horizon the spread is mostly set by
  the platform's speed (correlation 0.83), because in our generator the *time* a turn begins is random. Kept as an
  experimental flag, off by default.
- Training data come from our own trajectory generator, so a real car's motion is a domain gap. The held-out regime
  tests extrapolation within the generator, not reality.

## Commands

```bash
# retrain (needs torch; ~20 min on the RTX 4050; defaults are the shipped recipe)
cd workspace/uav_rl_landing
~/venvs/atlas-ml/bin/python -m prediction.train --out prediction/weights/mdn_v2.npz
# evaluate vs the tracker (numpy only)
PYTHONPATH=../ros2_ws/src/moving_platform:. python3 -m prediction.evaluate
# fly it (real Gazebo, NOT yet validated): the usual Phase 3c command plus --mdn
python3 -m mission.circular_landing_main --start-platform --fast --kz 3.0 --window 1.0 --camera-latency 0.09 --mdn
```

If you retrain, regenerate `weights/reference_v2.npz` (torch outputs for a few inputs) or the parity test will fail.
