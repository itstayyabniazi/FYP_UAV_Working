# Graph Report - FYP_UAV  (2026-10-05)

## Corpus Check
- 180 files · ~97,849 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 379 file(s) not represented in the graph (top: .msg 275, .launch 34, (none) 23)

## Summary
- 1498 nodes · 2305 edges · 151 communities (110 shown, 41 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 68 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c094402d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_multiresolution.py
- LandingSimulationObject
- vision_relative_state_node
- test_missions.py
- QLearning
- patch_x500_camera.py
- LandingSimulationEnv
- Sim Analysis Node
- numpy
- Vicon Launch Scripts
- Platform Trajectory Generator
- execute_agent_evaluation_for_one_exp.py
- px4_msgs CI & Release
- RewardManager
- Vicon ENU-NED Conversion
- Parameters
- .start_takeoff
- math
- vicon_compute_relative_state_moving_platform_drone.py
- Vicon Debug Interface
- training_q_learning_parameters
- FakeWorld
- ArucoLandingTargetNode
- Sim Observation Generator
- q_learning.py
- RosMissionIO
- Vicon Observation Generator
- One-Euro Platform Filter
- ViconEnv
- training_action_interface.py
- ament_flake8_main
- RelativeStateNode
- detect_contact_in_msg
- LogTraining
- ViconObject
- LandingController
- rl_multi_rotor_landing repository (paper code)
- VisionLander
- .__init__
- time
- rospy
- TargetTracker
- ament_pep257_main
- StateDiscretizer
- World-Base TF Publisher
- main
- rl_multi_rotor_landing_sim/src/training_q_learning/src/training_q_learning/utils_multiresolution.py
- Platform State Publisher (C++)
- Changelog Generator
- Action to UAV Pose
- ROS 2 Package Setup
- RelativeStateNode
- MovingPlatformLander
- interfaces ament package
- Copyright Lint Tests
- Stability Axes TF
- grid_utils.py
- rl_multi_rotor_landing_sim/src/training_q_learning/src/training_q_learning/utils.py
- MovingPlatformNode
- vision_relative_state_node.py
- Catkin Packages
- UAV Pose From State Estimate
- LogTraining
- Landing Trial Tracker
- Observation Relative State
- Flight Activated Flag
- Script: publish_vmp_x.sh
- Script: publish_vmp_y.sh
- Script: launch_action_interface.sh
- Script: launch_analysis_node_2D.sh
- Script: launch_cascaded_pid_environment_in_virtual_screens.sh
- Script: launch_cascaded_pid_interface.sh
- Script: launch_compute_relative_information.sh
- Script: launch_environment_in_virtual_screens.sh
- Script: launch_landing_simulation.sh
- Script: launch_observation_generator.sh
- Script: launch_publish_stability_axes.sh
- Script: launch_test_model_2D.sh
- Script: launch_training.sh
- Moving Platform Description
- Release Notes Generator
- Catkin Setup Files
- Docker Dev Environment
- GCS Environment Setup
- publish_stability_axes_as_tf_frame
- rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/parameters.py
- Sim Cleanup Scripts
- Sim Environment Setup
- ROS 2 pipeline (px4_bridge -> relative_state -> landing_controller)
- initialize_grid_list
- Copyright Lint Tests
- Copyright Lint Tests
- Parameters
- Parameters
- Copyright Lint Tests
- generate_aruco_marker.py
- activate_training_venv.sh
- launch_vicon_bridge.sh
- rl_multi_rotor_landing_sim catkin workspace
- process_action
- moving_platform_node (circular trajectory publisher)
- run_sim_terminals.sh
- launch_ros_bridge.sh
- launch_ros_core.sh
- Issue template chooser config
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
- reward.py (unnormalized weights)
- PositionHistory
- FYP UAV: Autonomous Landing of Multi-Rotor on Moving Platform
- pre-commit
- publish_tf_transform_from_world_frame_to_copter_frame
- test_pep257
- PoseTwistAccelerationState
- PoseTwistAccelerationState
- Interface
- ActionManager
- test_pep257
- .generate_initial_pose
- LandingEnv
- get_publisher
- CascadedPIDData
- CascadedPIDInterface
- .__init__
- add_cur_step_lims_of_state
- TelemetryStalled
- initialize_grid_list
- landing_controller/test/test_flake8.py
- moving_platform/test/test_flake8.py
- test_copyright
- test_pep257
- vision_landing_main.py

## God Nodes (most connected - your core abstractions)
1. `RosMissionIO` - 37 edges
2. `FakeWorld` - 29 edges
3. `Parameters` - 24 edges
4. `VisionLander` - 24 edges
5. `ResetManager` - 20 edges
6. `MovingPlatformLander` - 20 edges
7. `LandingEnv` - 19 edges
8. `Parameters` - 18 edges
9. `TrajectoryGenerator` - 17 edges
10. `LandingSimulationEnv` - 16 edges

## Surprising Connections (you probably didn't know these)
- `FYP UAV: Autonomous Landing of Multi-Rotor on Moving Platform` --references--> `vision_node package (ArUco perception)`  [EXTRACTED]
  README.md → workspace/ros2_ws/src/vision_node/README.md
- `FYP UAV: Autonomous Landing of Multi-Rotor on Moving Platform` --references--> `uav_rl_landing module`  [EXTRACTED]
  README.md → workspace/uav_rl_landing/README.md
- `QLearning` --uses--> `LogTraining`  [INFERRED]
  workspace/rl_multi_rotor_landing/rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/custom_q_learning.py → workspace/rl_multi_rotor_landing/rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_q_learning.py
- `get_discrete_rel_states_from_ros_msg()` --uses--> `Parameters`  [INFERRED]
  workspace/rl_multi_rotor_landing/rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_multiresolution.py → workspace/rl_multi_rotor_landing/rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/parameters.py
- `get_discrete_state_from_ros_msg()` --uses--> `Parameters`  [INFERRED]
  workspace/rl_multi_rotor_landing/rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_multiresolution.py → workspace/rl_multi_rotor_landing/rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/parameters.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **ArUco vision perception flow** — workspace_ros2_ws_src_vision_node_readme_aruco_landing_target_node, workspace_ros2_ws_src_vision_node_readme_vision_relative_state_node, workspace_ros2_ws_src_vision_node_readme_rl_observation_topic, workspace_ros2_ws_src_vision_node_readme_target_lost_watchdog [EXTRACTED 1.00]
- **Moving platform simulation setup (node, Gazebo model, cmd_vel bridge)** — workspace_ros2_ws_src_moving_platform_readme_moving_platform_node, workspace_ros2_ws_src_moving_platform_readme_gazebo_model, workspace_ros2_ws_src_moving_platform_readme_cmd_vel_bridge [EXTRACTED 1.00]
- **px4_msgs automated release pipeline** — workspace_ros2_ws_src_px4_msgs_github_workflows_create_release, workspace_ros2_ws_src_px4_msgs_github_workflows_package, workspace_ros2_ws_src_px4_msgs_github_workflows_release, workspace_ros2_ws_src_px4_msgs_github_workflows_release_bloom [EXTRACTED 1.00]
- **ROS 2 landing pipeline: px4_bridge -> relative_state -> RL agent -> landing_controller** — workspace_uav_rl_landing_readme_px4_bridge_uav_state_node, workspace_uav_rl_landing_readme_relative_state_node, workspace_uav_rl_landing_agent_q_learning, workspace_uav_rl_landing_readme_landing_controller_node [EXTRACTED 1.00]
- **px4_msgs quality assurance gates (CI, pre-commit, quality declaration)** — workspace_ros2_ws_src_px4_msgs_github_workflows_build, workspace_ros2_ws_src_px4_msgs_pre_commit_config, workspace_ros2_ws_src_px4_msgs_quality_declaration, workspace_ros2_ws_src_px4_msgs_github_dependabot [INFERRED 0.75]

## Communities (151 total, 41 thin omitted)

### Community 0 - "rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_multiresolution.py"
Cohesion: 0.18
Nodes (15): discretize_action(), discretize_relative_state(), get_discrete_action_state_from_ros_msg(), get_discrete_rel_states_from_ros_msg(), get_discrete_state_from_ros_msg(), get_latest_cur_step_for_state(), Action, ObservationRelativeState (+7 more)

### Community 1 - "LandingSimulationObject"
Cohesion: 0.10
Nodes (14): LandingSimulationObjectState, ObservationRelativeStateMsg, LandingSimulationObject, Bool, ContactsState, Functions reads the continouos observations of the environment whenever the…, Function checks if the contact sensor on top of the moving platform sends…, Functions resets variables to init values whenever a reset signal is received. (+6 more)

### Community 2 - "vision_relative_state_node"
Cohesion: 0.29
Nodes (8): RLObservation.msg, relative_state_node (ground-truth path), /rl_observation topic, Target-lost watchdog (termination.py), vision_relative_state_node, No contact sensor: touchdown inferred from altitude/offset/speed, relative_state_node, termination.py (success/crash_landing/timeout)

### Community 3 - "test_missions.py"
Cohesion: 0.10
Nodes (30): circular_state(), linear_state(), Platform trajectories as pure functions of elapsed time (no ROS imports, so…, Counter-clockwise circle; at t=0 the platform is at (center_x + radius,…, Straight-line motion at constant speed from (start_x, start_y). heading_deg is…, MovingLandingConfig, check(), _locked_at() (+22 more)

### Community 4 - "QLearning"
Cohesion: 0.12
Nodes (10): ndarray, QLearning, Function scales the values of a Q-table. Two options are available. - Mode…, Function adds num_ref_steps new curriculum steps to the sequential curriculum…, Function resets table values to predefined integer value., Class contains different functions to perform RL training for landing a multi-…, Function sets up the logging system for the training environment. It handles…, Function sets up the training environment and performs intial reset (+2 more)

### Community 5 - "patch_x500_camera.py"
Cohesion: 0.09
Nodes (24): argparse, csv, matplotlib_pyplot, os_path, Path, pathlib, re, rosbag (+16 more)

### Community 6 - "LandingSimulationEnv"
Cohesion: 0.08
Nodes (16): LogTopicFreqs, This is a variation of the create_log_dir_path_function in the utils script.…, LogTopicFreqs, This is a variation of the create_log_dir_path_function in the utils script.…, LandingSimulationEnv, Bool, Function maps an action integer number to an action string, updates the new…, Function resets the training environment and updates logging data (+8 more)

### Community 7 - "Sim Analysis Node"
Cohesion: 0.07
Nodes (18): AnalysisNode, Function publishes basic statistics over the ROS framework for the movement in…, Function publishes basic statistics over the ROS framework for the movement in…, Function logs and computes basic statistics for motion in x-direction., Function logs and computes basic statistics for motion in y-direction., Function prints statistics to the terminal window, Function reads the current discrete states of the longitudinal motion., Function reads the current discrete states of the lateral motion. (+10 more)

### Community 8 - "numpy"
Cohesion: 0.09
Nodes (29): copy, datetime, gazebo_msgs_srv, gym, gym_envs_registration, numpy, os, pandas (+21 more)

### Community 9 - "Vicon Launch Scripts"
Cohesion: 0.07
Nodes (20): src_rl_multi_rotor_landing_rl_multi_rotor_landing_gcs_other_files_setup_bash, ROS_IP, launch_audio_feedback.sh script, ROS_IP, launch_vicon_action_to_uavpose.sh script, launch_vicon_compute_relative_information.sh script, ROS_IP, launch_vicon_filter_platform_data.sh script (+12 more)

### Community 10 - "Platform Trajectory Generator"
Cohesion: 0.08
Nodes (16): Function computes a straight trajectory for the moving platform., Function computes a rectiliar periodic trajectory for the moving platform., Function computes a vertical, straight trajectory for the moving platform, Function computes a rectiliar periodic trajectory., Function computes the trajectory based on arguments trajectory_type,…, Function publishes the updated platform position to the ROS network., Function resets time to a random value within an interval of episode_length…, Function handles the service request to reset the seed for the random number… (+8 more)

### Community 11 - "execute_agent_evaluation_for_one_exp.py"
Cohesion: 0.09
Nodes (20): fileinput, shutil, sys, This script automizes the execution of the evaluation of an agent for all…, get_last_final_result_path(), get_last_parameters_file(), This script automizes the execution of the evaluation of an agent., This functions opens a file, searches for a pattern, replaces it with the… (+12 more)

### Community 12 - "px4_msgs CI & Release"
Cohesion: 0.14
Nodes (26): px4_msgs CHANGELOG (tracks PX4 release lines 1.16, 1.17), px4_msgs CMakeLists.txt, rosidl_generate_interfaces (msg/srv glob to C++/Python/IDL), px4_msgs Code of Conduct, px4_msgs Contributing guide and release process, DCO sign-off and Conventional Commits policy, Dependabot config (github-actions updates), Pull request template (+18 more)

### Community 14 - "Vicon ENU-NED Conversion"
Cohesion: 0.13
Nodes (10): Convert quaterion defined in ENU frame to NED frame, Convert PoseStamped message from ENU to NED frame., Converts twist stamped message from ENU frame to NED frame., Publishes auxposition, auxvelocity in NED frame only when a new message was…, Function stores the pose and twist information together with the reference…, Reads vicon drone pose message, performs the frame conversion from ENU to NED…, Reads vicon drone pose message, performs the frame conversion from ENU to NED…, Reads vicon moving platform pose message, performs the frame conversion from… (+2 more)

### Community 15 - "Parameters"
Cohesion: 0.11
Nodes (14): ndarray, QLearning, Function scales the values of a Q-table. Two options are available. - Mode…, Function adds num_ref_steps new curriculum steps to the sequential curriculum…, Function resets table values to predefined integer value., Class contains different functions to perform RL training for landing a multi-…, Function sets up the training environment and performs intial reset, Function implements the Double Q-learning algorithm presented in… (+6 more)

### Community 17 - "math"
Cohesion: 0.15
Nodes (15): collections, dataclasses, math, random, typing, main(), measure_camera_latency.py Measures the delay between a camera image being taken…, moving_landing.py Phase 3 mission: land on a platform that MOVES (straight… (+7 more)

### Community 18 - "vicon_compute_relative_state_moving_platform_drone.py"
Cohesion: 0.11
Nodes (16): tf2_geometry_msgs, compute_landing_simulation_object_state_msg(), compute_relative_pos_msg(), compute_relative_vel_msg(), This scripts defines a ROS node that provides information about the moving…, Reads pose message of moving platform and stores data in storage class., Reads twist message of moving platform and stores data in storage class., Function computes the relative velocity vector between the moving platform and… (+8 more)

### Community 19 - "Vicon Debug Interface"
Cohesion: 0.14
Nodes (9): Converts twist stamped message from ENU frame to NED frame., Class containing debugging functions and required variables, Reads vicon drone pose message., Reads state estimate drone pose message., Reads vicon drone twist message., Reads state estimate drone twist message., Convert quaterion defined in ENU frame to NED frame?, Convert PoseStamped message from ENU to NED frame. (+1 more)

### Community 20 - "training_q_learning_parameters"
Cohesion: 0.16
Nodes (11): librepilot_msg, roslaunch, training_q_learning_custom_q_learning, training_q_learning_parameters, training_q_learning_utils_multiresolution, Script uses two instances of one RL agent to control the movement of the drone…, Script creates the simulation environment that is required in order to use 4…, Script uses two instances of one RL agent to control the movement of the drone… (+3 more)

### Community 22 - "ArucoLandingTargetNode"
Cohesion: 0.12
Nodes (12): LandingTarget, ArucoLandingTargetNode, build_detector_params(), euler_to_rotation_matrix(), main(), Node, World-from-body rotation matrix for the 3-2-1 (yaw, pitch, roll) Euler…, True once camera intrinsics are available. If no camera_info shows up within… (+4 more)

### Community 23 - "Sim Observation Generator"
Cohesion: 0.12
Nodes (15): compute_observation_action_msg(), compute_relative_observation_msg(), This script defines a ROS node that computes the relative information between…, Function sets a flag when the simulation is reset., Function reads the relative position message and stores the message in the…, Function reads the relative velocity message and stores the message in the…, Function reads the relative acceleration message and stores the message in the…, Function reads the setpoints for the action values of the drone. (+7 more)

### Community 24 - "q_learning.py"
Cohesion: 0.14
Nodes (10): ExplorationManager, Choose action using epsilon-greedy policy., Update epsilon according to schedule., Restore epsilon from checkpoint., Current exploration rate., Handles epsilon-greedy exploration., q_learning.py Double Q-learning training loop (Hasselt 2010), ported from the…, decay_rate_from_schedule() (+2 more)

### Community 25 - "RosMissionIO"
Cohesion: 0.07
Nodes (9): Switch landing_controller to velocity setpoints. It only streams offboard…, Sim ground truth from /platform/state, converted to PX4 local NED: (north,…, New absolute marker samples (time, x, y) since the last call., True if no RAW PX4 message (/fmu/out/vehicle_local_position_v1) has arrived in…, (messages, of which detected) received on /landing_target in the last `window`…, Mean absolute marker (x, y) over the latest few FRESH detections, or None if…, (mean rel_x, rel_y, rel_z, n) over the last `window` s, or None., Check the pipeline is up before arming anything. Same lesson as Phase 1: a… (+1 more)

### Community 26 - "Vicon Observation Generator"
Cohesion: 0.13
Nodes (14): sensor_msgs_msg, compute_observation_action_msg(), compute_relative_observation_msg(), This script defines a ROS node that computes the relative information between…, Function reads the relative position message and stores the message in the…, Function reads the relative velocity message and stores the message in the…, Function reads the relative acceleration message and stores the message in the…, Function reads the setpoints for the action values of the drone. (+6 more)

### Community 27 - "One-Euro Platform Filter"
Cohesion: 0.19
Nodes (5): OneEuroFilter, Function stores the pose and twist data of the platform received via the vicon…, Initialize the one euro filter. Based on https://jaantollander.com/post/noise-…, Compute the filtered signal., SmoothPlatformData

### Community 28 - "ViconEnv"
Cohesion: 0.19
Nodes (7): Function maps an action integer number to an action string, updates the new…, Function resets the training environment and updates logging data, Function sends out a boolean value indicating that a reset has been requested.…, Function performs the normalization of observations of the environment and…, Function publishes the action values that are currently set to the ROS network., Function performs one time step for when two instances of the same agent are…, ViconEnv

### Community 29 - "training_action_interface.py"
Cohesion: 0.14
Nodes (13): publish_roll_pitch_yawrate_thrust_msg(), This script creates an interface node which fuses the setpoints for the roll,…, Function reads the message containing the relative pose information of moving…, Function publishes the roll pitch yawrate thrust message based on the values…, Function handles the reset procedure required to assign the initial values to…, Function reads the control effort message (thrust) that is output by the PID…, Function reads the control effort message (yaw rate) that is output by the PID…, Function reads the message containing the relative pose information of moving… (+5 more)

### Community 30 - "ament_flake8_main"
Cohesion: 0.15
Nodes (10): ament_flake8_main, flake8, linter, test_flake8(), flake8, linter, test_flake8(), flake8 (+2 more)

### Community 31 - "RelativeStateNode"
Cohesion: 0.29
Nodes (3): main(), Node, RelativeStateNode

### Community 32 - "detect_contact_in_msg"
Cohesion: 0.67
Nodes (3): detect_contact_in_msg(), ContactsState, Function returns the value true if a contact has been detected by a contact…

### Community 33 - "LogTraining"
Cohesion: 0.05
Nodes (22): rosgraph, CascadedPIDData, CascadedPIDInterface, FlightActivated, Class stores information RL controlled flight is activated., Reads the status of the ROS controlled parameters and stores the value in the…, Function sets up the logging system for the training environment. It handles…, create_log_dir_path() (+14 more)

### Community 34 - "ViconObject"
Cohesion: 0.14
Nodes (8): Class for setting up a gym based training environment that can be used in…, Function reads observation from corresponding topic and updates old observation…, Function checks episode termination status and generates the appropriate reward., Publication of the current discrete state to the ROS environment., Function reads the current state of the drone whenever triggered by the…, Functions reads the continouos observations of the environment whenever the…, Function checks whether or not the episode has to be terminated or not. It can…, ViconObject

### Community 35 - "LandingController"
Cohesion: 0.21
Nodes (4): LandingController, main(), Node, Switch PX4 into its own AUTO.LAND flight mode instead of us trying to fake a…

### Community 36 - "rl_multi_rotor_landing repository (paper code)"
Cohesion: 0.25
Nodes (9): rl_multi_rotor_landing_gcs catkin workspace, LibrePilot Ground Control Station, moving_platform_control package (model train on rails), rl_multi_rotor_landing repository (paper code), rl_multi_rotor_landing_uav catkin workspace, Real-hardware experiment with Vicon and LibrePilot GCS, Python requirements (gym, numpy, rospkg, tensorboard, ...), LibrePilot installation steps (+1 more)

### Community 37 - "VisionLander"
Cohesion: 0.18
Nodes (8): Slide the setpoint toward the target by one control period (a plain jump would…, Fly to a point and wait until the UAV (not just the setpoint) is there. Returns…, Sim ground truth for where the marker is right now (evaluation only, never used…, Called once at search altitude, before the patrol starts., Fly the corners in order, hovering `dwell_time` at each; return "TRACK" the…, Fly to a corner, checking for the marker on every control tick, and logging…, Swapped / sign-flipped north-east axes, judged from the expected vs measured…, VisionLander

### Community 38 - ".__init__"
Cohesion: 0.28
Nodes (5): Vehicle / action-space configuration., Reinforcement-learning / curriculum configuration., RLParameters, SimulationParameters, UAVParameters

### Community 39 - "time"
Cohesion: 0.08
Nodes (23): interfaces_msg, px4_msgs_msg, rclpy, rclpy_node, rclpy_qos, time, Publishes the moving platform's ground-truth state (PlatformState, the RL…, Detects the ArUco marker on the moving platform (see… (+15 more)

### Community 40 - "rospy"
Cohesion: 0.07
Nodes (36): geometry_msgs_msg, mav_msgs_msg, rospy, std_msgs_msg, tf2_ros, tf_transformations, training_q_learning_msg, training_q_learning_utils (+28 more)

### Community 41 - "TargetTracker"
Cohesion: 0.15
Nodes (6): Low-pass estimate of how fast the fitted velocity vector's HEADING is rotating…, True if a sample ARRIVED within the last `max_age` seconds., The target's estimated state at time `now`, or None if there is no data or the…, t = when the marker was SEEN (capture time); received = when the sample arrived…, TargetState, TargetTracker

### Community 42 - "ament_pep257_main"
Cohesion: 0.22
Nodes (7): ament_pep257_main, linter, pep257, test_pep257(), linter, pep257, test_pep257()

### Community 43 - "StateDiscretizer"
Cohesion: 0.31
Nodes (4): Build discretization limits for every observation according to the current…, Convert one continuous value into a discrete bin index (evenly-spaced bins over…, Convert a continuous observation into a discrete state tuple. `observation`…, StateDiscretizer

### Community 44 - "World-Base TF Publisher"
Cohesion: 0.24
Nodes (8): PositionOrientationState, publish_transform_message(), publish_world_to_world_link_transform_message(), Class for storing the current position and orientation of the moving platform, Read model state of moving platform., Function publishes the required tf transform from world frame to an additional…, Publish the transformation message to describe the motion of the moving…, read_model_state()

### Community 45 - "main"
Cohesion: 0.25
Nodes (8): copyright, linter, skip, test_copyright(), build_detector_params(), main(), Standalone sanity check for the ArUco detection logic in…, Same tuning as aruco_landing_target_node.py's build_detector_params() -- see…

### Community 46 - "rl_multi_rotor_landing_sim/src/training_q_learning/src/training_q_learning/utils_multiresolution.py"
Cohesion: 0.18
Nodes (15): discretize_action(), discretize_relative_state(), get_discrete_action_state_from_ros_msg(), get_discrete_rel_states_from_ros_msg(), get_discrete_state_from_ros_msg(), get_latest_cur_step_for_state(), Action, ObservationRelativeState (+7 more)

### Community 47 - "Platform State Publisher (C++)"
Cohesion: 0.22
Nodes (5): jointstate, model, ros, string, transform_broadcaster

### Community 48 - "Changelog Generator"
Cohesion: 0.42
Nodes (8): contributors(), emit(), forthcoming_block(), generate(), join_csv(), names(), generate_changelog.sh script, underline()

### Community 49 - "Action to UAV Pose"
Cohesion: 0.29
Nodes (5): ActionMsg, ActionToUavPose, Class stores all data that is required to convert roll pitch yawrate thrust to…, Funcion assigns the values of roll, pitch and yaw to the velocity field of the…, Function processes the msgs received on the topic

### Community 51 - "RelativeStateNode"
Cohesion: 0.29
Nodes (3): main(), Node, RelativeStateNode

### Community 52 - "MovingPlatformLander"
Cohesion: 0.17
Nodes (8): main(), parse_corner(), Phase 3b: camera-guided landing on a MOVING platform (circular motion) -- one…, main(), parse_corner(), Phase 3: camera-guided landing on a MOVING platform (straight-line motion) --…, MovingPlatformLander, Climb toward where the platform should be NOW (constant-velocity prediction) in…

### Community 53 - "interfaces ament package"
Cohesion: 0.25
Nodes (8): LandingCommand.msg, interfaces ament package, TakeoffSetpoint.msg, UAVState.msg, landing_controller_node (position/velocity modes), PX4 requires GCS heartbeat to arm, px4_bridge uav_state_node, Takeoff / reset phase (reset_manager)

### Community 55 - "Stability Axes TF"
Cohesion: 0.33
Nodes (6): nav_msgs_msg, publish_stability_axes_as_tf_frame(), Function publishes the stability axes as tf frame. The stability axes xy-plane…, Function publishes the stability axes frame w.r.t. the world frame., Function reads the odometry messages of the drone and triggers publishing of…, read_odom_msg()

### Community 56 - "grid_utils.py"
Cohesion: 0.17
Nodes (12): QTableManager, q_table.py Creates and manages the Q-Tables used by Double Q-Learning., Create: Q(s,a) DoubleQ(s,a) VisitCounter(s,a), create_double_q_tables(), create_empty_q_table(), create_visit_counter(), initialize_grid_list(), Grid utilities. This module contains helper functions used for multi-resolution… (+4 more)

### Community 57 - "rl_multi_rotor_landing_sim/src/training_q_learning/src/training_q_learning/utils.py"
Cohesion: 0.15
Nodes (11): gazebo_msgs_msg, rospkg, rostopic, create_log_dir_path(), This script copies all the files that are necessary to determine the settings…, This is a variation of the create_log_dir_path_function in the utils script.…, This script contains the definition of a node that can be used for testing and…, This script contains the definition of a node that can be used for testing and… (+3 more)

### Community 58 - "MovingPlatformNode"
Cohesion: 0.29
Nodes (5): main(), MovingPlatformNode, Node, Seconds on the ROS clock. Wall time by default; SIM time with `-p…, Block briefly until self._now() is reporting real time, not an as-yet-…

### Community 59 - "vision_relative_state_node.py"
Cohesion: 0.25
Nodes (4): main(), Node, Vision-based drop-in alternative to relative_state package's…, VisionRelativeStateNode

### Community 60 - "Catkin Packages"
Cohesion: 0.33
Nodes (6): training_q_learning catkin package (GCS/Vicon), Vicon scripts (vicon_interface, vicon_test_model_2D, vicon_cascaded_pid_controller, ...), training_q_learning catkin package (simulation), ResetRandomSeed.srv, Custom ROS messages (Action, ObservationRelativeState, TwistModified, LandingSimulationObjectState), Simulation scripts (training.py, observation_generator.py, test_model_2D.py, cascaded_pid_controller.py, ...)

### Community 61 - "UAV Pose From State Estimate"
Cohesion: 0.40
Nodes (3): Class stores all data that is required to convert roll pitch yawrate thrust to…, Function processes the msgs received on the topic, UAVPoseFromStateEstimate

### Community 62 - "LogTraining"
Cohesion: 0.17
Nodes (8): LogTraining, Function saves the training and logging data, Function saves the logging data, Function handles the logging of data at the end of each episode., Class contains functions for printing out training information and for data…, Function performs operation that is executed in each timestep., Function prints info to the terminal when verbose is set to true., Function saves numpy.ndarrays that are used in the context of Q-learning. Array…

### Community 64 - "Observation Relative State"
Cohesion: 0.40
Nodes (3): ObservationRelativeState, Class stores the relative position, relative velocity, relative acceleration…, Function checks if all sensor values are provided in the same reference frame.

### Community 65 - "Flight Activated Flag"
Cohesion: 0.40
Nodes (3): FlightActivated, Class stores information RL controlled flight is activated., Reads the status of the ROS controlled parameters and stores the value in the…

### Community 66 - "Script: publish_vmp_x.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, publish_vmp_x.sh script

### Community 67 - "Script: publish_vmp_y.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, publish_vmp_y.sh script

### Community 68 - "Script: launch_action_interface.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_action_interface.sh script

### Community 69 - "Script: launch_analysis_node_2D.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_analysis_node_2D.sh script

### Community 70 - "Script: launch_cascaded_pid_environment_in_virtual_screens.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_cascaded_pid_environment_in_virtual_screens.sh script

### Community 71 - "Script: launch_cascaded_pid_interface.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_cascaded_pid_interface.sh script

### Community 72 - "Script: launch_compute_relative_information.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_compute_relative_information.sh script

### Community 73 - "Script: launch_environment_in_virtual_screens.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_environment_in_virtual_screens.sh script

### Community 74 - "Script: launch_landing_simulation.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_landing_simulation.sh script

### Community 75 - "Script: launch_observation_generator.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_observation_generator.sh script

### Community 76 - "Script: launch_publish_stability_axes.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_publish_stability_axes.sh script

### Community 77 - "Script: launch_test_model_2D.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_test_model_2D.sh script

### Community 78 - "Script: launch_training.sh"
Cohesion: 0.40
Nodes (4): GAZEBO_MASTER_URI, ROS_IP, ROS_MASTER_URI, launch_training.sh script

### Community 79 - "Moving Platform Description"
Cohesion: 0.40
Nodes (5): parser executable, moving_platform_description catkin package, state_publisher executable, command_moving_platform_trajectories.py and world_base_link_transform_publisher.py, JointStateController config (50 Hz)

### Community 80 - "Release Notes Generator"
Cohesion: 0.70
Nodes (4): decls(), header(), namelist(), generate_release_notes.sh script

### Community 82 - "Docker Dev Environment"
Cohesion: 0.50
Nodes (4): /dev/dri GPU passthrough with render group (RENDER_GID), fyp-uav docker compose service, Workspace volume mounts (/workspace, /gazebo, /datasets, /docs), Dockerized dev environment (Ubuntu 22.04, ROS 2 Humble)

### Community 83 - "GCS Environment Setup"
Cohesion: 0.50
Nodes (3): setup.bash script, ROS_PACKAGE_PATH, ROS_PROJECT_ROOT

### Community 84 - "publish_stability_axes_as_tf_frame"
Cohesion: 0.50
Nodes (4): publish_stability_axes_as_tf_frame(), Function publishes the stability axes frame w.r.t. the world frame., Function reads the pose messages of the copter in the vicon system., read_pose_msg()

### Community 85 - "rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/parameters.py"
Cohesion: 0.23
Nodes (7): This script contains the parameters to set up a training case…, Class provides data about the vehicle, Class provides parameter affecting the training and values generated from the…, Class provides variables that affect the reinforcement learning algorithm and…, RLParameters, SimulationParameters, UAVParameters

### Community 87 - "Sim Environment Setup"
Cohesion: 0.50
Nodes (3): setup.bash script, ROS_PACKAGE_PATH, ROS_PROJECT_ROOT

### Community 88 - "ROS 2 pipeline (px4_bridge -> relative_state -> landing_controller)"
Cohesion: 0.29
Nodes (7): ArUco vision pipeline (vision_node), Gazebo Harmonic, Micro XRCE-DDS Agent, PX4 SITL (x500 model), pymavlink headless GCS heartbeat, ROS 2 pipeline (px4_bridge -> relative_state -> landing_controller), ros_gz built from source (Fortress/Harmonic mismatch fix)

### Community 89 - "initialize_grid_list"
Cohesion: 0.50
Nodes (3): Function creates a numpy.ndarray that can be indexed according to a…, initialize_grid_list(), The grid list can be initialized using this function. It will create a nested…

### Community 90 - "Copyright Lint Tests"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 91 - "Copyright Lint Tests"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 92 - "Parameters"
Cohesion: 0.22
Nodes (8): Parameters, This script contains the parameters to set up a training case…, Class provides data about the vehicle, Class provides parameter affecting the training and values generated from the…, Class provides variables that affect the reinforcement learning algorithm and…, RLParameters, SimulationParameters, UAVParameters

### Community 93 - "Parameters"
Cohesion: 0.26
Nodes (6): build_grid(), main(), QLearning, Log/save/decay after an episode. Returns True if training should stop., Load previously saved Q-tables (as produced by save())., Parameters

### Community 94 - "Copyright Lint Tests"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 95 - "generate_aruco_marker.py"
Cohesion: 0.22
Nodes (7): cv2, LandingTarget.msg, Generates the ArUco marker image used as the visual landing target on top of…, aruco_landing_target_node (ArUco detection + solvePnP), CAMERA_TO_BODY frame convention (unverified), patch_x500_camera.py (downward camera patch), vision_node package (ArUco perception)

### Community 98 - "rl_multi_rotor_landing_sim catkin workspace"
Cohesion: 0.29
Nodes (7): Cascaded PI controller baseline, Sequential curriculum training procedure, Goldschmid & Ahmad paper (Autonomous Robots 2024), RotorS + ROS Noetic + Gazebo 11 stack, rl_multi_rotor_landing_sim catkin workspace, Tabular Double Q-learning (Hasselt 2010), uav_rl_landing module

### Community 99 - "process_action"
Cohesion: 0.33
Nodes (6): process_action(), publish_setpoint_v_z(), publish_setpoint_yaw(), Function publishes the setpoint for the PID controller of v_z based on the…, Function publishes the setpoint for the PID controller of the yaw angle based…, Function triggers the processing procedure whenever a new msg is received from…

### Community 100 - "moving_platform_node (circular trajectory publisher)"
Cohesion: 0.33
Nodes (6): PlatformState.msg, ros_gz_bridge cmd_vel bridge, moving_platform Gazebo model (VelocityControl plugin), moving_platform_node (circular trajectory publisher), Open-loop velocity control drift, /platform/state ground truth topic

### Community 101 - "run_sim_terminals.sh"
Cohesion: 0.60
Nodes (5): find_terminal(), open_terminal(), run_sim_terminals.sh script, start_all(), stop_all()

### Community 104 - "Issue template chooser config"
Cohesion: 0.67
Nodes (3): Bug report issue template, Issue template chooser config, Feature request issue template

### Community 127 - "PositionHistory"
Cohesion: 0.29
Nodes (3): PositionHistory, Recent UAV (t, x, y) samples, so a camera measurement can be combined with…, UAV position at time t (linear interpolation; clamped to the ends), or None if…

### Community 128 - "FYP UAV: Autonomous Landing of Multi-Rotor on Moving Platform"
Cohesion: 0.50
Nodes (5): Double Q-learning agent with curriculum discretization, FYP UAV: Autonomous Landing of Multi-Rotor on Moving Platform, Reinforcement Learning based Autonomous Multi-Rotor Landing on Moving Platforms (Goldschmid & Ahmad), Remaining work (no real training, 1D control, no contact sensor, unnormalized reward), RL training module (uav_rl_landing)

### Community 130 - "publish_tf_transform_from_world_frame_to_copter_frame"
Cohesion: 0.50
Nodes (4): publish_tf_transform_from_world_frame_to_copter_frame(), Function publishes a tf transform from the euler_angle_parent_frame frame to…, Function reads the pose messages of the copter in the vicon system and calls…, read_pose_msg()

### Community 131 - "test_pep257"
Cohesion: 0.50
Nodes (3): linter, pep257, test_pep257()

### Community 135 - "ActionManager"
Cohesion: 0.17
Nodes (7): ActionManager, node : rclpy.node.Node The owning node, used to create the publisher.…, Reset actions to their initial values., Update action values using the discrete action selected by the RL agent. Only…, Publish the current control command., Return the current action values., Handles UAV actions. Responsibilities ---------------- - Maintain current…

### Community 136 - "test_pep257"
Cohesion: 0.50
Nodes (3): linter, pep257, test_pep257()

### Community 138 - "LandingEnv"
Cohesion: 0.24
Nodes (5): LandingEnv, Node, Apply one discrete action, advance one control period, and return (state,…, Spin this node's callbacks for approximately duration_sec, so subscription…, Reset the episode: sample a target pose, fly there for real and hold (position-…

### Community 139 - "get_publisher"
Cohesion: 0.25
Nodes (5): Class for setting up a gym based training environment that can be used in…, get_publisher(), _get_subscribers(), Function gets a publisher and returns an error if the publisher is not up.…, Function gets the list of subscribers to a topic. Source:…

### Community 142 - ".__init__"
Cohesion: 0.29
Nodes (3): Call at the start of every episode., Returns (done: bool, outcome: str, success: bool). outcome is one of:…, TerminationManager

### Community 143 - "add_cur_step_lims_of_state"
Cohesion: 0.33
Nodes (4): Function implements the Double Q-learning algorithm presented in…, Class contains information about the training such as reward computation,…, add_cur_step_lims_of_state(), Function reads the limit value for the different discretization steps defined…

### Community 144 - "TelemetryStalled"
Cohesion: 0.50
Nodes (4): Exception, MissionTimeout, No fresh /uav/state for too long -- almost always a crashed or hung PX4/Gazebo,…, TelemetryStalled

### Community 145 - "initialize_grid_list"
Cohesion: 0.50
Nodes (3): Function creates a numpy.ndarray that can be indexed according to a…, initialize_grid_list(), The grid list can be initialized using this function. It will create a nested…

### Community 146 - "landing_controller/test/test_flake8.py"
Cohesion: 0.50
Nodes (3): flake8, linter, test_flake8()

### Community 147 - "moving_platform/test/test_flake8.py"
Cohesion: 0.50
Nodes (3): flake8, linter, test_flake8()

### Community 148 - "test_copyright"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 149 - "test_pep257"
Cohesion: 0.50
Nodes (3): linter, pep257, test_pep257()

### Community 150 - "vision_landing_main.py"
Cohesion: 0.67
Nodes (3): main(), parse_corner(), Camera-guided landing on a static platform -- one script. Takes off, flies the…

## Knowledge Gaps
- **127 isolated node(s):** `archive_training_results.sh script`, `init_workspaces.sh script`, `kill_vicon.sh script`, `prepare_terminal_window.sh script`, `record_rosbag.bash script` (+122 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 710 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **41 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `main` to `test_pep257`, `test_pep257`, `ament_pep257_main`, `test_copyright`, `test_pep257`, `Copyright Lint Tests`, `Copyright Lint Tests`, `Copyright Lint Tests`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `TrajectoryGenerator` connect `Platform Trajectory Generator` to `numpy`, `Parameters`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `AnalysisNode` connect `Sim Analysis Node` to `rospy`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `RosMissionIO` (e.g. with `Parameters` and `ResetManager`) actually correct?**
  _`RosMissionIO` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `archive_training_results.sh script`, `init_workspaces.sh script`, `kill_vicon.sh script` to the rest of the system?**
  _127 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `LandingSimulationObject` be split into smaller, more focused modules?**
  _Cohesion score 0.09881422924901186 - nodes in this community are weakly interconnected._
- **Should `test_missions.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10416666666666667 - nodes in this community are weakly interconnected._