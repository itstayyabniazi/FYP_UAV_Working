# Graph Report - FYP_UAV  (2026-10-15)

## Corpus Check
- 188 files · ~111,318 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 380 file(s) not represented in the graph (top: .msg 275, .launch 34, (none) 21)

## Summary
- 1650 nodes · 2641 edges · 180 communities (106 shown, 74 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 101 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7fd8b07e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- compute_observation_action_msg
- RosMissionIO
- CascadedPIDData
- extract_topics_from_rosbag.py
- LandingSimulationEnv
- Parameters
- AnalysisNode
- rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_multiresolution.py
- ExplorationManager
- Vicon Launch Scripts
- Platform Trajectory Generator
- MovingPlatformLander
- train.py
- px4_msgs Contributing guide and release process
- LogTraining
- os
- ResetManager
- math
- FakeWorld
- test_missions.py
- RewardManager
- ArucoLandingTargetNode
- LandingSimulationObject
- ViconInterface
- ros_io.py
- ViconDebug
- rl_multi_rotor_landing repository (paper code)
- TargetTracker
- SmoothPlatformData
- compute_landing_simulation_object_state_msg
- Moving-platform landing mission (lock / track / touchdown)
- write_data_to_csv
- grid_utils.py
- ament_flake8_main
- ament_pep257_main
- test_marker_detection.py
- TargetTracker
- CascadedPIDInterface
- interfaces ament package
- LandingController
- MovingPlatformNode
- landing_env.py
- patch_x500_camera.py
- rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/parameters.py
- rl_multi_rotor_landing_sim/src/training_q_learning/src/training_q_learning/parameters.py
- config/parameters.py
- LandingEnv
- numpy
- StateDiscretizer
- Linear 5 km/h with --fast and travel_length=50
- Project Atlas (README)
- .save_training_data
- state_publisher.cpp
- moving_platform_node
- generate_changelog.sh
- ActionToUavPose
- Gotchas (RTF, ground truth, FakeWorld limits, travel_length)
- MDNPredictor
- setuptools
- plot_topic_freq_from_flight.py
- _RandomPath
- RelativeStateNode
- pytest
- publish_stability_axes.py
- RelativeStateNode
- VisionRelativeStateNode
- training_q_learning catkin package (simulation)
- UAVPoseFromStateEstimate
- process_action
- world_base_link_transform_publisher.py
- run_sim_terminals.sh
- compute_observation_action_msg
- TrackLandingTrial
- ObservationRelativeState
- FlightActivated
- publish_vmp_x.sh
- publish_vmp_y.sh
- launch_action_interface.sh
- launch_analysis_node_2D.sh
- launch_cascaded_pid_environment_in_virtual_screens.sh
- launch_cascaded_pid_interface.sh
- launch_compute_relative_information.sh
- launch_environment_in_virtual_screens.sh
- launch_landing_simulation.sh
- launch_observation_generator.sh
- launch_publish_stability_axes.sh
- launch_test_model_2D.sh
- launch_training.sh
- moving_platform_description catkin package
- generate_release_notes.sh
- catkin_pkg_python_setup
- execute_training_curriculum_for_one_sim_one_exp.py
- rl_multi_rotor_landing_gcs/other_files/setup.bash
- vicon_publish_stability_axes.py
- publish_roll_pitch_yawrate_thrust_msg
- .check_done_criteria
- clear_all_sims.sh script
- rl_multi_rotor_landing_sim/other_files/setup.bash
- main
- q_learning.py
- test_copyright
- test_copyright
- moving_platform_node.py
- test_copyright
- test_copyright
- CascadedPIDData
- CascadedPIDInterface
- fyp-uav docker compose service
- pre-commit
- activate_training_venv.sh
- launch_vicon_bridge.sh
- PoseTwistAccelerationState
- PoseTwistAccelerationState
- Interface
- detect_contact_in_msg
- launch_ros_bridge.sh
- launch_ros_core.sh
- training.py
- Issue template chooser config
- archive_training_results.sh
- init_workspaces.sh
- kill_vicon.sh
- rl_multi_rotor_landing_gcs/other_files/prepare_terminal_window.sh
- record_rosbag.bash
- launch_vicon_environment_in_virtual_screens.sh
- vicon_compute_relative_state_moving_platform_drone.py
- PositionHistory
- .compute_reward
- QLearning
- moving_platform/test/test_flake8.py
- decay_rate_from_schedule
- publish_tf_transform_from_world_frame_to_copter_frame
- test_pep257
- prediction/ — LSTM-MDN platform-motion predictor (Phase 4)
- check_node_status.sh script
- .read_drone_state
- rl_multi_rotor_landing_sim/other_files/prepare_terminal_window.sh
- .read_training_continous_observations
- .read_contact_state
- .read_reset_simulation_signal
- compute_relative_observation_msg
- read_relative_position
- read_relative_velocity
- read_relative_acceleration
- read_action_setpoints
- compute_training_parameters.py
- compute_relative_acc_msg
- compute_relative_pos_msg
- compute_relative_vel_msg
- launch_bridges_in_virtual_screens.sh
- launch_telemetry_bridge.sh
- build_deb_container.sh
- build_deb_host.sh
- 1D longitudinal state space (rel_x, rel_vx)
- No contact sensor: touchdown inferred from altitude/offset/speed
- dummy.txt (empty placeholder in training_results)
- datagen.py
- reward.py (unnormalized weights)
- read_drone_imu
- read_moving_platform_imu
- read_gazebo_model_states
- compute_relative_observation_msg
- read_simulation_reset
- read_relative_position
- read_relative_velocity
- read_relative_acceleration
- read_action_setpoints
- read_twist
- reset_action_values
- read_v_z_control_effort
- read_yaw_control_effort
- read_pose

## God Nodes (most connected - your core abstractions)
1. `RosMissionIO` - 37 edges
2. `FakeWorld` - 34 edges
3. `MovingPlatformLander` - 29 edges
4. `Parameters` - 24 edges
5. `VisionLander` - 24 edges
6. `ResetManager` - 20 edges
7. `LandingEnv` - 19 edges
8. `MovingLandingConfig` - 19 edges
9. `Parameters` - 18 edges
10. `TargetTracker` - 18 edges

## Surprising Connections (you probably didn't know these)
- `FakeWorld offline harness (fake_world.py, test_missions.py)` --conceptually_related_to--> `Offline FakeWorld test harness`  [INFERRED]
  CLAUDE.md → README.md
- `use_sim_time / real-time-factor (RTF) finding` --conceptually_related_to--> `Simulation speed: use_sim_time and /clock bridge`  [INFERRED]
  README.md → workspace/ros2_ws/src/vision_node/README.md
- `What it does and why` --references--> `circular_state()`  [INFERRED]
  workspace/uav_rl_landing/prediction/README.md → workspace/ros2_ws/src/moving_platform/moving_platform/trajectories.py
- `What it does and why` --references--> `linear_state()`  [INFERRED]
  workspace/uav_rl_landing/prediction/README.md → workspace/ros2_ws/src/moving_platform/moving_platform/trajectories.py
- `What it does and why` --references--> `random_state()`  [INFERRED]
  workspace/uav_rl_landing/prediction/README.md → workspace/ros2_ws/src/moving_platform/moving_platform/trajectories.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **px4_msgs automated release pipeline** — workspace_ros2_ws_src_px4_msgs_github_workflows_create_release, workspace_ros2_ws_src_px4_msgs_github_workflows_package, workspace_ros2_ws_src_px4_msgs_github_workflows_release, workspace_ros2_ws_src_px4_msgs_github_workflows_release_bloom [EXTRACTED 1.00]
- **ROS 2 landing pipeline: px4_bridge -> relative_state -> RL agent -> landing_controller** — workspace_uav_rl_landing_readme_px4_bridge_uav_state_node, workspace_uav_rl_landing_readme_relative_state_node, workspace_uav_rl_landing_agent_q_learning, workspace_uav_rl_landing_readme_landing_controller_node [EXTRACTED 1.00]
- **px4_msgs quality assurance gates (CI, pre-commit, quality declaration)** — workspace_ros2_ws_src_px4_msgs_github_workflows_build, workspace_ros2_ws_src_px4_msgs_pre_commit_config, workspace_ros2_ws_src_px4_msgs_quality_declaration, workspace_ros2_ws_src_px4_msgs_github_dependabot [INFERRED 0.75]
- **5 km/h hardware-target enablers: --fast profile, tracker_max_speed fix, hysteresis fix, low camera latency** — workspace_ros2_ws_src_vision_node_readme_fast_profile, workspace_ros2_ws_src_vision_node_readme_tracker_max_speed_fix, workspace_ros2_ws_src_vision_node_readme_alignment_hysteresis_fix, workspace_ros2_ws_src_vision_node_readme_low_absolute_latency_finding, readme_five_kmh_hardware_target [INFERRED 0.85]
- **Moving-platform landing flow: patrol, ArUco lock, tracker-driven tracking, velocity-matched touchdown** — readme_patrol_search, readme_aruco_detection, readme_target_tracker, readme_moving_platform_landing_mission, readme_velocity_matched_touchdown [INFERRED 0.85]
- **RTF drift cluster: wall-clock platform node, ground-truth mismatch, false abort, trusted contact line** — readme_use_sim_time_rtf_finding, readme_false_estimate_mismatch_abort, claude_no_ground_truth_flag, claude_contact_line_trust_rule, workspace_ros2_ws_src_moving_platform_readme_use_sim_time_clock [INFERRED 0.85]

## Communities (180 total, 74 thin omitted)

### Community 1 - "RosMissionIO"
Cohesion: 0.05
Nodes (21): Exception, Switch landing_controller to velocity setpoints. It only streams offboard…, Sim ground truth from /platform/state, converted to PX4 local NED: (north,…, New absolute marker samples (time, x, y) since the last call., True if no RAW PX4 message (/fmu/out/vehicle_local_position_v1) has arrived in…, (messages, of which detected) received on /landing_target in the last `window`…, Mean absolute marker (x, y) over the latest few FRESH detections, or None if…, (mean rel_x, rel_y, rel_z, n) over the last `window` s, or None. (+13 more)

### Community 3 - "extract_topics_from_rosbag.py"
Cohesion: 0.24
Nodes (6): csv, os_path, rosbag, This script extracts flights from ros topics by determining the time periods in…, This scrips extracts topics from rosbag files that are required for further…, This script computes the duration of one round of training and applies…

### Community 4 - "LandingSimulationEnv"
Cohesion: 0.07
Nodes (28): Function creates a numpy.ndarray that can be indexed according to a…, LandingSimulationEnv, Bool, Function maps an action integer number to an action string, updates the new…, Function resets the training environment and updates logging data, Function sends out a boolean value indicating that a reset has been requested.…, Function sends out a boolean value indicating that a reset has been comnpleted.…, Function performs the normalization of observations of the environment and… (+20 more)

### Community 5 - "Parameters"
Cohesion: 0.05
Nodes (31): ndarray, QLearning, Function scales the values of a Q-table. Two options are available. - Mode…, Function adds num_ref_steps new curriculum steps to the sequential curriculum…, Function resets table values to predefined integer value., Class contains different functions to perform RL training for landing a multi-…, Function sets up the logging system for the training environment. It handles…, Function sets up the training environment and performs intial reset (+23 more)

### Community 6 - "AnalysisNode"
Cohesion: 0.07
Nodes (18): AnalysisNode, Function publishes basic statistics over the ROS framework for the movement in…, Function publishes basic statistics over the ROS framework for the movement in…, Function logs and computes basic statistics for motion in x-direction., Function logs and computes basic statistics for motion in y-direction., Function prints statistics to the terminal window, Function reads the current discrete states of the longitudinal motion., Function reads the current discrete states of the lateral motion. (+10 more)

### Community 7 - "rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_multiresolution.py"
Cohesion: 0.08
Nodes (25): Function creates a numpy.ndarray that can be indexed according to a…, discretize_action(), discretize_relative_state(), get_discrete_action_state_from_ros_msg(), get_discrete_rel_states_from_ros_msg(), get_discrete_state_from_ros_msg(), get_latest_cur_step_for_state(), initialize_grid_list() (+17 more)

### Community 8 - "ExplorationManager"
Cohesion: 0.22
Nodes (5): ExplorationManager, Choose action using epsilon-greedy policy., Restore epsilon from checkpoint., Current exploration rate., Handles epsilon-greedy exploration.

### Community 9 - "Vicon Launch Scripts"
Cohesion: 0.07
Nodes (20): src_rl_multi_rotor_landing_rl_multi_rotor_landing_gcs_other_files_setup_bash, ROS_IP, launch_audio_feedback.sh script, ROS_IP, launch_vicon_action_to_uavpose.sh script, launch_vicon_compute_relative_information.sh script, ROS_IP, launch_vicon_filter_platform_data.sh script (+12 more)

### Community 10 - "Platform Trajectory Generator"
Cohesion: 0.08
Nodes (16): Function computes a straight trajectory for the moving platform., Function computes a rectiliar periodic trajectory for the moving platform., Function computes a vertical, straight trajectory for the moving platform, Function computes a rectiliar periodic trajectory., Function computes the trajectory based on arguments trajectory_type,…, Function publishes the updated platform position to the ROS network., Function resets time to a random value within an interval of episode_length…, Function handles the service request to reset the seed for the random number… (+8 more)

### Community 11 - "MovingPlatformLander"
Cohesion: 0.10
Nodes (21): argparse, main(), parse_corner(), Phase 3b: camera-guided landing on a MOVING platform (circular motion) -- one…, main(), parse_corner(), Phase 3: camera-guided landing on a MOVING platform (straight-line motion) --…, MovingLandingConfig (+13 more)

### Community 12 - "train.py"
Cohesion: 0.19
Nodes (12): torch, torch_nn, torch_nn_functional, evaluate_nll(), export_npz(), LSTMMDN, main(), mdn_nll() (+4 more)

### Community 13 - "px4_msgs Contributing guide and release process"
Cohesion: 0.14
Nodes (26): px4_msgs CHANGELOG (tracks PX4 release lines 1.16, 1.17), px4_msgs CMakeLists.txt, rosidl_generate_interfaces (msg/srv glob to C++/Python/IDL), px4_msgs Code of Conduct, px4_msgs Contributing guide and release process, DCO sign-off and Conventional Commits policy, Dependabot config (github-actions updates), Pull request template (+18 more)

### Community 14 - "LogTraining"
Cohesion: 0.17
Nodes (8): LogTraining, Function saves the training and logging data, Function saves the logging data, Function handles the logging of data at the end of each episode., Class contains functions for printing out training information and for data…, Function performs operation that is executed in each timestep., Function prints info to the terminal when verbose is set to true., Function saves numpy.ndarrays that are used in the context of Q-learning. Array…

### Community 15 - "os"
Cohesion: 0.06
Nodes (40): datetime, gym, os, pandas, pickle, rosnode, rospkg, rostopic (+32 more)

### Community 16 - "ResetManager"
Cohesion: 0.10
Nodes (10): Command landing_controller into position-hold mode, targeting `pose`., Publish a new position-hold target without touching the control mode (used to…, True once /uav/state has converged on `pose` within tolerance., Hand control back to the RL agent's velocity commands., Disarm landing_controller (see its "disarm" mode) so the UAV actually sits…, Deliberately a no-op: moving_platform_node.py now drives the platform on a…, node : rclpy.node.Node The owning node, used to create subscriptions/publishers., A platform location (default: the hard-coded one), expressed in PX4's local NED… (+2 more)

### Community 17 - "math"
Cohesion: 0.13
Nodes (18): CLAUDE.md (Project Atlas instructions), circular_landing_main.py (motion-agnostic, --fast), FakeWorld offline harness (fake_world.py, test_missions.py), collections, dataclasses, math, typing, main() (+10 more)

### Community 19 - "test_missions.py"
Cohesion: 0.12
Nodes (25): fit_camera_latency(), Fit the camera latency from a flight over a STATIC marker. samples: (time,…, check(), _locked_at(), platform_error(), Offline tests for the vision missions (no ROS / PX4 / Gazebo needed). cd…, The bug found in the first Gazebo run: uncompensated camera latency corrupts…, KEY FINDING (from a real Gazebo run + this fake world's takeoff timing… (+17 more)

### Community 21 - "ArucoLandingTargetNode"
Cohesion: 0.12
Nodes (12): LandingTarget, ArucoLandingTargetNode, build_detector_params(), euler_to_rotation_matrix(), main(), Node, World-from-body rotation matrix for the 3-2-1 (yaw, pitch, roll) Euler…, True once camera intrinsics are available. If no camera_info shows up within… (+4 more)

### Community 22 - "LandingSimulationObject"
Cohesion: 0.06
Nodes (26): rosgraph, ndarray, QLearning, Function scales the values of a Q-table. Two options are available. - Mode…, Function adds num_ref_steps new curriculum steps to the sequential curriculum…, Function resets table values to predefined integer value., Class contains different functions to perform RL training for landing a multi-…, Function sets up the logging system for the training environment. It handles… (+18 more)

### Community 23 - "ViconInterface"
Cohesion: 0.13
Nodes (10): Convert quaterion defined in ENU frame to NED frame, Convert PoseStamped message from ENU to NED frame., Converts twist stamped message from ENU frame to NED frame., Publishes auxposition, auxvelocity in NED frame only when a new message was…, Function stores the pose and twist information together with the reference…, Reads vicon drone pose message, performs the frame conversion from ENU to NED…, Reads vicon drone pose message, performs the frame conversion from ENU to NED…, Reads vicon moving platform pose message, performs the frame conversion from… (+2 more)

### Community 24 - "ros_io.py"
Cohesion: 0.31
Nodes (8): interfaces_msg, px4_msgs_msg, rclpy, rclpy_node, rclpy_qos, Detects the ArUco marker on the moving platform (see…, Vision-based drop-in alternative to relative_state package's…, ros_io.py ROS 2 implementation of the `io` interface that…

### Community 25 - "ViconDebug"
Cohesion: 0.14
Nodes (9): Converts twist stamped message from ENU frame to NED frame., Class containing debugging functions and required variables, Reads vicon drone pose message., Reads state estimate drone pose message., Reads vicon drone twist message., Reads state estimate drone twist message., Convert quaterion defined in ENU frame to NED frame?, Convert PoseStamped message from ENU to NED frame. (+1 more)

### Community 26 - "rl_multi_rotor_landing repository (paper code)"
Cohesion: 0.14
Nodes (15): Cascaded PI controller baseline, Sequential curriculum training procedure, rl_multi_rotor_landing_gcs catkin workspace, LibrePilot Ground Control Station, moving_platform_control package (model train on rails), Goldschmid & Ahmad paper (Autonomous Robots 2024), rl_multi_rotor_landing repository (paper code), RotorS + ROS Noetic + Gazebo 11 stack (+7 more)

### Community 27 - "TargetTracker"
Cohesion: 0.17
Nodes (4): Low-pass estimate of how fast the fitted velocity vector's HEADING is rotating…, True if a sample ARRIVED within the last `max_age` seconds., t = when the marker was SEEN (capture time); received = when the sample arrived…, TargetTracker

### Community 28 - "SmoothPlatformData"
Cohesion: 0.19
Nodes (5): OneEuroFilter, Function stores the pose and twist data of the platform received via the vicon…, Initialize the one euro filter. Based on https://jaantollander.com/post/noise-…, Compute the filtered signal., SmoothPlatformData

### Community 30 - "Moving-platform landing mission (lock / track / touchdown)"
Cohesion: 0.16
Nodes (14): ArUco marker detection, Blind final ~1 m of descent, Moving-platform landing mission (lock / track / touchdown), Nested smaller marker (proposed fix for blind window), Velocity-matched contact touchdown, ArUco detection (DICT_4X4_50, marker id 0, solvePnP), aruco_landing_target_node, Blind final descent window (marker leaves FOV below ~1 m) (+6 more)

### Community 31 - "write_data_to_csv"
Cohesion: 0.19
Nodes (6): LogTopicFreqs, This is a variation of the create_log_dir_path_function in the utils script.…, LogTopicFreqs, This is a variation of the create_log_dir_path_function in the utils script.…, Functions writes a list of values as a row to a .csv file., write_data_to_csv()

### Community 32 - "grid_utils.py"
Cohesion: 0.21
Nodes (10): Create: Q(s,a) DoubleQ(s,a) VisitCounter(s,a), create_double_q_tables(), create_empty_q_table(), create_visit_counter(), initialize_grid_list(), Grid utilities. This module contains helper functions used for multi-resolution…, Create a nested numpy array whose shape matches the discretization grid.…, Create an empty Q-table. The last dimension corresponds to actions. (+2 more)

### Community 33 - "ament_flake8_main"
Cohesion: 0.12
Nodes (13): ament_flake8_main, flake8, linter, test_flake8(), flake8, linter, test_flake8(), flake8 (+5 more)

### Community 34 - "ament_pep257_main"
Cohesion: 0.14
Nodes (10): ament_pep257_main, linter, pep257, test_pep257(), linter, pep257, test_pep257(), linter (+2 more)

### Community 35 - "test_marker_detection.py"
Cohesion: 0.33
Nodes (4): cv2, pathlib, Generates the ArUco marker image used as the visual landing target on top of…, Standalone sanity check for the ArUco detection logic in…

### Community 36 - "TargetTracker"
Cohesion: 0.21
Nodes (13): Camera-latency compensation, Circular platform motion, CTRV curvature-aware extrapolation, Reversal detector firing on ordinary curvature (bug), TargetTracker, Circular motion (radius, angular_speed, center), Camera-latency compensation (io.camera_latency), CTRV curvature extrapolation in TargetTracker (+5 more)

### Community 37 - "CascadedPIDInterface"
Cohesion: 0.15
Nodes (4): CascadedPIDInterface, FlightActivated, Class stores information RL controlled flight is activated., Reads the status of the ROS controlled parameters and stores the value in the…

### Community 38 - "interfaces ament package"
Cohesion: 0.17
Nodes (12): LandingCommand.msg, LandingTarget.msg, interfaces ament package, PlatformState.msg, RLObservation.msg, TakeoffSetpoint.msg, UAVState.msg, landing_controller_node (position/velocity modes) (+4 more)

### Community 39 - "LandingController"
Cohesion: 0.21
Nodes (4): LandingController, main(), Node, Switch PX4 into its own AUTO.LAND flight mode instead of us trying to fake a…

### Community 40 - "MovingPlatformNode"
Cohesion: 0.31
Nodes (5): main(), MovingPlatformNode, Node, Seconds on the ROS clock. Wall time by default; SIM time with `-p…, Block briefly until self._now() is reporting real time, not an as-yet-…

### Community 41 - "landing_env.py"
Cohesion: 0.12
Nodes (12): Parameters, ActionManager, node : rclpy.node.Node The owning node, used to create the publisher.…, Reset actions to their initial values., Update action values using the discrete action selected by the RL agent. Only…, Publish the current control command., Return the current action values., Handles UAV actions. Responsibilities ---------------- - Maintain current… (+4 more)

### Community 42 - "patch_x500_camera.py"
Cohesion: 0.29
Nodes (10): Path, re, find_link_anchor(), find_model_sdf(), _is_file_safe(), main(), patch(), Path.is_file() raises PermissionError (rather than returning False) when an… (+2 more)

### Community 43 - "rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/parameters.py"
Cohesion: 0.23
Nodes (7): This script contains the parameters to set up a training case…, Class provides data about the vehicle, Class provides parameter affecting the training and values generated from the…, Class provides variables that affect the reinforcement learning algorithm and…, RLParameters, SimulationParameters, UAVParameters

### Community 44 - "rl_multi_rotor_landing_sim/src/training_q_learning/src/training_q_learning/parameters.py"
Cohesion: 0.23
Nodes (7): This script contains the parameters to set up a training case…, Class provides data about the vehicle, Class provides parameter affecting the training and values generated from the…, Class provides variables that affect the reinforcement learning algorithm and…, RLParameters, SimulationParameters, UAVParameters

### Community 45 - "config/parameters.py"
Cohesion: 0.23
Nodes (7): Parameters for the uav_rl_landing training case. Ported from the original…, # NOTE: there is no contact sensor wired up yet (no Gazebo contact, Vehicle / action-space configuration., Reinforcement-learning / curriculum configuration., RLParameters, SimulationParameters, UAVParameters

### Community 46 - "LandingEnv"
Cohesion: 0.14
Nodes (8): LandingEnv, Node, Apply one discrete action, advance one control period, and return (state,…, Spin this node's callbacks for approximately duration_sec, so subscription…, Reset the episode: sample a target pose, fly there for real and hold (position-…, Call at the start of every episode., Returns (done: bool, outcome: str, success: bool). outcome is one of:…, TerminationManager

### Community 47 - "numpy"
Cohesion: 0.10
Nodes (38): copy, gazebo_msgs_msg, gazebo_msgs_srv, geometry_msgs_msg, gym_envs_registration, librepilot_msg, mav_msgs_msg, numpy (+30 more)

### Community 48 - "StateDiscretizer"
Cohesion: 0.24
Nodes (5): State Discretizer Converts continuous observations (an…, Build discretization limits for every observation according to the current…, Convert one continuous value into a discrete bin index (evenly-spaced bins over…, Convert a continuous observation into a discrete state tuple. `observation`…, StateDiscretizer

### Community 49 - "Linear 5 km/h with --fast and travel_length=50"
Cohesion: 0.15
Nodes (16): Validated status table (2026-10-14), Platform motion anchored to a patrol leg, Control-law speed ceiling (~0.8-1.0 m/s with default gains), --fast control profile (higher-bandwidth gains), 5 km/h (1.39 m/s) real-hardware target, Linear (back-and-forth) platform motion, One-way platform motion fails with the patrol design, Square patrol search (A-B-C-D) (+8 more)

### Community 50 - "Project Atlas (README)"
Cohesion: 0.22
Nodes (13): Double Q-learning agent, RL based Autonomous Multi-Rotor Landing on Moving Platforms (Goldschmid & Ahmad), Phase 1: landing on hard-coded static platform, Phase 2: camera-guided landing on static platform, Phase 3: landing on a moving platform (linear + circular), Phase 4+: RL-controlled approach and real hardware, Project Atlas (README), PX4 + ROS 2 Humble + Gazebo Harmonic stack (+5 more)

### Community 51 - ".save_training_data"
Cohesion: 0.20
Nodes (5): Function saves numpy.ndarrays that are used in the context of Q-learning. Array…, Function saves the training and logging data, Function saves the logging data, Function handles the logging of data at the end of each episode., Function prints info to the terminal when verbose is set to true.

### Community 52 - "state_publisher.cpp"
Cohesion: 0.22
Nodes (5): jointstate, model, ros, string, transform_broadcaster

### Community 53 - "moving_platform_node"
Cohesion: 0.25
Nodes (8): cmd_vel -> Gazebo VelocityControl plugin, moving_platform_node, Open-loop velocity control drift, PlatformState ground truth on /platform/state, trajectories.py (ROS-free trajectory maths), Trajectory clock: wall time vs use_sim_time, wait_for_start / /moving_platform/start, Simulation speed: use_sim_time and /clock bridge

### Community 54 - "generate_changelog.sh"
Cohesion: 0.42
Nodes (8): contributors(), emit(), forthcoming_block(), generate(), join_csv(), names(), generate_changelog.sh script, underline()

### Community 55 - "ActionToUavPose"
Cohesion: 0.29
Nodes (5): ActionMsg, ActionToUavPose, Class stores all data that is required to convert roll pitch yawrate thrust to…, Funcion assigns the values of roll, pitch and yaw to the velocity field of the…, Function processes the msgs received on the topic

### Community 56 - "Gotchas (RTF, ground truth, FakeWorld limits, travel_length)"
Cohesion: 0.31
Nodes (9): Trust the 'Contact at ... predicted platform position' line, Gotchas (RTF, ground truth, FakeWorld limits, travel_length), --no-ground-truth flag, False ESTIMATE_MISMATCH abort / --no-ground-truth workaround, Offline FakeWorld test harness, tracker_max_speed vs max_speed flight-safety fix, use_sim_time / real-time-factor (RTF) finding, Offline FakeWorld tests (tests.test_missions) (+1 more)

### Community 57 - "MDNPredictor"
Cohesion: 0.21
Nodes (7): density_peak(), MDNPredictor, Prediction, Build the network input once per set of detections (ENU: xs east, ys north, ts…, The candidate point (a mode centre or the mixture mean) where the mixture is…, seq (L, 3) float, H seconds -> pi (K,), mu (K, 2), sigma (K, 2), rho (K,) in…, _sigmoid()

### Community 59 - "plot_topic_freq_from_flight.py"
Cohesion: 0.53
Nodes (5): matplotlib_pyplot, calcualte_windowed_freqs_over_time(), create_plot(), decompose_vector(), plot_topic_frequency()

### Community 60 - "_RandomPath"
Cohesion: 0.33
Nodes (5): _advance(), _RandomPath, Position and heading after tau seconds at speed v and constant turn rate w…, The segment stays in the arena AND ends somewhere the platform can still turn…, _wrap()

### Community 61 - "RelativeStateNode"
Cohesion: 0.29
Nodes (3): main(), Node, RelativeStateNode

### Community 63 - "publish_stability_axes.py"
Cohesion: 0.33
Nodes (6): nav_msgs_msg, publish_stability_axes_as_tf_frame(), Function publishes the stability axes as tf frame. The stability axes xy-plane…, Function publishes the stability axes frame w.r.t. the world frame., Function reads the odometry messages of the drone and triggers publishing of…, read_odom_msg()

### Community 64 - "RelativeStateNode"
Cohesion: 0.29
Nodes (3): main(), Node, RelativeStateNode

### Community 65 - "VisionRelativeStateNode"
Cohesion: 0.29
Nodes (3): main(), Node, VisionRelativeStateNode

### Community 66 - "training_q_learning catkin package (simulation)"
Cohesion: 0.33
Nodes (6): training_q_learning catkin package (GCS/Vicon), Vicon scripts (vicon_interface, vicon_test_model_2D, vicon_cascaded_pid_controller, ...), training_q_learning catkin package (simulation), ResetRandomSeed.srv, Custom ROS messages (Action, ObservationRelativeState, TwistModified, LandingSimulationObjectState), Simulation scripts (training.py, observation_generator.py, test_model_2D.py, cascaded_pid_controller.py, ...)

### Community 67 - "UAVPoseFromStateEstimate"
Cohesion: 0.40
Nodes (3): Class stores all data that is required to convert roll pitch yawrate thrust to…, Function processes the msgs received on the topic, UAVPoseFromStateEstimate

### Community 68 - "process_action"
Cohesion: 0.33
Nodes (6): process_action(), publish_setpoint_v_z(), publish_setpoint_yaw(), Function publishes the setpoint for the PID controller of v_z based on the…, Function publishes the setpoint for the PID controller of the yaw angle based…, Function triggers the processing procedure whenever a new msg is received from…

### Community 69 - "world_base_link_transform_publisher.py"
Cohesion: 0.24
Nodes (8): PositionOrientationState, publish_transform_message(), publish_world_to_world_link_transform_message(), Class for storing the current position and orientation of the moving platform, Read model state of moving platform., Function publishes the required tf transform from world frame to an additional…, Publish the transformation message to describe the motion of the moving…, read_model_state()

### Community 70 - "run_sim_terminals.sh"
Cohesion: 0.60
Nodes (5): find_terminal(), open_terminal(), run_sim_terminals.sh script, start_all(), stop_all()

### Community 73 - "ObservationRelativeState"
Cohesion: 0.40
Nodes (3): ObservationRelativeState, Class stores the relative position, relative velocity, relative acceleration…, Function checks if all sensor values are provided in the same reference frame.

### Community 74 - "FlightActivated"
Cohesion: 0.40
Nodes (3): FlightActivated, Class stores information RL controlled flight is activated., Reads the status of the ROS controlled parameters and stores the value in the…

### Community 75 - "publish_vmp_x.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, publish_vmp_x.sh script

### Community 76 - "publish_vmp_y.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, publish_vmp_y.sh script

### Community 77 - "launch_action_interface.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_action_interface.sh script

### Community 78 - "launch_analysis_node_2D.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_analysis_node_2D.sh script

### Community 79 - "launch_cascaded_pid_environment_in_virtual_screens.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_cascaded_pid_environment_in_virtual_screens.sh script

### Community 80 - "launch_cascaded_pid_interface.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_cascaded_pid_interface.sh script

### Community 81 - "launch_compute_relative_information.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_compute_relative_information.sh script

### Community 82 - "launch_environment_in_virtual_screens.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_environment_in_virtual_screens.sh script

### Community 83 - "launch_landing_simulation.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_landing_simulation.sh script

### Community 84 - "launch_observation_generator.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_observation_generator.sh script

### Community 85 - "launch_publish_stability_axes.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_publish_stability_axes.sh script

### Community 86 - "launch_test_model_2D.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_test_model_2D.sh script

### Community 87 - "launch_training.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_training.sh script

### Community 88 - "moving_platform_description catkin package"
Cohesion: 0.40
Nodes (5): parser executable, moving_platform_description catkin package, state_publisher executable, command_moving_platform_trajectories.py and world_base_link_transform_publisher.py, JointStateController config (50 Hz)

### Community 89 - "generate_release_notes.sh"
Cohesion: 0.70
Nodes (4): decls(), header(), namelist(), generate_release_notes.sh script

### Community 91 - "execute_training_curriculum_for_one_sim_one_exp.py"
Cohesion: 0.22
Nodes (8): fileinput, get_last_final_result_path(), This script automizes the execution of the sequential curriculum. Requirements:…, This functions opens a file, searches for a pattern, replaces it with the…, Functions open a text file, searches through all lines and replaces the lines…, Function returns the absolute path to the latest final result that can be used…, replace_line_in_textfile_that_contains(), replace_text_in_file()

### Community 92 - "rl_multi_rotor_landing_gcs/other_files/setup.bash"
Cohesion: 0.50
Nodes (3): setup.bash script, ROS_PACKAGE_PATH, ROS_PROJECT_ROOT

### Community 93 - "vicon_publish_stability_axes.py"
Cohesion: 0.22
Nodes (8): tf2_ros, uav_msgs_msg, publish_stability_axes_as_tf_frame(), Function publishes the stability axes frame w.r.t. the world frame., Function reads the pose messages of the copter in the vicon system., read_pose_msg(), This script publishes the copter frame based on the state estimate of the fx as…, This scripts defines a conversion node that converts messages of type…

### Community 97 - "rl_multi_rotor_landing_sim/other_files/setup.bash"
Cohesion: 0.50
Nodes (3): setup.bash script, ROS_PACKAGE_PATH, ROS_PROJECT_ROOT

### Community 98 - "main"
Cohesion: 0.20
Nodes (10): copyright, linter, skip, test_copyright(), linter, pep257, test_pep257(), build_detector_params() (+2 more)

### Community 99 - "q_learning.py"
Cohesion: 0.28
Nodes (5): build_grid(), main(), q_learning.py Double Q-learning training loop (Hasselt 2010), ported from the…, QTableManager, q_table.py Creates and manages the Q-Tables used by Double Q-Learning.

### Community 100 - "test_copyright"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 101 - "test_copyright"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 102 - "moving_platform_node.py"
Cohesion: 0.15
Nodes (17): bisect, random, Publishes the moving platform's ground-truth state (PlatformState, the RL…, circular_state(), linear_state(), random_state(), Platform trajectories as pure functions of elapsed time (no ROS imports, so…, Counter-clockwise circle; at t=0 the platform is at (center_x + radius,… (+9 more)

### Community 103 - "test_copyright"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 104 - "test_copyright"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 107 - "fyp-uav docker compose service"
Cohesion: 0.67
Nodes (3): /dev/dri GPU passthrough with render group (RENDER_GID), fyp-uav docker compose service, Workspace volume mounts (/workspace, /gazebo, /datasets, /docs)

### Community 114 - "detect_contact_in_msg"
Cohesion: 0.67
Nodes (3): detect_contact_in_msg(), ContactsState, Function returns the value true if a contact has been detected by a contact…

### Community 117 - "training.py"
Cohesion: 0.29
Nodes (5): roslaunch, training_q_learning_custom_q_learning, Script creates the simulation environment that is required in order to use 4…, This script starts a training session., This script starts a training session.

### Community 118 - "Issue template chooser config"
Cohesion: 0.67
Nodes (3): Bug report issue template, Issue template chooser config, Feature request issue template

### Community 125 - "vicon_compute_relative_state_moving_platform_drone.py"
Cohesion: 0.11
Nodes (16): tf2_geometry_msgs, compute_landing_simulation_object_state_msg(), compute_relative_pos_msg(), compute_relative_vel_msg(), This scripts defines a ROS node that provides information about the moving…, Reads pose message of moving platform and stores data in storage class., Reads twist message of moving platform and stores data in storage class., Function computes the relative velocity vector between the moving platform and… (+8 more)

### Community 126 - "PositionHistory"
Cohesion: 0.33
Nodes (3): PositionHistory, Recent UAV (t, x, y) samples, so a camera measurement can be combined with…, UAV position at time t (linear interpolation; clamped to the ends), or None if…

### Community 127 - ".compute_reward"
Cohesion: 0.25
Nodes (4): Function checks whether or not the episode has to be terminated or not. It can…, Function computes the reward function of the agent for the current timestep., Function checks episode termination status and generates the appropriate reward., Publication of the current discrete state to the ROS environment.

### Community 128 - "QLearning"
Cohesion: 0.36
Nodes (3): QLearning, Log/save/decay after an episode. Returns True if training should stop., Load previously saved Q-tables (as produced by save()).

### Community 129 - "moving_platform/test/test_flake8.py"
Cohesion: 0.50
Nodes (3): flake8, linter, test_flake8()

### Community 130 - "decay_rate_from_schedule"
Cohesion: 0.33
Nodes (4): Update epsilon according to schedule., decay_rate_from_schedule(), schedule.py Utility functions for learning-rate and exploration-rate scheduling., Compute a value from a decay schedule. Supported schedule types: "lin" ->…

### Community 131 - "publish_tf_transform_from_world_frame_to_copter_frame"
Cohesion: 0.50
Nodes (4): publish_tf_transform_from_world_frame_to_copter_frame(), Function publishes a tf transform from the euler_angle_parent_frame frame to…, Function reads the pose messages of the copter in the vicon system and calls…, read_pose_msg()

### Community 132 - "test_pep257"
Cohesion: 0.50
Nodes (3): linter, pep257, test_pep257()

### Community 133 - "prediction/ — LSTM-MDN platform-motion predictor (Phase 4)"
Cohesion: 0.50
Nodes (4): Choices that matter, Commands, prediction/ — LSTM-MDN platform-motion predictor (Phase 4), Results (all offline)

### Community 160 - "datagen.py"
Cohesion: 0.08
Nodes (33): concurrent_futures, sys, _chunk(), make_dataset(), make_track(), truth(), observe(), Synthetic training / evaluation data for the platform-motion predictor. A… (+25 more)

## Knowledge Gaps
- **136 isolated node(s):** `archive_training_results.sh script`, `init_workspaces.sh script`, `kill_vicon.sh script`, `prepare_terminal_window.sh script`, `record_rosbag.bash script` (+131 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 763 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **74 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `main` to `ament_pep257_main`, `test_marker_detection.py`, `test_pep257`, `test_copyright`, `test_copyright`, `test_copyright`, `test_copyright`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `CLAUDE.md (Project Atlas instructions)` connect `math` to `Gotchas (RTF, ground truth, FakeWorld limits, travel_length)`, `Linear 5 km/h with --fast and travel_length=50`, `Project Atlas (README)`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Why does `TrajectoryGenerator` connect `Platform Trajectory Generator` to `Parameters`, `numpy`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `RosMissionIO` (e.g. with `Parameters` and `ResetManager`) actually correct?**
  _`RosMissionIO` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `archive_training_results.sh script`, `init_workspaces.sh script`, `kill_vicon.sh script` to the rest of the system?**
  _136 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `RosMissionIO` be split into smaller, more focused modules?**
  _Cohesion score 0.05084745762711865 - nodes in this community are weakly interconnected._
- **Should `LandingSimulationEnv` be split into smaller, more focused modules?**
  _Cohesion score 0.07195121951219512 - nodes in this community are weakly interconnected._