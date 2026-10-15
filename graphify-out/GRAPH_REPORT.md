# Graph Report - FYP_UAV  (2026-10-15)

## Corpus Check
- 181 files · ~104,225 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 377 file(s) not represented in the graph (top: .msg 275, .launch 34, (none) 21)

## Summary
- 1570 nodes · 2451 edges · 151 communities (110 shown, 41 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 92 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5426c3b1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- vicon_observation_generator.py
- RosMissionIO
- LandingSimulationObject
- numpy
- LandingSimulationEnv
- QLearning
- AnalysisNode
- rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_multiresolution.py
- q_learning.py
- Vicon Launch Scripts
- Platform Trajectory Generator
- MovingPlatformLander
- landing_simulation_env.py
- px4_msgs Contributing guide and release process
- .setup_logging_system
- os
- ResetManager
- moving_landing.py
- FakeWorld
- test_missions.py
- RewardManager
- ArucoLandingTargetNode
- QLearning
- ViconInterface
- ros_io.py
- ViconDebug
- rl_multi_rotor_landing repository (paper code)
- TargetTracker
- SmoothPlatformData
- compute_relative_state_moving_platform_drone.py
- Moving-platform landing mission (lock / track / touchdown)
- rl_multi_rotor_landing_sim/src/training_q_learning/src/training_q_learning/utils_multiresolution.py
- initialize_grid_list
- ament_flake8_main
- ament_pep257_main
- extract_flights_from_rosbag_topics.py
- TargetTracker
- ViconEnv
- interfaces ament package
- LandingController
- moving_platform_node.py
- landing_env.py
- patch_x500_camera.py
- rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/parameters.py
- rl_multi_rotor_landing_sim/src/training_q_learning/src/training_q_learning/parameters.py
- .__init__
- LandingEnv
- rospy
- StateDiscretizer
- Linear 5 km/h with --fast and travel_length=50
- Project Atlas (README)
- LogTraining
- state_publisher.cpp
- moving_platform_node
- generate_changelog.sh
- ActionToUavPose
- Gotchas (RTF, ground truth, FakeWorld limits, travel_length)
- VisionLander
- setuptools
- plot_topic_freq_from_flight.py
- trajectories.py
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
- observation_generator.py
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
- rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_q_learning.py
- rl_multi_rotor_landing_gcs/other_files/setup.bash
- vicon_action_to_uavpose.py
- training_action_interface.py
- ViconObject
- clear_all_sims.sh script
- rl_multi_rotor_landing_sim/other_files/setup.bash
- test_copyright
- test_pep257
- test_copyright
- test_copyright
- test_random
- main
- test_copyright
- vision_node/test/test_flake8.py
- test_pep257
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
- TelemetryStalled
- initialize_grid_list
- moving_platform/test/test_flake8.py
- vision_landing_main.py
- .drain_samples
- .relative_measurement
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
1. `RosMissionIO` - 37 edges
2. `FakeWorld` - 32 edges
3. `Parameters` - 24 edges
4. `VisionLander` - 24 edges
5. `MovingPlatformLander` - 23 edges
6. `ResetManager` - 20 edges
7. `LandingEnv` - 19 edges
8. `Parameters` - 18 edges
9. `TrajectoryGenerator` - 17 edges
10. `MovingLandingConfig` - 17 edges

## Surprising Connections (you probably didn't know these)
- `FakeWorld offline harness (fake_world.py, test_missions.py)` --conceptually_related_to--> `Offline FakeWorld test harness`  [INFERRED]
  CLAUDE.md → README.md
- `--fast control profile (higher-bandwidth gains)` --conceptually_related_to--> `--fast profile (kp=3.0, max_accel=5.0, max_speed=4.0, tracker_window=0.6)`  [INFERRED]
  README.md → workspace/ros2_ws/src/vision_node/README.md
- `use_sim_time / real-time-factor (RTF) finding` --conceptually_related_to--> `Simulation speed: use_sim_time and /clock bridge`  [INFERRED]
  README.md → workspace/ros2_ws/src/vision_node/README.md
- `CLAUDE.md (Project Atlas instructions)` --references--> `Project Atlas (README)`  [EXTRACTED]
  CLAUDE.md → README.md
- `ArUco marker detection` --conceptually_related_to--> `ArUco detection (DICT_4X4_50, marker id 0, solvePnP)`  [INFERRED]
  README.md → workspace/ros2_ws/src/vision_node/README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **px4_msgs automated release pipeline** — workspace_ros2_ws_src_px4_msgs_github_workflows_create_release, workspace_ros2_ws_src_px4_msgs_github_workflows_package, workspace_ros2_ws_src_px4_msgs_github_workflows_release, workspace_ros2_ws_src_px4_msgs_github_workflows_release_bloom [EXTRACTED 1.00]
- **ROS 2 landing pipeline: px4_bridge -> relative_state -> RL agent -> landing_controller** — workspace_uav_rl_landing_readme_px4_bridge_uav_state_node, workspace_uav_rl_landing_readme_relative_state_node, workspace_uav_rl_landing_agent_q_learning, workspace_uav_rl_landing_readme_landing_controller_node [EXTRACTED 1.00]
- **px4_msgs quality assurance gates (CI, pre-commit, quality declaration)** — workspace_ros2_ws_src_px4_msgs_github_workflows_build, workspace_ros2_ws_src_px4_msgs_pre_commit_config, workspace_ros2_ws_src_px4_msgs_quality_declaration, workspace_ros2_ws_src_px4_msgs_github_dependabot [INFERRED 0.75]
- **5 km/h hardware-target enablers: --fast profile, tracker_max_speed fix, hysteresis fix, low camera latency** — workspace_ros2_ws_src_vision_node_readme_fast_profile, workspace_ros2_ws_src_vision_node_readme_tracker_max_speed_fix, workspace_ros2_ws_src_vision_node_readme_alignment_hysteresis_fix, workspace_ros2_ws_src_vision_node_readme_low_absolute_latency_finding, readme_five_kmh_hardware_target [INFERRED 0.85]
- **Moving-platform landing flow: patrol, ArUco lock, tracker-driven tracking, velocity-matched touchdown** — readme_patrol_search, readme_aruco_detection, readme_target_tracker, readme_moving_platform_landing_mission, readme_velocity_matched_touchdown [INFERRED 0.85]
- **RTF drift cluster: wall-clock platform node, ground-truth mismatch, false abort, trusted contact line** — readme_use_sim_time_rtf_finding, readme_false_estimate_mismatch_abort, claude_no_ground_truth_flag, claude_contact_line_trust_rule, workspace_ros2_ws_src_moving_platform_readme_use_sim_time_clock [INFERRED 0.85]

## Communities (151 total, 41 thin omitted)

### Community 0 - "vicon_observation_generator.py"
Cohesion: 0.13
Nodes (14): sensor_msgs_msg, compute_observation_action_msg(), compute_relative_observation_msg(), This script defines a ROS node that computes the relative information between…, Function reads the relative position message and stores the message in the…, Function reads the relative velocity message and stores the message in the…, Function reads the relative acceleration message and stores the message in the…, Function reads the setpoints for the action values of the drone. (+6 more)

### Community 1 - "RosMissionIO"
Cohesion: 0.08
Nodes (7): Switch landing_controller to velocity setpoints. It only streams offboard…, Sim ground truth from /platform/state, converted to PX4 local NED: (north,…, True if no RAW PX4 message (/fmu/out/vehicle_local_position_v1) has arrived in…, (messages, of which detected) received on /landing_target in the last `window`…, Mean absolute marker (x, y) over the latest few FRESH detections, or None if…, Check the pipeline is up before arming anything. Same lesson as Phase 1: a…, RosMissionIO

### Community 2 - "LandingSimulationObject"
Cohesion: 0.05
Nodes (21): LandingSimulationObjectState, ObservationRelativeStateMsg, CascadedPIDData, CascadedPIDInterface, Class for setting up a gym based training environment that can be used in…, LandingSimulationObject, Bool, ContactsState (+13 more)

### Community 3 - "numpy"
Cohesion: 0.14
Nodes (12): csv, numpy, os_path, pandas, rosbag, socketserver, This scrips extracts topics from rosbag files that are required for further…, This script can be used to plot the frequencies of the ROS topics that were… (+4 more)

### Community 4 - "LandingSimulationEnv"
Cohesion: 0.08
Nodes (16): LogTopicFreqs, This is a variation of the create_log_dir_path_function in the utils script.…, LogTopicFreqs, This is a variation of the create_log_dir_path_function in the utils script.…, LandingSimulationEnv, Bool, Function maps an action integer number to an action string, updates the new…, Function resets the training environment and updates logging data (+8 more)

### Community 5 - "QLearning"
Cohesion: 0.12
Nodes (10): ndarray, QLearning, Function scales the values of a Q-table. Two options are available. - Mode…, Function adds num_ref_steps new curriculum steps to the sequential curriculum…, Function resets table values to predefined integer value., Class contains different functions to perform RL training for landing a multi-…, Function sets up the training environment and performs intial reset, Function implements the Double Q-learning algorithm presented in… (+2 more)

### Community 6 - "AnalysisNode"
Cohesion: 0.07
Nodes (18): AnalysisNode, Function publishes basic statistics over the ROS framework for the movement in…, Function publishes basic statistics over the ROS framework for the movement in…, Function logs and computes basic statistics for motion in x-direction., Function logs and computes basic statistics for motion in y-direction., Function prints statistics to the terminal window, Function reads the current discrete states of the longitudinal motion., Function reads the current discrete states of the lateral motion. (+10 more)

### Community 7 - "rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_multiresolution.py"
Cohesion: 0.18
Nodes (15): discretize_action(), discretize_relative_state(), get_discrete_action_state_from_ros_msg(), get_discrete_rel_states_from_ros_msg(), get_discrete_state_from_ros_msg(), get_latest_cur_step_for_state(), Action, ObservationRelativeState (+7 more)

### Community 8 - "q_learning.py"
Cohesion: 0.09
Nodes (17): ExplorationManager, Choose action using epsilon-greedy policy., Update epsilon according to schedule., Restore epsilon from checkpoint., Current exploration rate., Handles epsilon-greedy exploration., build_grid(), main() (+9 more)

### Community 9 - "Vicon Launch Scripts"
Cohesion: 0.07
Nodes (20): src_rl_multi_rotor_landing_rl_multi_rotor_landing_gcs_other_files_setup_bash, ROS_IP, launch_audio_feedback.sh script, ROS_IP, launch_vicon_action_to_uavpose.sh script, launch_vicon_compute_relative_information.sh script, ROS_IP, launch_vicon_filter_platform_data.sh script (+12 more)

### Community 10 - "Platform Trajectory Generator"
Cohesion: 0.08
Nodes (16): Function computes a straight trajectory for the moving platform., Function computes a rectiliar periodic trajectory for the moving platform., Function computes a vertical, straight trajectory for the moving platform, Function computes a rectiliar periodic trajectory., Function computes the trajectory based on arguments trajectory_type,…, Function publishes the updated platform position to the ROS network., Function resets time to a random value within an interval of episode_length…, Function handles the service request to reset the seed for the random number… (+8 more)

### Community 11 - "MovingPlatformLander"
Cohesion: 0.12
Nodes (20): circular_state(), Counter-clockwise circle; at t=0 the platform is at (center_x + radius,…, main(), parse_corner(), Phase 3b: camera-guided landing on a MOVING platform (circular motion) -- one…, main(), parse_corner(), Phase 3: camera-guided landing on a MOVING platform (straight-line motion) --… (+12 more)

### Community 12 - "landing_simulation_env.py"
Cohesion: 0.11
Nodes (24): copy, gym, gym_envs_registration, std_srvs_srv, training_q_learning_parameters, training_q_learning_utils_multiresolution, training_q_learning_utils_q_learning, This scripts defines a conversion node that converts messages of type… (+16 more)

### Community 13 - "px4_msgs Contributing guide and release process"
Cohesion: 0.14
Nodes (26): px4_msgs CHANGELOG (tracks PX4 release lines 1.16, 1.17), px4_msgs CMakeLists.txt, rosidl_generate_interfaces (msg/srv glob to C++/Python/IDL), px4_msgs Code of Conduct, px4_msgs Contributing guide and release process, DCO sign-off and Conventional Commits policy, Dependabot config (github-actions updates), Pull request template (+18 more)

### Community 14 - ".setup_logging_system"
Cohesion: 0.50
Nodes (3): Function sets up the logging system for the training environment. It handles…, create_log_dir_path(), Function determines a unique path where the training data should be stored…

### Community 15 - "os"
Cohesion: 0.07
Nodes (32): fileinput, gazebo_msgs_msg, os, rospkg, rostopic, shutil, time, This script automizes the execution of the evaluation of an agent for all… (+24 more)

### Community 16 - "ResetManager"
Cohesion: 0.09
Nodes (11): Command landing_controller into position-hold mode, targeting `pose`., Publish a new position-hold target without touching the control mode (used to…, True once /uav/state has converged on `pose` within tolerance., Hand control back to the RL agent's velocity commands., Disarm landing_controller (see its "disarm" mode) so the UAV actually sits…, Deliberately a no-op: moving_platform_node.py now drives the platform on a…, node : rclpy.node.Node The owning node, used to create subscriptions/publishers., A platform location (default: the hard-coded one), expressed in PX4's local NED… (+3 more)

### Community 17 - "moving_landing.py"
Cohesion: 0.20
Nodes (13): CLAUDE.md (Project Atlas instructions), circular_landing_main.py (motion-agnostic, --fast), FakeWorld offline harness (fake_world.py, test_missions.py), dataclasses, typing, main(), measure_camera_latency.py Measures the delay between a camera image being taken…, moving_landing.py Phase 3 mission: land on a platform that MOVES (straight… (+5 more)

### Community 19 - "test_missions.py"
Cohesion: 0.13
Nodes (19): collections, random, A fake drone + camera + platform implementing the `io` interface of…, check(), _locked_at(), platform_error(), Offline tests for the vision missions (no ROS / PX4 / Gazebo needed). cd…, KEY FINDING (from a real Gazebo run + this fake world's takeoff timing… (+11 more)

### Community 21 - "ArucoLandingTargetNode"
Cohesion: 0.12
Nodes (12): LandingTarget, ArucoLandingTargetNode, build_detector_params(), euler_to_rotation_matrix(), main(), Node, World-from-body rotation matrix for the 3-2-1 (yaw, pitch, roll) Euler…, True once camera intrinsics are available. If no camera_info shows up within… (+4 more)

### Community 22 - "QLearning"
Cohesion: 0.07
Nodes (19): ndarray, QLearning, Function scales the values of a Q-table. Two options are available. - Mode…, Function adds num_ref_steps new curriculum steps to the sequential curriculum…, Function resets table values to predefined integer value., Function creates a numpy.ndarray that can be indexed according to a…, Class contains different functions to perform RL training for landing a multi-…, Function sets up the logging system for the training environment. It handles… (+11 more)

### Community 23 - "ViconInterface"
Cohesion: 0.13
Nodes (10): Convert quaterion defined in ENU frame to NED frame, Convert PoseStamped message from ENU to NED frame., Converts twist stamped message from ENU frame to NED frame., Publishes auxposition, auxvelocity in NED frame only when a new message was…, Function stores the pose and twist information together with the reference…, Reads vicon drone pose message, performs the frame conversion from ENU to NED…, Reads vicon drone pose message, performs the frame conversion from ENU to NED…, Reads vicon moving platform pose message, performs the frame conversion from… (+2 more)

### Community 24 - "ros_io.py"
Cohesion: 0.23
Nodes (11): interfaces_msg, math, px4_msgs_msg, rclpy, rclpy_node, rclpy_qos, Detects the ArUco marker on the moving platform (see…, Vision-based drop-in alternative to relative_state package's… (+3 more)

### Community 25 - "ViconDebug"
Cohesion: 0.14
Nodes (9): Converts twist stamped message from ENU frame to NED frame., Class containing debugging functions and required variables, Reads vicon drone pose message., Reads state estimate drone pose message., Reads vicon drone twist message., Reads state estimate drone twist message., Convert quaterion defined in ENU frame to NED frame?, Convert PoseStamped message from ENU to NED frame. (+1 more)

### Community 26 - "rl_multi_rotor_landing repository (paper code)"
Cohesion: 0.15
Nodes (14): Cascaded PI controller baseline, Sequential curriculum training procedure, rl_multi_rotor_landing_gcs catkin workspace, LibrePilot Ground Control Station, moving_platform_control package (model train on rails), rl_multi_rotor_landing repository (paper code), RotorS + ROS Noetic + Gazebo 11 stack, rl_multi_rotor_landing_sim catkin workspace (+6 more)

### Community 27 - "TargetTracker"
Cohesion: 0.19
Nodes (4): Low-pass estimate of how fast the fitted velocity vector's HEADING is rotating…, True if a sample ARRIVED within the last `max_age` seconds., t = when the marker was SEEN (capture time); received = when the sample arrived…, TargetTracker

### Community 28 - "SmoothPlatformData"
Cohesion: 0.19
Nodes (5): OneEuroFilter, Function stores the pose and twist data of the platform received via the vicon…, Initialize the one euro filter. Based on https://jaantollander.com/post/noise-…, Compute the filtered signal., SmoothPlatformData

### Community 29 - "compute_relative_state_moving_platform_drone.py"
Cohesion: 0.10
Nodes (18): gazebo_msgs_srv, tf, training_q_learning_srv, compute_landing_simulation_object_state_msg(), compute_relative_acc_msg(), compute_relative_pos_msg(), compute_relative_vel_msg(), Function reads drone imu message and saves it to data class of drone. (+10 more)

### Community 30 - "Moving-platform landing mission (lock / track / touchdown)"
Cohesion: 0.16
Nodes (14): ArUco marker detection, Blind final ~1 m of descent, Moving-platform landing mission (lock / track / touchdown), Nested smaller marker (proposed fix for blind window), Velocity-matched contact touchdown, ArUco detection (DICT_4X4_50, marker id 0, solvePnP), aruco_landing_target_node, Blind final descent window (marker leaves FOV below ~1 m) (+6 more)

### Community 31 - "rl_multi_rotor_landing_sim/src/training_q_learning/src/training_q_learning/utils_multiresolution.py"
Cohesion: 0.16
Nodes (17): discretize_action(), discretize_relative_state(), get_discrete_action_state_from_ros_msg(), get_discrete_rel_states_from_ros_msg(), get_discrete_state_from_ros_msg(), get_latest_cur_step_for_state(), initialize_grid_list(), Action (+9 more)

### Community 32 - "initialize_grid_list"
Cohesion: 0.20
Nodes (9): Create: Q(s,a) DoubleQ(s,a) VisitCounter(s,a), create_double_q_tables(), create_empty_q_table(), create_visit_counter(), initialize_grid_list(), Create a nested numpy array whose shape matches the discretization grid.…, Create an empty Q-table. The last dimension corresponds to actions., Create the state-action visit counter. (+1 more)

### Community 33 - "ament_flake8_main"
Cohesion: 0.15
Nodes (10): ament_flake8_main, flake8, linter, test_flake8(), flake8, linter, test_flake8(), flake8 (+2 more)

### Community 34 - "ament_pep257_main"
Cohesion: 0.15
Nodes (10): ament_pep257_main, linter, pep257, test_pep257(), linter, pep257, test_pep257(), linter (+2 more)

### Community 35 - "extract_flights_from_rosbag_topics.py"
Cohesion: 0.25
Nodes (4): cv2, pathlib, This script extracts flights from ros topics by determining the time periods in…, Generates the ArUco marker image used as the visual landing target on top of…

### Community 36 - "TargetTracker"
Cohesion: 0.13
Nodes (21): Validated status table (2026-10-14), Camera-latency compensation, Circular platform motion, Control-law speed ceiling (~0.8-1.0 m/s with default gains), CTRV curvature-aware extrapolation, --fast control profile (higher-bandwidth gains), 5 km/h (1.39 m/s) real-hardware target, Offline FakeWorld test harness (+13 more)

### Community 37 - "ViconEnv"
Cohesion: 0.05
Nodes (19): rosgraph, CascadedPIDData, CascadedPIDInterface, FlightActivated, Class stores information RL controlled flight is activated., Reads the status of the ROS controlled parameters and stores the value in the…, get_publisher(), _get_subscribers() (+11 more)

### Community 38 - "interfaces ament package"
Cohesion: 0.17
Nodes (12): LandingCommand.msg, LandingTarget.msg, interfaces ament package, PlatformState.msg, RLObservation.msg, TakeoffSetpoint.msg, UAVState.msg, landing_controller_node (position/velocity modes) (+4 more)

### Community 39 - "LandingController"
Cohesion: 0.21
Nodes (4): LandingController, main(), Node, Switch PX4 into its own AUTO.LAND flight mode instead of us trying to fake a…

### Community 40 - "moving_platform_node.py"
Cohesion: 0.21
Nodes (8): main(), MovingPlatformNode, Node, Seconds on the ROS clock. Wall time by default; SIM time with `-p…, Block briefly until self._now() is reporting real time, not an as-yet-…, Publishes the moving platform's ground-truth state (PlatformState, the RL…, linear_state(), Straight-line motion at constant speed from (start_x, start_y). heading_deg is…

### Community 41 - "landing_env.py"
Cohesion: 0.10
Nodes (15): Parameters, Parameters for the uav_rl_landing training case. Ported from the original…, # NOTE: there is no contact sensor wired up yet (no Gazebo contact, ActionManager, node : rclpy.node.Node The owning node, used to create the publisher.…, Reset actions to their initial values., Update action values using the discrete action selected by the RL agent. Only…, Publish the current control command. (+7 more)

### Community 42 - "patch_x500_camera.py"
Cohesion: 0.26
Nodes (11): argparse, Path, re, find_link_anchor(), find_model_sdf(), _is_file_safe(), main(), patch() (+3 more)

### Community 43 - "rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/parameters.py"
Cohesion: 0.23
Nodes (7): This script contains the parameters to set up a training case…, Class provides data about the vehicle, Class provides parameter affecting the training and values generated from the…, Class provides variables that affect the reinforcement learning algorithm and…, RLParameters, SimulationParameters, UAVParameters

### Community 44 - "rl_multi_rotor_landing_sim/src/training_q_learning/src/training_q_learning/parameters.py"
Cohesion: 0.23
Nodes (7): This script contains the parameters to set up a training case…, Class provides data about the vehicle, Class provides parameter affecting the training and values generated from the…, Class provides variables that affect the reinforcement learning algorithm and…, RLParameters, SimulationParameters, UAVParameters

### Community 45 - ".__init__"
Cohesion: 0.28
Nodes (5): Vehicle / action-space configuration., Reinforcement-learning / curriculum configuration., RLParameters, SimulationParameters, UAVParameters

### Community 46 - "LandingEnv"
Cohesion: 0.24
Nodes (5): LandingEnv, Node, Apply one discrete action, advance one control period, and return (state,…, Spin this node's callbacks for approximately duration_sec, so subscription…, Reset the episode: sample a target pose, fly there for real and hold (position-…

### Community 47 - "rospy"
Cohesion: 0.15
Nodes (17): geometry_msgs_msg, librepilot_msg, mav_msgs_msg, rospy, std_msgs_msg, tf_transformations, training_q_learning_msg, training_q_learning_utils (+9 more)

### Community 48 - "StateDiscretizer"
Cohesion: 0.24
Nodes (5): State Discretizer Converts continuous observations (an…, Build discretization limits for every observation according to the current…, Convert one continuous value into a discrete bin index (evenly-spaced bins over…, Convert a continuous observation into a discrete state tuple. `observation`…, StateDiscretizer

### Community 49 - "Linear 5 km/h with --fast and travel_length=50"
Cohesion: 0.20
Nodes (12): Platform motion anchored to a patrol leg, Linear (back-and-forth) platform motion, One-way platform motion fails with the patrol design, Square patrol search (A-B-C-D), travel_length / instant-reversal finding (travel_length=50), Linear motion parameters (start_x/y, heading_deg, speed, travel_length), Alignment hysteresis loosening (align_speed_tol, realign_tol), Anchored back-and-forth platform motion (B->C leg east=9) (+4 more)

### Community 50 - "Project Atlas (README)"
Cohesion: 0.21
Nodes (14): Double Q-learning agent, RL based Autonomous Multi-Rotor Landing on Moving Platforms (Goldschmid & Ahmad), Phase 1: landing on hard-coded static platform, Phase 2: camera-guided landing on static platform, Phase 3: landing on a moving platform (linear + circular), Phase 4+: RL-controlled approach and real hardware, Project Atlas (README), PX4 + ROS 2 Humble + Gazebo Harmonic stack (+6 more)

### Community 51 - "LogTraining"
Cohesion: 0.17
Nodes (8): LogTraining, Function saves numpy.ndarrays that are used in the context of Q-learning. Array…, Function saves the training and logging data, Function saves the logging data, Function handles the logging of data at the end of each episode., Class contains functions for printing out training information and for data…, Function performs operation that is executed in each timestep., Function prints info to the terminal when verbose is set to true.

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
Cohesion: 0.60
Nodes (5): Trust the 'Contact at ... predicted platform position' line, Gotchas (RTF, ground truth, FakeWorld limits, travel_length), --no-ground-truth flag, False ESTIMATE_MISMATCH abort / --no-ground-truth workaround, use_sim_time / real-time-factor (RTF) finding

### Community 57 - "VisionLander"
Cohesion: 0.17
Nodes (8): Slide the setpoint toward the target by one control period (a plain jump would…, Fly to a point and wait until the UAV (not just the setpoint) is there. Returns…, Sim ground truth for where the marker is right now (evaluation only, never used…, Called once at search altitude, before the patrol starts., Fly the corners in order, hovering `dwell_time` at each; return "TRACK" the…, Fly to a corner, checking for the marker on every control tick, and logging…, Swapped / sign-flipped north-east axes, judged from the expected vs measured…, VisionLander

### Community 59 - "plot_topic_freq_from_flight.py"
Cohesion: 0.53
Nodes (5): matplotlib_pyplot, calcualte_windowed_freqs_over_time(), create_plot(), decompose_vector(), plot_topic_frequency()

### Community 60 - "trajectories.py"
Cohesion: 0.23
Nodes (9): bisect, _advance(), random_state(), _RandomPath, Platform trajectories as pure functions of elapsed time (no ROS imports, so…, Random but smooth motion at constant `speed` inside the ellipse centred on…, Position and heading after tau seconds at speed v and constant turn rate w…, The segment stays in the arena AND ends somewhere the platform can still turn… (+1 more)

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

### Community 71 - "observation_generator.py"
Cohesion: 0.12
Nodes (15): compute_observation_action_msg(), compute_relative_observation_msg(), This script defines a ROS node that computes the relative information between…, Function sets a flag when the simulation is reset., Function reads the relative position message and stores the message in the…, Function reads the relative velocity message and stores the message in the…, Function reads the relative acceleration message and stores the message in the…, Function reads the setpoints for the action values of the drone. (+7 more)

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

### Community 91 - "rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_q_learning.py"
Cohesion: 0.15
Nodes (11): datetime, pickle, rosnode, torch_utils_tensorboard, decay_rate_from_schedule(), This script contains the definitions of classes and function that are required…, Function determines the decay rate that has been defined using a dictionary.…, Function implements the Double Q-learning algorithm presented in… (+3 more)

### Community 92 - "rl_multi_rotor_landing_gcs/other_files/setup.bash"
Cohesion: 0.50
Nodes (3): setup.bash script, ROS_PACKAGE_PATH, ROS_PROJECT_ROOT

### Community 93 - "vicon_action_to_uavpose.py"
Cohesion: 0.16
Nodes (12): tf2_ros, uav_msgs_msg, This scripts defines a conversion node that converts messages of type…, publish_stability_axes_as_tf_frame(), Function publishes the stability axes frame w.r.t. the world frame., Function reads the pose messages of the copter in the vicon system., read_pose_msg(), publish_tf_transform_from_world_frame_to_copter_frame() (+4 more)

### Community 94 - "training_action_interface.py"
Cohesion: 0.14
Nodes (13): publish_roll_pitch_yawrate_thrust_msg(), This script creates an interface node which fuses the setpoints for the roll,…, Function reads the message containing the relative pose information of moving…, Function publishes the roll pitch yawrate thrust message based on the values…, Function handles the reset procedure required to assign the initial values to…, Function reads the control effort message (thrust) that is output by the PID…, Function reads the control effort message (yaw rate) that is output by the PID…, Function reads the message containing the relative pose information of moving… (+5 more)

### Community 95 - "ViconObject"
Cohesion: 0.17
Nodes (7): Function reads observation from corresponding topic and updates old observation…, Function checks episode termination status and generates the appropriate reward., Publication of the current discrete state to the ROS environment., Function reads the current state of the drone whenever triggered by the…, Functions reads the continouos observations of the environment whenever the…, Function checks whether or not the episode has to be terminated or not. It can…, ViconObject

### Community 97 - "rl_multi_rotor_landing_sim/other_files/setup.bash"
Cohesion: 0.50
Nodes (3): setup.bash script, ROS_PACKAGE_PATH, ROS_PROJECT_ROOT

### Community 98 - "test_copyright"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 99 - "test_pep257"
Cohesion: 0.50
Nodes (3): linter, pep257, test_pep257()

### Community 100 - "test_copyright"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 101 - "test_copyright"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 102 - "test_random"
Cohesion: 0.20
Nodes (9): The target's estimated state at time `now`, or None if there is no data or the…, TargetState, jitter_and_mission_time(), Mission against random_state paths, one seed per run (the seed IS the arrival…, --fast on a 1 m/s random path: (mean RMS of the horizontal command's high-…, Phase 3c: a randomly moving platform (moving_platform/trajectories.py's…, run_random_sweep(), truth_state() (+1 more)

### Community 103 - "main"
Cohesion: 0.20
Nodes (9): sys, copyright, linter, skip, test_copyright(), build_detector_params(), main(), Standalone sanity check for the ArUco detection logic in… (+1 more)

### Community 104 - "test_copyright"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 105 - "vision_node/test/test_flake8.py"
Cohesion: 0.50
Nodes (3): flake8, linter, test_flake8()

### Community 106 - "test_pep257"
Cohesion: 0.50
Nodes (3): linter, pep257, test_pep257()

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

### Community 127 - "TelemetryStalled"
Cohesion: 0.50
Nodes (4): Exception, MissionTimeout, No fresh /uav/state for too long -- almost always a crashed or hung PX4/Gazebo,…, TelemetryStalled

### Community 128 - "initialize_grid_list"
Cohesion: 0.50
Nodes (3): Function creates a numpy.ndarray that can be indexed according to a…, initialize_grid_list(), The grid list can be initialized using this function. It will create a nested…

### Community 129 - "moving_platform/test/test_flake8.py"
Cohesion: 0.50
Nodes (3): flake8, linter, test_flake8()

### Community 130 - "vision_landing_main.py"
Cohesion: 0.67
Nodes (3): main(), parse_corner(), Camera-guided landing on a static platform -- one script. Takes off, flies the…

## Knowledge Gaps
- **133 isolated node(s):** `archive_training_results.sh script`, `init_workspaces.sh script`, `kill_vicon.sh script`, `prepare_terminal_window.sh script`, `record_rosbag.bash script` (+128 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 727 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **41 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `main` to `test_copyright`, `test_pep257`, `test_copyright`, `test_copyright`, `ament_pep257_main`, `test_copyright`, `test_pep257`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `TargetTracker` connect `TargetTracker` to `moving_landing.py`, `Moving-platform landing mission (lock / track / touchdown)`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `CLAUDE.md (Project Atlas instructions)` connect `moving_landing.py` to `Gotchas (RTF, ground truth, FakeWorld limits, travel_length)`, `Project Atlas (README)`, `TargetTracker`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `RosMissionIO` (e.g. with `Parameters` and `ResetManager`) actually correct?**
  _`RosMissionIO` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `archive_training_results.sh script`, `init_workspaces.sh script`, `kill_vicon.sh script` to the rest of the system?**
  _133 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `vicon_observation_generator.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Should `RosMissionIO` be split into smaller, more focused modules?**
  _Cohesion score 0.08374384236453201 - nodes in this community are weakly interconnected._