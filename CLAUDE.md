# Project Atlas — UAV landing on a moving platform

Final-year project: PX4 + ROS 2 Humble + Gazebo Harmonic, autonomous take-off → search by camera → lock onto a
moving platform → land on it. Real-hardware target: a moving car roof at **>= 5 km/h (1.39 m/s)**.
Full write-up and history: `README.md` (§3.3 is the Phase 3 moving-platform story).

## Layout
- `workspace/uav_rl_landing/mission/` — mission code. `moving_landing.py` (lock/track/touchdown loop),
  `target_tracker.py` (velocity fit, reversal detection, CTRV curvature), `vision_landing.py` (patrol, base class),
  `moving_landing_main.py` (linear, default gains), `circular_landing_main.py` (**motion-agnostic**, has `--fast`).
- `workspace/uav_rl_landing/tests/` — offline harness (`fake_world.py`, `test_missions.py`). No ROS needed.
- `workspace/ros2_ws/src/moving_platform/` — platform node, `trajectories.py`, Gazebo models.
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
| Circular 5 km/h | **offline only** — still to test |

## Gotchas
- Trust the `Contact at ... from the predicted platform position` line. The final "touched down X m of
  /platform_state" line is unreliable (ground truth is wall-clock driven; RTF seen 58–149%).
- Use `--no-ground-truth` for demos: the first-detection check can false-abort with `ESTIMATE_MISMATCH` on long legs.
- Run `moving_platform_node` with `-p use_sim_time:=true` (bridge `/clock` first). Hypothesis, unconfirmed by a run.
- `TELEMETRY_STALLED` / PX4 mutex crashes are environmental Gazebo instability — restart the stack.
- `FakeWorld` is not PX4 physics. Flight-safety issues (e.g. `tracker_max_speed` vs `max_speed`) need real runs.
- One-way platform motion cannot be caught by the patrol (1.5 vs 1.39 m/s); use a long back-and-forth leg. Avoid
  `travel_length` 30/40 (reversal lands on touchdown timing). Widen `--corners` to `travel_length + 2`.
- The red cross on the platform is cosmetic; only the ArUco pattern is detected.

## Conventions
- Stage files by name. Keep `workspace/rl_multi_rotor_landing` (submodule with unrelated edits) and
  `workspace/live_frame*.png` out of commits. Push only when asked.
- Validate offline with the user's real conditions before giving real-Gazebo commands; give every flag.
