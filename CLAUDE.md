# Project Atlas — UAV landing on a moving platform

Final-year project: PX4 + ROS 2 Humble + Gazebo Harmonic, autonomous take-off → search by camera → lock onto a
moving platform → land on it. Real-hardware target: a moving car roof at **>= 5 km/h (1.39 m/s)**.
Full write-up and history: `README.md` (§3.3 is the Phase 3 moving-platform story).

## Layout
- `workspace/uav_rl_landing/mission/` — mission code. `moving_landing.py` (lock/track/touchdown loop),
  `target_tracker.py` (velocity fit, reversal detection, CTRV curvature), `vision_landing.py` (patrol, base class),
  `moving_landing_main.py` (linear, default gains), `circular_landing_main.py` (**motion-agnostic**, has `--fast`).
- `workspace/uav_rl_landing/prediction/` — Phase 4 LSTM-MDN motion predictor (features, datagen, train, numpy inference,
  evaluate, weights). Opt-in via `--mdn`; see its README. Training needs `~/venvs/atlas-ml` (torch); the mission needs only numpy.
- `workspace/uav_rl_landing/tests/` — offline harness (`fake_world.py`, `test_missions.py`). No ROS needed.
- `workspace/ros2_ws/src/moving_platform/` — platform node, `trajectories.py` (`circular_state`, `linear_state`,
  `random_state`), Gazebo models. `motion:=random` spawns at the arena centre (9.5, 6.0).
- `workspace/ros2_ws/src/vision_node/` — ArUco detector (DICT_4X4_50, id 0) and the launch recipes README.
- `workspace/scripts/run_sim_terminals.sh` — opens one terminal per sim node.

## Commands
- Offline suite: `cd workspace/uav_rl_landing && python3 -m tests.test_missions` (several minutes; timeout >= 540 s).
- Missions run from `workspace/uav_rl_landing` (the dir containing `mission/`), e.g.
  `python3 -m mission.circular_landing_main --start-platform --no-curvature --fast --camera-latency 0.09 --no-ground-truth --corners 0,0 0,9 52,9 52,0`
- Measure camera latency before trusting `--fast`: `python3 -m mission.measure_camera_latency`.
- `graphify update .` refreshes the code graph (free); doc changes need `/graphify --update`.

## Validated status (2026-10-14)
| Case | Evidence |
|---|---|
| Linear 0.3 m/s, default gains | real Gazebo |
| Linear 5 km/h, `--fast`, `travel_length=50` | real Gazebo (9 of 11 runs landed; 2 non-code failures) |
| Circular 0.45 / 0.8 / 1.0 m/s | real Gazebo |
| Circular 5 km/h | **not validated**: the old offline "10/10" used `error_to_estimate`; true offset median 1.69 m |
| Random motion, smooth, 0.3 m/s | real Gazebo, 2/2 landed |
| Random motion, smooth, 0.5 m/s, defaults | real Gazebo: landed slightly OFF the platform (offline true offset median 1.5 m) |
| Random motion, 0.5 m/s, `--kz 3.0` + curvature on (no `--no-curvature`) | real Gazebo, 5/5 on the platform, ground-truth offset 0.05–0.39 m |
| Random motion at 1.0 m/s, `--fast --kz 3.0` | real Gazebo, 3 landed: 0.29 / 1.22 / 0.69 m from centre (1 of 3 clearly on); slow lock + jiggle. `--window 1.0` is the offline-validated mitigation, not yet flown |
| Random motion, LSTM-MDN predictor (`--mdn`) | **offline only, not flown**: random 1.0 m/s `--fast` 78% within 0.45 m vs 33% for the tracker; circular and linear 5 km/h not regressed; 5 km/h on tight turns still ~33% |
| Random motion, hard zig-zag >= 0.5 m/s, or near 5 km/h | open problem (tracker estimate; perfect tracker lands 12/12) |

## Gotchas
- **Judge landings by the TRUE offset, not by the predicted-position line.** `error_to_estimate` and `Contact ... from the
  predicted platform position` only compare with the tracker's own prediction and read ~0.05 m even when the UAV lands
  metres off a TURNING platform (below ~1 m the marker is out of view). Offline use `summary["offset_at_contact"]`; in
  Gazebo keep ground truth on with `use_sim_time:=true` and read `Ground truth at that instant`.
- Trust the `Contact at ... from the predicted platform position` line. The final "touched down X m of
  /platform_state" line is unreliable (ground truth is wall-clock driven; RTF seen 58–149%).
- Use `--no-ground-truth` for demos: the first-detection check can false-abort with `ESTIMATE_MISMATCH` on long legs.
- Run `moving_platform_node` with `-p use_sim_time:=true` (bridge `/clock` first). Hypothesis, unconfirmed by a run.
- The "tracked platform speed is NN% of /platform/state's" RTF note misfires at low speed (fired in 26/40 offline runs
  at exactly RTF 1.0); read RTF from Gazebo instead.
- "On the platform" means more than the 0.75 m half-width: the drone's own body overhangs the edge, so judge ~0.45 m or
  better as fully on. `--fast` amplifies camera noise into command jitter (the visible jiggle); a longer `--window` helps.
- `TELEMETRY_STALLED` / PX4 mutex crashes are environmental Gazebo instability — restart the stack.
- `FakeWorld` is not PX4 physics. Flight-safety issues (e.g. `tracker_max_speed` vs `max_speed`) need real runs.
- One-way platform motion cannot be caught by the patrol (1.5 vs 1.39 m/s); use a long back-and-forth leg. Avoid
  `travel_length` 30/40 (reversal lands on touchdown timing). Widen `--corners` to `travel_length + 2`.
- The red cross on the platform is cosmetic; only the ArUco pattern is detected.

- **Real lock-on trouble is mostly the fixed camera tilting.** Real logs: every marker dropout at 17-27 deg of tilt (5 m x
  tan 24 deg = 2.2 m = the FOV half-width). `tests/fake_world.py` now has an opt-in tilt model (`max_accel=5.0, vel_tau=0.7`,
  calibrated to the real logs: ~80-90 s per mission, ~1.5-2 failed lock attempts) and a `gimbal=True` switch for a stabilised
  camera. Offline in that world: a gimbal cuts failed attempts ~60% (1.9 -> 0.8 per run) and mission time 90 -> 60 s.
  **Fixed-camera scenario that locks reliably (offline, tilt world): platform turn rate <= 0.6 rad/s** (`-p max_turn_rate:=0.6`;
  0 failed attempts, 31-36 s per mission at 0.8-1.0 m/s with `--fast --kz 3.0 --window 1.0`; turn rate 1.0 gives ~1.9 failed attempts,
  ~90 s). The platform's turn rate, not its speed, is what breaks the lock.
  Things that do NOT help (all tested): a flat command-acceleration cap (landed 1/36), a visibility-aware acceleration limit,
  lower/higher `kp`, other tracker windows, looser `align_*` tolerances.
- The MDN descent gate (`--mdn-gate`) did not help offline; keep it off. Use `--mdn-point peak` (the mixture mean fails on
  straight back-and-forth). The model is over-confident outside its training ranges.
- Retraining changes the weights: regenerate `prediction/weights/reference_v2.npz` or the torch-parity test fails.

## Conventions
- Stage files by name. Keep `workspace/rl_multi_rotor_landing` (submodule with unrelated edits) and
  `workspace/live_frame*.png` out of commits. Push only when asked.
- Validate offline with the user's real conditions before giving real-Gazebo commands; give every flag.
