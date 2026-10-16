# Graph Report - FYP_UAV  (2026-10-16)

## Corpus Check
- 189 files · ~114,951 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 380 file(s) not represented in the graph (top: .msg 275, .launch 34, (none) 21)

## Summary
- 1672 nodes · 2679 edges · 148 communities (112 shown, 36 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 104 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5e854e6f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- landing_simulation_env.py
- LandingSimulationEnv
- LandingSimulationObject
- time
- AnalysisNode
- q_learning.py
- RosMissionIO
- src_rl_multi_rotor_landing_rl_multi_rotor_landing_gcs_other_files_setup_bash
- TrajectoryGenerator
- px4_msgs Contributing guide and release process
- FakeWorld
- numpy
- test_missions.py
- rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_q_learning.py
- Parameters
- training_action_interface.py
- ResetManager
- moving_platform_node.py
- VisionLander
- rl_multi_rotor_landing_sim/src/training_q_learning/src/training_q_learning/utils_multiresolution.py
- aruco_landing_target_node.py
- QLearning
- MovingPlatformLander
- ViconInterface
- LogTraining
- LandingEnv
- vicon_compute_relative_state_moving_platform_drone.py
- ViconDebug
- compute_relative_state_moving_platform_drone.py
- math
- get_publisher
- rospy
- rl_multi_rotor_landing repository (paper code)
- rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_multiresolution.py
- observation_generator.py
- TargetTracker
- MovingLandingConfig
- --fast higher-bandwidth gain profile
- LSTM-MDN predictor (mixture of K=5 bivariate Gaussians)
- vicon_observation_generator.py
- write_data_to_csv
- SmoothPlatformData
- ViconEnv
- ViconObject
- StateDiscretizer
- ament_flake8_main
- get_publisher
- interfaces ament package
- LandingController
- ActionManager
- training.py
- moving_landing.py (lock/track/touchdown loop)
- moving_platform
- Phase 3: moving platform (linear and circular)
- CascadedPIDData
- rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/parameters.py
- Parameters
- grid_utils.py
- config/parameters.py
- patch_x500_camera.py
- main
- ros_io.py
- add_cur_step_lims_of_state
- moving_platform_node (publishes /platform/state, drives Gazebo model)
- LogTraining
- world_base_link_transform_publisher.py
- linear_state
- landing_env.py
- ament_pep257_main
- landing_controller/test/test_flake8.py
- state_publisher.cpp
- generate_changelog.sh
- moving_platform/test/test_flake8.py
- test_circular
- ActionToUavPose
- setuptools
- test_copyright
- pytest
- test_pep257
- publish_stability_axes.py
- rclpy_node
- vision_relative_state_node.py
- training_q_learning catkin package (simulation)
- UAVPoseFromStateEstimate
- run_sim_terminals.sh
- PositionHistory
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
- vision_landing.py
- rl_multi_rotor_landing_gcs/other_files/setup.bash
- initialize_grid_list
- clear_all_sims.sh script
- rl_multi_rotor_landing_sim/other_files/setup.bash
- test_copyright
- test_pep257
- test_pep257
- test_copyright
- test_copyright
- README.md project write-up
- fyp-uav docker compose service
- pre-commit
- activate_training_venv.sh
- launch_vicon_bridge.sh
- launch_ros_bridge.sh
- launch_ros_core.sh
- Issue template chooser config
- test_random
- archive_training_results.sh
- init_workspaces.sh
- kill_vicon.sh
- rl_multi_rotor_landing_gcs/other_files/prepare_terminal_window.sh
- record_rosbag.bash
- launch_vicon_environment_in_virtual_screens.sh
- check_node_status.sh script
- rl_multi_rotor_landing_sim/other_files/prepare_terminal_window.sh
- launch_bridges_in_virtual_screens.sh
- launch_telemetry_bridge.sh
- build_deb_container.sh
- build_deb_host.sh
- 1D longitudinal state space (rel_x, rel_vx)
- No contact sensor: touchdown inferred from altitude/offset/speed
- dummy.txt (empty placeholder in training_results)
- reward.py (unnormalized weights)

## God Nodes (most connected - your core abstractions)
1. `RosMissionIO` - 38 edges
2. `FakeWorld` - 38 edges
3. `MovingPlatformLander` - 31 edges
4. `Parameters` - 24 edges
5. `VisionLander` - 24 edges
6. `MovingLandingConfig` - 21 edges
7. `ResetManager` - 20 edges
8. `LandingEnv` - 19 edges
9. `Parameters` - 18 edges
10. `TargetTracker` - 18 edges

## Surprising Connections (you probably didn't know these)
- `LSTM-MDN predictor (mixture of K=5 bivariate Gaussians)` --semantically_similar_to--> `Curvature-aware (CTRV) tracker extrapolation`  [INFERRED] [semantically similar]
  workspace/uav_rl_landing/prediction/README.md → README.md
- `Correction: judge by true offset at contact` --semantically_similar_to--> `Judge landings by TRUE offset, not predicted-position line`  [INFERRED] [semantically similar]
  README.md → CLAUDE.md
- `What it does and why` --references--> `circular_state()`  [INFERRED]
  workspace/uav_rl_landing/prediction/README.md → workspace/ros2_ws/src/moving_platform/moving_platform/trajectories.py
- `What it does and why` --references--> `random_state()`  [INFERRED]
  workspace/uav_rl_landing/prediction/README.md → workspace/ros2_ws/src/moving_platform/moving_platform/trajectories.py
- `evaluate.py (MDN vs CV vs tracker CTRV)` --references--> `target_tracker.py (velocity fit, reversal detection, CTRV)`  [EXTRACTED]
  workspace/uav_rl_landing/prediction/README.md → CLAUDE.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **MDN predictor train-to-inference pipeline** — workspace_uav_rl_landing_prediction_readme_features_py, workspace_uav_rl_landing_prediction_readme_datagen_py, workspace_uav_rl_landing_prediction_readme_train_py, workspace_uav_rl_landing_prediction_readme_mdn_numpy_py, workspace_uav_rl_landing_prediction_readme_evaluate_py [EXTRACTED 1.00]
- **px4_msgs automated release pipeline** — workspace_ros2_ws_src_px4_msgs_github_workflows_create_release, workspace_ros2_ws_src_px4_msgs_github_workflows_package, workspace_ros2_ws_src_px4_msgs_github_workflows_release, workspace_ros2_ws_src_px4_msgs_github_workflows_release_bloom [EXTRACTED 1.00]
- **ROS 2 landing pipeline: px4_bridge -> relative_state -> RL agent -> landing_controller** — workspace_uav_rl_landing_readme_px4_bridge_uav_state_node, workspace_uav_rl_landing_readme_relative_state_node, workspace_uav_rl_landing_agent_q_learning, workspace_uav_rl_landing_readme_landing_controller_node [EXTRACTED 1.00]
- **px4_msgs quality assurance gates (CI, pre-commit, quality declaration)** — workspace_ros2_ws_src_px4_msgs_github_workflows_build, workspace_ros2_ws_src_px4_msgs_pre_commit_config, workspace_ros2_ws_src_px4_msgs_quality_declaration, workspace_ros2_ws_src_px4_msgs_github_dependabot [INFERRED 0.75]
- **Mitigations for the blind final metre** — readme_kz_gain, readme_curvature_tracker, workspace_uav_rl_landing_prediction_readme_lstm_mdn, readme_blind_final_metre [INFERRED 0.85]
- **Components of the --fast tuning profile** — readme_fast_profile, workspace_ros2_ws_src_vision_node_readme_hysteresis_fix, readme_tracker_max_speed_fix, workspace_ros2_ws_src_vision_node_readme_jiggle_window [INFERRED 0.85]

## Communities (148 total, 36 thin omitted)

### Community 0 - "landing_simulation_env.py"
Cohesion: 0.10
Nodes (27): copy, gazebo_msgs_msg, gazebo_msgs_srv, gym, gym_envs_registration, librepilot_msg, std_msgs_msg, std_srvs_srv (+19 more)

### Community 1 - "LandingSimulationEnv"
Cohesion: 0.15
Nodes (10): LandingSimulationEnv, Bool, Function maps an action integer number to an action string, updates the new…, Function resets the training environment and updates logging data, Function sends out a boolean value indicating that a reset has been requested.…, Function sends out a boolean value indicating that a reset has been comnpleted.…, Function performs the normalization of observations of the environment and…, Function publishes the action values that are currently set to the ROS network. (+2 more)

### Community 2 - "LandingSimulationObject"
Cohesion: 0.10
Nodes (14): LandingSimulationObjectState, ObservationRelativeStateMsg, LandingSimulationObject, Bool, ContactsState, Functions reads the continouos observations of the environment whenever the…, Function checks if the contact sensor on top of the moving platform sends…, Functions resets variables to init values whenever a reset signal is received. (+6 more)

### Community 3 - "time"
Cohesion: 0.07
Nodes (28): fileinput, rospkg, rostopic, shutil, time, This script automizes the execution of the evaluation of an agent for all…, get_last_final_result_path(), get_last_parameters_file() (+20 more)

### Community 4 - "AnalysisNode"
Cohesion: 0.07
Nodes (18): AnalysisNode, Function publishes basic statistics over the ROS framework for the movement in…, Function publishes basic statistics over the ROS framework for the movement in…, Function logs and computes basic statistics for motion in x-direction., Function logs and computes basic statistics for motion in y-direction., Function prints statistics to the terminal window, Function reads the current discrete states of the longitudinal motion., Function reads the current discrete states of the lateral motion. (+10 more)

### Community 5 - "q_learning.py"
Cohesion: 0.09
Nodes (18): ExplorationManager, Choose action using epsilon-greedy policy., Update epsilon according to schedule., Restore epsilon from checkpoint., Current exploration rate., Handles epsilon-greedy exploration., build_grid(), main() (+10 more)

### Community 6 - "RosMissionIO"
Cohesion: 0.07
Nodes (10): Angle [deg] between the UAV's up axis and vertical, from /uav/state roll and…, Switch landing_controller to velocity setpoints. It only streams offboard…, Sim ground truth from /platform/state, converted to PX4 local NED: (north,…, New absolute marker samples (time, x, y) since the last call., True if no RAW PX4 message (/fmu/out/vehicle_local_position_v1) has arrived in…, (messages, of which detected) received on /landing_target in the last `window`…, Mean absolute marker (x, y) over the latest few FRESH detections, or None if…, (mean rel_x, rel_y, rel_z, n) over the last `window` s, or None. (+2 more)

### Community 7 - "src_rl_multi_rotor_landing_rl_multi_rotor_landing_gcs_other_files_setup_bash"
Cohesion: 0.07
Nodes (20): src_rl_multi_rotor_landing_rl_multi_rotor_landing_gcs_other_files_setup_bash, ROS_IP, launch_audio_feedback.sh script, ROS_IP, launch_vicon_action_to_uavpose.sh script, launch_vicon_compute_relative_information.sh script, ROS_IP, launch_vicon_filter_platform_data.sh script (+12 more)

### Community 8 - "TrajectoryGenerator"
Cohesion: 0.08
Nodes (16): Function computes a straight trajectory for the moving platform., Function computes a rectiliar periodic trajectory for the moving platform., Function computes a vertical, straight trajectory for the moving platform, Function computes a rectiliar periodic trajectory., Function computes the trajectory based on arguments trajectory_type,…, Function publishes the updated platform position to the ROS network., Function resets time to a random value within an interval of episode_length…, Function handles the service request to reset the seed for the random number… (+8 more)

### Community 9 - "px4_msgs Contributing guide and release process"
Cohesion: 0.14
Nodes (26): px4_msgs CHANGELOG (tracks PX4 release lines 1.16, 1.17), px4_msgs CMakeLists.txt, rosidl_generate_interfaces (msg/srv glob to C++/Python/IDL), px4_msgs Code of Conduct, px4_msgs Contributing guide and release process, DCO sign-off and Conventional Commits policy, Dependabot config (github-actions updates), Pull request template (+18 more)

### Community 10 - "FakeWorld"
Cohesion: 0.10
Nodes (3): FakeWorld, Tilt [deg] from vertical (only when the tilt model is on), like…, (north, east, v_north, v_east) at world time t.

### Community 11 - "numpy"
Cohesion: 0.08
Nodes (27): csv, matplotlib_pyplot, numpy, os, os_path, pandas, pathlib, rosbag (+19 more)

### Community 12 - "test_missions.py"
Cohesion: 0.16
Nodes (16): random, A fake drone + camera + platform implementing the `io` interface of…, check(), platform_error(), Offline tests for the vision missions (no ROS / PX4 / Gazebo needed). cd…, Phase 2 mission against a static platform at (north, east)., # NOTE: the jitter-sweep checks below judge success against error_to_estimate…, # IMPORTANT: matters which latency BASELINE this runs at, not just whether it's… (+8 more)

### Community 13 - "rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_q_learning.py"
Cohesion: 0.18
Nodes (10): datetime, pickle, rosnode, torch_utils_tensorboard, decay_rate_from_schedule(), This script contains the definitions of classes and function that are required…, Function determines the decay rate that has been defined using a dictionary.…, decay_rate_from_schedule() (+2 more)

### Community 14 - "Parameters"
Cohesion: 0.11
Nodes (14): ndarray, QLearning, Function scales the values of a Q-table. Two options are available. - Mode…, Function adds num_ref_steps new curriculum steps to the sequential curriculum…, Function resets table values to predefined integer value., Class contains different functions to perform RL training for landing a multi-…, Function sets up the training environment and performs intial reset, Function implements the Double Q-learning algorithm presented in… (+6 more)

### Community 15 - "training_action_interface.py"
Cohesion: 0.09
Nodes (21): Interface, process_action(), publish_roll_pitch_yawrate_thrust_msg(), publish_setpoint_v_z(), publish_setpoint_yaw(), This script creates an interface node which fuses the setpoints for the roll,…, Function reads the message containing the relative pose information of moving…, Function publishes the setpoint for the PID controller of v_z based on the… (+13 more)

### Community 16 - "ResetManager"
Cohesion: 0.09
Nodes (12): Command landing_controller into position-hold mode, targeting `pose`., Publish a new position-hold target without touching the control mode (used to…, True once /uav/state has converged on `pose` within tolerance., Hand control back to the RL agent's velocity commands., Disarm landing_controller (see its "disarm" mode) so the UAV actually sits…, Deliberately a no-op: moving_platform_node.py now drives the platform on a…, node : rclpy.node.Node The owning node, used to create subscriptions/publishers., A platform location (default: the hard-coded one), expressed in PX4's local NED… (+4 more)

### Community 17 - "moving_platform_node.py"
Cohesion: 0.07
Nodes (27): bisect, main(), MovingPlatformNode, Node, Seconds on the ROS clock. Wall time by default; SIM time with `-p…, Block briefly until self._now() is reporting real time, not an as-yet-…, Publishes the moving platform's ground-truth state (PlatformState, the RL…, bearing_deg() (+19 more)

### Community 18 - "VisionLander"
Cohesion: 0.18
Nodes (8): Slide the setpoint toward the target by one control period (a plain jump would…, Fly to a point and wait until the UAV (not just the setpoint) is there. Returns…, Sim ground truth for where the marker is right now (evaluation only, never used…, Called once at search altitude, before the patrol starts., Fly the corners in order, hovering `dwell_time` at each; return "TRACK" the…, Fly to a corner, checking for the marker on every control tick, and logging…, Swapped / sign-flipped north-east axes, judged from the expected vs measured…, VisionLander

### Community 19 - "rl_multi_rotor_landing_sim/src/training_q_learning/src/training_q_learning/utils_multiresolution.py"
Cohesion: 0.18
Nodes (15): discretize_action(), discretize_relative_state(), get_discrete_action_state_from_ros_msg(), get_discrete_rel_states_from_ros_msg(), get_discrete_state_from_ros_msg(), get_latest_cur_step_for_state(), Action, ObservationRelativeState (+7 more)

### Community 20 - "aruco_landing_target_node.py"
Cohesion: 0.10
Nodes (15): cv2, LandingTarget, Generates the ArUco marker image used as the visual landing target on top of…, ArucoLandingTargetNode, build_detector_params(), euler_to_rotation_matrix(), main(), Node (+7 more)

### Community 21 - "QLearning"
Cohesion: 0.11
Nodes (12): ndarray, QLearning, Function scales the values of a Q-table. Two options are available. - Mode…, Function adds num_ref_steps new curriculum steps to the sequential curriculum…, Function resets table values to predefined integer value., Function creates a numpy.ndarray that can be indexed according to a…, Class contains different functions to perform RL training for landing a multi-…, Function sets up the training environment and performs intial reset (+4 more)

### Community 22 - "MovingPlatformLander"
Cohesion: 0.17
Nodes (7): MovingPlatformLander, The predictor's view of the platform at `now + ahead`: (Prediction, H) or…, TargetState from the predictor for the blind stretch (None = fall back to the…, Climb toward where the platform should be NOW (constant-velocity prediction) in…, The fake world's TILT model (tests/fake_world.py, max_accel=...): a body-fixed…, test_tilt(), sweep()

### Community 23 - "ViconInterface"
Cohesion: 0.13
Nodes (10): Convert quaterion defined in ENU frame to NED frame, Convert PoseStamped message from ENU to NED frame., Converts twist stamped message from ENU frame to NED frame., Publishes auxposition, auxvelocity in NED frame only when a new message was…, Function stores the pose and twist information together with the reference…, Reads vicon drone pose message, performs the frame conversion from ENU to NED…, Reads vicon drone pose message, performs the frame conversion from ENU to NED…, Reads vicon moving platform pose message, performs the frame conversion from… (+2 more)

### Community 24 - "LogTraining"
Cohesion: 0.13
Nodes (11): Function sets up the logging system for the training environment. It handles…, create_log_dir_path(), LogTraining, Function saves numpy.ndarrays that are used in the context of Q-learning. Array…, Function saves the training and logging data, Function saves the logging data, Function handles the logging of data at the end of each episode., Class contains functions for printing out training information and for data… (+3 more)

### Community 25 - "LandingEnv"
Cohesion: 0.14
Nodes (8): LandingEnv, Node, Apply one discrete action, advance one control period, and return (state,…, Spin this node's callbacks for approximately duration_sec, so subscription…, Reset the episode: sample a target pose, fly there for real and hold (position-…, Call at the start of every episode., Returns (done: bool, outcome: str, success: bool). outcome is one of:…, TerminationManager

### Community 26 - "vicon_compute_relative_state_moving_platform_drone.py"
Cohesion: 0.10
Nodes (18): tf2_geometry_msgs, compute_landing_simulation_object_state_msg(), compute_relative_pos_msg(), compute_relative_vel_msg(), PoseTwistAccelerationState, This scripts defines a ROS node that provides information about the moving…, Reads pose message of moving platform and stores data in storage class., Reads twist message of moving platform and stores data in storage class. (+10 more)

### Community 27 - "ViconDebug"
Cohesion: 0.14
Nodes (9): Converts twist stamped message from ENU frame to NED frame., Class containing debugging functions and required variables, Reads vicon drone pose message., Reads state estimate drone pose message., Reads vicon drone twist message., Reads state estimate drone twist message., Convert quaterion defined in ENU frame to NED frame?, Convert PoseStamped message from ENU to NED frame. (+1 more)

### Community 28 - "compute_relative_state_moving_platform_drone.py"
Cohesion: 0.10
Nodes (17): compute_landing_simulation_object_state_msg(), compute_relative_acc_msg(), compute_relative_pos_msg(), compute_relative_vel_msg(), PoseTwistAccelerationState, Function reads drone imu message and saves it to data class of drone., Function reads moving platform imu message and saves it to data class of moving…, Function computes the relative velocity vector between the moving platform and… (+9 more)

### Community 29 - "math"
Cohesion: 0.05
Nodes (54): concurrent_futures, math, sys, torch, torch_nn, torch_nn_functional, _chunk(), make_dataset() (+46 more)

### Community 30 - "get_publisher"
Cohesion: 0.13
Nodes (6): CascadedPIDInterface, Class for setting up a gym based training environment that can be used in…, get_publisher(), _get_subscribers(), Function gets a publisher and returns an error if the publisher is not up.…, Function gets the list of subscribers to a topic. Source:…

### Community 31 - "rospy"
Cohesion: 0.11
Nodes (22): geometry_msgs_msg, mav_msgs_msg, rospy, tf2_ros, tf_transformations, training_q_learning_msg, uav_msgs_msg, This scripts defines a conversion node that converts messages of type… (+14 more)

### Community 32 - "rl_multi_rotor_landing repository (paper code)"
Cohesion: 0.14
Nodes (15): Cascaded PI controller baseline, Sequential curriculum training procedure, rl_multi_rotor_landing_gcs catkin workspace, LibrePilot Ground Control Station, moving_platform_control package (model train on rails), Goldschmid & Ahmad paper (Autonomous Robots 2024), rl_multi_rotor_landing repository (paper code), RotorS + ROS Noetic + Gazebo 11 stack (+7 more)

### Community 33 - "rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_multiresolution.py"
Cohesion: 0.18
Nodes (15): discretize_action(), discretize_relative_state(), get_discrete_action_state_from_ros_msg(), get_discrete_rel_states_from_ros_msg(), get_discrete_state_from_ros_msg(), get_latest_cur_step_for_state(), Action, ObservationRelativeState (+7 more)

### Community 34 - "observation_generator.py"
Cohesion: 0.12
Nodes (15): compute_observation_action_msg(), compute_relative_observation_msg(), This script defines a ROS node that computes the relative information between…, Function sets a flag when the simulation is reset., Function reads the relative position message and stores the message in the…, Function reads the relative velocity message and stores the message in the…, Function reads the relative acceleration message and stores the message in the…, Function reads the setpoints for the action values of the drone. (+7 more)

### Community 35 - "TargetTracker"
Cohesion: 0.21
Nodes (4): Low-pass estimate of how fast the fitted velocity vector's HEADING is rotating…, True if a sample ARRIVED within the last `max_age` seconds., t = when the marker was SEEN (capture time); received = when the sample arrived…, TargetTracker

### Community 36 - "MovingLandingConfig"
Cohesion: 0.19
Nodes (11): main(), parse_corner(), Phase 3b: camera-guided landing on a MOVING platform (circular motion) -- one…, main(), parse_corner(), Phase 3: camera-guided landing on a MOVING platform (straight-line motion) --…, MovingLandingConfig, Like run_random_sweep but for any platform function. Returns (share within 0.75… (+3 more)

### Community 37 - "--fast higher-bandwidth gain profile"
Cohesion: 0.14
Nodes (16): CLAUDE.md project instructions, FakeWorld offline harness (not PX4 physics, no attitude), Real-hardware target: car roof >= 5 km/h (1.39 m/s), Offline test suite (tests.test_missions), Judge landings by TRUE offset, not predicted-position line, Validated status table (2026-10-14), --fast higher-bandwidth gain profile, tracker_max_speed decoupled from UAV max_speed (flight-safety fix) (+8 more)

### Community 38 - "LSTM-MDN predictor (mixture of K=5 bivariate Gaussians)"
Cohesion: 0.27
Nodes (10): --mdn / --mdn-point / --mdn-gate flags, prediction/ package (Phase 4 LSTM-MDN), datagen.py (synthetic tracks: train/val/heldout), evaluate.py (MDN vs CV vs tracker CTRV), LSTM-MDN predictor (mixture of K=5 bivariate Gaussians), --mdn-gate uncertainty descent gate (negative result), mdn_numpy.py (pure-numpy mission inference), --mdn-point peak (densest mixture point) (+2 more)

### Community 39 - "vicon_observation_generator.py"
Cohesion: 0.13
Nodes (14): sensor_msgs_msg, compute_observation_action_msg(), compute_relative_observation_msg(), This script defines a ROS node that computes the relative information between…, Function reads the relative position message and stores the message in the…, Function reads the relative velocity message and stores the message in the…, Function reads the relative acceleration message and stores the message in the…, Function reads the setpoints for the action values of the drone. (+6 more)

### Community 40 - "write_data_to_csv"
Cohesion: 0.19
Nodes (6): LogTopicFreqs, This is a variation of the create_log_dir_path_function in the utils script.…, LogTopicFreqs, This is a variation of the create_log_dir_path_function in the utils script.…, Functions writes a list of values as a row to a .csv file., write_data_to_csv()

### Community 41 - "SmoothPlatformData"
Cohesion: 0.19
Nodes (5): OneEuroFilter, Function stores the pose and twist data of the platform received via the vicon…, Initialize the one euro filter. Based on https://jaantollander.com/post/noise-…, Compute the filtered signal., SmoothPlatformData

### Community 42 - "ViconEnv"
Cohesion: 0.19
Nodes (7): Function maps an action integer number to an action string, updates the new…, Function resets the training environment and updates logging data, Function sends out a boolean value indicating that a reset has been requested.…, Function performs the normalization of observations of the environment and…, Function publishes the action values that are currently set to the ROS network., Function performs one time step for when two instances of the same agent are…, ViconEnv

### Community 43 - "ViconObject"
Cohesion: 0.14
Nodes (8): Class for setting up a gym based training environment that can be used in…, Function reads observation from corresponding topic and updates old observation…, Function checks episode termination status and generates the appropriate reward., Publication of the current discrete state to the ROS environment., Function reads the current state of the drone whenever triggered by the…, Functions reads the continouos observations of the environment whenever the…, Function checks whether or not the episode has to be terminated or not. It can…, ViconObject

### Community 44 - "StateDiscretizer"
Cohesion: 0.24
Nodes (5): State Discretizer Converts continuous observations (an…, Build discretization limits for every observation according to the current…, Convert one continuous value into a discrete bin index (evenly-spaced bins over…, Convert a continuous observation into a discrete state tuple. `observation`…, StateDiscretizer

### Community 45 - "ament_flake8_main"
Cohesion: 0.15
Nodes (10): ament_flake8_main, flake8, linter, test_flake8(), flake8, linter, test_flake8(), flake8 (+2 more)

### Community 46 - "get_publisher"
Cohesion: 0.08
Nodes (9): CascadedPIDData, CascadedPIDInterface, FlightActivated, Class stores information RL controlled flight is activated., Reads the status of the ROS controlled parameters and stores the value in the…, get_publisher(), _get_subscribers(), Function gets a publisher and returns an error if the publisher is not up.… (+1 more)

### Community 47 - "interfaces ament package"
Cohesion: 0.17
Nodes (12): LandingCommand.msg, LandingTarget.msg, interfaces ament package, PlatformState.msg, RLObservation.msg, TakeoffSetpoint.msg, UAVState.msg, landing_controller_node (position/velocity modes) (+4 more)

### Community 48 - "LandingController"
Cohesion: 0.11
Nodes (9): px4_msgs_msg, rclpy_qos, LandingController, main(), Node, Switch PX4 into its own AUTO.LAND flight mode instead of us trying to fake a…, main(), Node (+1 more)

### Community 49 - "ActionManager"
Cohesion: 0.17
Nodes (7): ActionManager, node : rclpy.node.Node The owning node, used to create the publisher.…, Reset actions to their initial values., Update action values using the discrete action selected by the RL agent. Only…, Publish the current control command., Return the current action values., Handles UAV actions. Responsibilities ---------------- - Maintain current…

### Community 50 - "training.py"
Cohesion: 0.29
Nodes (5): roslaunch, training_q_learning_custom_q_learning, Script creates the simulation environment that is required in order to use 4…, This script starts a training session., This script starts a training session.

### Community 51 - "moving_landing.py (lock/track/touchdown loop)"
Cohesion: 0.22
Nodes (9): circular_landing_main.py (motion-agnostic, --fast), moving_landing_main.py (linear, default gains), moving_landing.py (lock/track/touchdown loop), --no-ground-truth flag, One-way platform motion cannot be caught by patrol, vision_landing.py (patrol, base class), Camera latency compensation (camera_latency 0.35 s default, 0.09 s measured), Mission states PATROL / TRACK / LAND / RECOVER (+1 more)

### Community 53 - "Phase 3: moving platform (linear and circular)"
Cohesion: 0.21
Nodes (15): target_tracker.py (velocity fit, reversal detection, CTRV), Anchor back-and-forth motion to a patrol leg, Blind final metre (marker out of view below ~1 m), Curvature-aware (CTRV) tracker extrapolation, Double Q-learning RL agent (earlier work), Goldschmid & Ahmad RL moving-platform landing paper, --kz 3.0 vertical gain, Phase 1: landing on hard-coded platform coordinates (+7 more)

### Community 55 - "rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/parameters.py"
Cohesion: 0.23
Nodes (7): This script contains the parameters to set up a training case…, Class provides data about the vehicle, Class provides parameter affecting the training and values generated from the…, Class provides variables that affect the reinforcement learning algorithm and…, RLParameters, SimulationParameters, UAVParameters

### Community 56 - "Parameters"
Cohesion: 0.22
Nodes (8): Parameters, This script contains the parameters to set up a training case…, Class provides data about the vehicle, Class provides parameter affecting the training and values generated from the…, Class provides variables that affect the reinforcement learning algorithm and…, RLParameters, SimulationParameters, UAVParameters

### Community 57 - "grid_utils.py"
Cohesion: 0.21
Nodes (10): Create: Q(s,a) DoubleQ(s,a) VisitCounter(s,a), create_double_q_tables(), create_empty_q_table(), create_visit_counter(), initialize_grid_list(), Grid utilities. This module contains helper functions used for multi-resolution…, Create a nested numpy array whose shape matches the discretization grid.…, Create an empty Q-table. The last dimension corresponds to actions. (+2 more)

### Community 58 - "config/parameters.py"
Cohesion: 0.23
Nodes (7): Parameters for the uav_rl_landing training case. Ported from the original…, # NOTE: there is no contact sensor wired up yet (no Gazebo contact, Vehicle / action-space configuration., Reinforcement-learning / curriculum configuration., RLParameters, SimulationParameters, UAVParameters

### Community 59 - "patch_x500_camera.py"
Cohesion: 0.26
Nodes (11): argparse, Path, re, find_link_anchor(), find_model_sdf(), _is_file_safe(), main(), patch() (+3 more)

### Community 60 - "main"
Cohesion: 0.25
Nodes (8): copyright, linter, skip, test_copyright(), build_detector_params(), main(), Standalone sanity check for the ArUco detection logic in…, Same tuning as aruco_landing_target_node.py's build_detector_params() -- see…

### Community 61 - "ros_io.py"
Cohesion: 0.17
Nodes (14): collections, dataclasses, rclpy, main(), measure_camera_latency.py Measures the delay between a camera image being taken…, moving_landing.py Phase 3 mission: land on a platform that MOVES (straight…, ros_io.py ROS 2 implementation of the `io` interface that…, fit_camera_latency() (+6 more)

### Community 62 - "add_cur_step_lims_of_state"
Cohesion: 0.33
Nodes (4): Function implements the Double Q-learning algorithm presented in…, Class contains information about the training such as reward computation,…, add_cur_step_lims_of_state(), Function reads the limit value for the different discretization steps defined…

### Community 63 - "moving_platform_node (publishes /platform/state, drives Gazebo model)"
Cohesion: 0.32
Nodes (8): Real-time-factor mismatch / sim-time ground truth drift, Linear motion (travel_length back-and-forth), moving_platform_node (publishes /platform/state, drives Gazebo model), platform_tracker live trajectory dashboard, Random motion (motion:=random, car-like smooth path), trajectories.py (circular_state, linear_state, random_state), use_sim_time with bridged /clock, wait_for_start signal on /moving_platform/start

### Community 64 - "LogTraining"
Cohesion: 0.15
Nodes (9): Function sets up the logging system for the training environment. It handles…, LogTraining, Function saves the training and logging data, Function saves the logging data, Function handles the logging of data at the end of each episode., Class contains functions for printing out training information and for data…, Function performs operation that is executed in each timestep., Function prints info to the terminal when verbose is set to true. (+1 more)

### Community 65 - "world_base_link_transform_publisher.py"
Cohesion: 0.24
Nodes (8): PositionOrientationState, publish_transform_message(), publish_world_to_world_link_transform_message(), Class for storing the current position and orientation of the moving platform, Read model state of moving platform., Function publishes the required tf transform from world frame to an additional…, Publish the transformation message to describe the motion of the moving…, read_model_state()

### Community 66 - "linear_state"
Cohesion: 0.22
Nodes (10): linear_state(), Straight-line motion at constant speed from (start_x, start_y). heading_deg is…, What it does and why, The bug found in the first Gazebo run: uncompensated camera latency corrupts…, KEY FINDING (from a real Gazebo run + this fake world's takeoff timing…, Same mission, run n times with the platform's clock offset by increasing…, run_moving(), run_moving_jitter() (+2 more)

### Community 67 - "landing_env.py"
Cohesion: 0.18
Nodes (5): interfaces_msg, Reinforcement learning environment for UAV landing on a moving platform. This…, reset_manager.py Handles episode reset / takeoff logic. Flow per episode…, Computes the reinforcement learning reward. This class contains the complete…, RewardManager

### Community 68 - "ament_pep257_main"
Cohesion: 0.22
Nodes (7): ament_pep257_main, linter, pep257, test_pep257(), linter, pep257, test_pep257()

### Community 69 - "landing_controller/test/test_flake8.py"
Cohesion: 0.50
Nodes (3): flake8, linter, test_flake8()

### Community 70 - "state_publisher.cpp"
Cohesion: 0.22
Nodes (5): jointstate, model, ros, string, transform_broadcaster

### Community 71 - "generate_changelog.sh"
Cohesion: 0.42
Nodes (8): contributors(), emit(), forthcoming_block(), generate(), join_csv(), names(), generate_changelog.sh script, underline()

### Community 72 - "moving_platform/test/test_flake8.py"
Cohesion: 0.50
Nodes (3): flake8, linter, test_flake8()

### Community 73 - "test_circular"
Cohesion: 0.25
Nodes (8): circular_state(), Counter-clockwise circle; at t=0 the platform is at (center_x + radius,…, _locked_at(), Timestamp of the "LOCKED on the platform" log line, or None if it never locked.…, Phase 3b (circular motion). The control loop itself…, test_circular(), _jitter_sweep(), _peak_estimate_speed()

### Community 74 - "ActionToUavPose"
Cohesion: 0.29
Nodes (5): ActionMsg, ActionToUavPose, Class stores all data that is required to convert roll pitch yawrate thrust to…, Funcion assigns the values of roll, pitch and yaw to the velocity field of the…, Function processes the msgs received on the topic

### Community 76 - "test_copyright"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 78 - "test_pep257"
Cohesion: 0.50
Nodes (3): linter, pep257, test_pep257()

### Community 79 - "publish_stability_axes.py"
Cohesion: 0.33
Nodes (6): nav_msgs_msg, publish_stability_axes_as_tf_frame(), Function publishes the stability axes as tf frame. The stability axes xy-plane…, Function publishes the stability axes frame w.r.t. the world frame., Function reads the odometry messages of the drone and triggers publishing of…, read_odom_msg()

### Community 80 - "rclpy_node"
Cohesion: 0.25
Nodes (4): rclpy_node, main(), Node, RelativeStateNode

### Community 81 - "vision_relative_state_node.py"
Cohesion: 0.25
Nodes (4): main(), Node, Vision-based drop-in alternative to relative_state package's…, VisionRelativeStateNode

### Community 82 - "training_q_learning catkin package (simulation)"
Cohesion: 0.33
Nodes (6): training_q_learning catkin package (GCS/Vicon), Vicon scripts (vicon_interface, vicon_test_model_2D, vicon_cascaded_pid_controller, ...), training_q_learning catkin package (simulation), ResetRandomSeed.srv, Custom ROS messages (Action, ObservationRelativeState, TwistModified, LandingSimulationObjectState), Simulation scripts (training.py, observation_generator.py, test_model_2D.py, cascaded_pid_controller.py, ...)

### Community 83 - "UAVPoseFromStateEstimate"
Cohesion: 0.40
Nodes (3): Class stores all data that is required to convert roll pitch yawrate thrust to…, Function processes the msgs received on the topic, UAVPoseFromStateEstimate

### Community 84 - "run_sim_terminals.sh"
Cohesion: 0.60
Nodes (5): find_terminal(), open_terminal(), run_sim_terminals.sh script, start_all(), stop_all()

### Community 85 - "PositionHistory"
Cohesion: 0.29
Nodes (3): PositionHistory, Recent UAV (t, x, y) samples, so a camera measurement can be combined with…, UAV position at time t (linear interpolation; clamped to the ends), or None if…

### Community 87 - "ObservationRelativeState"
Cohesion: 0.40
Nodes (3): ObservationRelativeState, Class stores the relative position, relative velocity, relative acceleration…, Function checks if all sensor values are provided in the same reference frame.

### Community 88 - "FlightActivated"
Cohesion: 0.40
Nodes (3): FlightActivated, Class stores information RL controlled flight is activated., Reads the status of the ROS controlled parameters and stores the value in the…

### Community 89 - "publish_vmp_x.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, publish_vmp_x.sh script

### Community 90 - "publish_vmp_y.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, publish_vmp_y.sh script

### Community 91 - "launch_action_interface.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_action_interface.sh script

### Community 92 - "launch_analysis_node_2D.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_analysis_node_2D.sh script

### Community 93 - "launch_cascaded_pid_environment_in_virtual_screens.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_cascaded_pid_environment_in_virtual_screens.sh script

### Community 94 - "launch_cascaded_pid_interface.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_cascaded_pid_interface.sh script

### Community 95 - "launch_compute_relative_information.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_compute_relative_information.sh script

### Community 96 - "launch_environment_in_virtual_screens.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_environment_in_virtual_screens.sh script

### Community 97 - "launch_landing_simulation.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_landing_simulation.sh script

### Community 98 - "launch_observation_generator.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_observation_generator.sh script

### Community 99 - "launch_publish_stability_axes.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_publish_stability_axes.sh script

### Community 100 - "launch_test_model_2D.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_test_model_2D.sh script

### Community 101 - "launch_training.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_training.sh script

### Community 102 - "moving_platform_description catkin package"
Cohesion: 0.40
Nodes (5): parser executable, moving_platform_description catkin package, state_publisher executable, command_moving_platform_trajectories.py and world_base_link_transform_publisher.py, JointStateController config (50 Hz)

### Community 103 - "generate_release_notes.sh"
Cohesion: 0.70
Nodes (4): decls(), header(), namelist(), generate_release_notes.sh script

### Community 105 - "vision_landing.py"
Cohesion: 0.33
Nodes (6): Exception, typing, MissionTimeout, vision_landing.py Phase 2 mission: take off, SEARCH for the platform's ArUco…, No fresh /uav/state for too long -- almost always a crashed or hung PX4/Gazebo,…, TelemetryStalled

### Community 106 - "rl_multi_rotor_landing_gcs/other_files/setup.bash"
Cohesion: 0.50
Nodes (3): setup.bash script, ROS_PACKAGE_PATH, ROS_PROJECT_ROOT

### Community 107 - "initialize_grid_list"
Cohesion: 0.50
Nodes (3): Function creates a numpy.ndarray that can be indexed according to a…, initialize_grid_list(), The grid list can be initialized using this function. It will create a nested…

### Community 109 - "rl_multi_rotor_landing_sim/other_files/setup.bash"
Cohesion: 0.50
Nodes (3): setup.bash script, ROS_PACKAGE_PATH, ROS_PROJECT_ROOT

### Community 110 - "test_copyright"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 111 - "test_pep257"
Cohesion: 0.50
Nodes (3): linter, pep257, test_pep257()

### Community 113 - "test_pep257"
Cohesion: 0.50
Nodes (3): linter, pep257, test_pep257()

### Community 114 - "test_copyright"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 117 - "test_copyright"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 118 - "README.md project write-up"
Cohesion: 0.22
Nodes (10): README.md project write-up, moving_platform README, vision_node README, aruco_landing_target_node (ArUco DICT_4X4_50 id 0 detector), CAMERA_TO_BODY frame convention, Choices that matter, Commands, prediction/ — LSTM-MDN platform-motion predictor (Phase 4) (+2 more)

### Community 119 - "fyp-uav docker compose service"
Cohesion: 0.67
Nodes (3): /dev/dri GPU passthrough with render group (RENDER_GID), fyp-uav docker compose service, Workspace volume mounts (/workspace, /gazebo, /datasets, /docs)

### Community 128 - "Issue template chooser config"
Cohesion: 0.67
Nodes (3): Bug report issue template, Issue template chooser config, Feature request issue template

### Community 129 - "test_random"
Cohesion: 0.20
Nodes (9): The target's estimated state at time `now`, or None if there is no data or the…, TargetState, jitter_and_mission_time(), Mission against random_state paths, one seed per run (the seed IS the arrival…, --fast on a 1 m/s random path: (mean RMS of the horizontal command's high-…, Phase 3c: a randomly moving platform (moving_platform/trajectories.py's…, run_random_sweep(), truth_state() (+1 more)

## Knowledge Gaps
- **133 isolated node(s):** `archive_training_results.sh script`, `init_workspaces.sh script`, `kill_vicon.sh script`, `prepare_terminal_window.sh script`, `record_rosbag.bash script` (+128 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 774 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **36 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Camera latency compensation (camera_latency 0.35 s default, 0.09 s measured)` connect `moving_landing.py (lock/track/touchdown loop)` to `ros_io.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `main()` connect `main` to `ament_pep257_main`, `test_copyright`, `test_copyright`, `test_pep257`, `test_pep257`, `test_pep257`, `test_copyright`, `test_copyright`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `moving_landing.py (lock/track/touchdown loop)` connect `moving_landing.py (lock/track/touchdown loop)` to `Phase 3: moving platform (linear and circular)`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `RosMissionIO` (e.g. with `Parameters` and `ResetManager`) actually correct?**
  _`RosMissionIO` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `MovingPlatformLander` (e.g. with `TargetState` and `TargetTracker`) actually correct?**
  _`MovingPlatformLander` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `archive_training_results.sh script`, `init_workspaces.sh script`, `kill_vicon.sh script` to the rest of the system?**
  _133 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `landing_simulation_env.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1024390243902439 - nodes in this community are weakly interconnected._