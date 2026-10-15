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
| random 1.0 m/s, `--fast --kz 3.0`, n=60 | 32/60 within 0.75 m, 19/60 within 0.45 m, median 0.70 m | 56/60, 43/60, median 0.18 m |
| random 1.0 m/s, camera noise 0.2 m, n=48 | 16/48, 7/48, median 1.11 m | 32/48, 25/48, median 0.42 m |
| random 0.5 m/s, defaults + `--kz 3.0`, n=48 | 38/48, 20/48, median 0.46 m | 44/48, 37/48, median 0.24 m |
| random 5 km/h (1.39 m/s), turn rate 1.0, n=48 | 3/48, 1/48, median 2.68 m | 16/48, 12/48, median 1.14 m (**still mostly misses**) |
| circular 0.8 m/s, n=24 | 20/24, 13/24, median 0.42 m | 23/24 within 0.45 m, median 0.19 m |
| linear 5 km/h back-and-forth over 50 m, n=18 | 14/18, 5/18, median 0.58 m | 18/18 within 0.45 m, median 0.09 m |

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
