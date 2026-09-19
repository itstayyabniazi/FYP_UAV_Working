# Graph Report - FYP_UAV  (2026-09-19)

## Corpus Check
- 167 files · ~68,933 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 376 file(s) not represented in the graph (top: .msg 275, .launch 34, (none) 22)

## Summary
- 1293 nodes · 1892 edges · 130 communities (92 shown, 38 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 58 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `aec7a8d7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_multiresolution.py
- LandingSimulationObject
- RL Landing Repo Overview
- rospy
- QLearning
- patch_x500_camera.py
- LandingSimulationEnv
- Sim Analysis Node
- rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/custom_q_learning.py
- Vicon Launch Scripts
- Platform Trajectory Generator
- time
- px4_msgs CI & Release
- ActionManager
- Vicon ENU-NED Conversion
- QLearning
- Episode Reset Manager
- numpy
- Vicon Relative State
- Vicon Debug Interface
- Sim Relative State Node
- Training Logger (Sim)
- aruco_landing_target_node.py
- Sim Observation Generator
- Exploration Manager
- grid_utils.py
- Vicon Observation Generator
- One-Euro Platform Filter
- rl_multi_rotor_landing_sim/src/training_q_learning/src/training_q_learning/utils_multiresolution.py
- training_action_interface.py
- ament_flake8_main
- rclpy
- rl_multi_rotor_landing_sim/src/training_q_learning/src/training_q_learning/utils.py
- Cascaded PID + Flight Mode
- Parameters
- LandingController
- Project Architecture & Status
- Sim Training Parameters
- config/parameters.py
- Landing Gym Env
- training.py
- landing_env.py
- ament_pep257_main
- vicon_publish_stability_axes.py
- World-Base TF Publisher
- main
- Reward Manager
- Platform State Publisher (C++)
- Changelog Generator
- Action to UAV Pose
- ROS 2 Package Setup
- Relative State Node (PX4)
- landing_simulation_env.py
- q_learning.py
- Copyright Lint Tests
- Stability Axes TF
- CascadedPIDData
- moving_platform_node.py
- Relative State Node
- interfaces_msg
- Catkin Packages
- UAV Pose From State Estimate
- write_data_to_csv
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
- rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_q_learning.py
- rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/parameters.py
- Sim Cleanup Scripts
- Sim Environment Setup
- plot_topic_freq_from_flight.py
- test_marker_detection.py
- Copyright Lint Tests
- Copyright Lint Tests
- flake8 Lint Tests (relative_state)
- pep257 Lint Tests (relative_state)
- Copyright Lint Tests
- landing_controller_node.py
- activate_training_venv.sh
- launch_vicon_bridge.sh
- PoseTwistAccelerationState
- PoseTwistAccelerationState
- Interface
- test_pep257
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
- px4_bridge/test/test_flake8.py
- test_pep257
- pre-commit

## God Nodes (most connected - your core abstractions)
1. `Parameters` - 24 edges
2. `LandingEnv` - 19 edges
3. `TrajectoryGenerator` - 17 edges
4. `LandingSimulationEnv` - 16 edges
5. `AnalysisNode` - 15 edges
6. `LandingSimulationObject` - 15 edges
7. `QLearning` - 13 edges
8. `ViconEnv` - 13 edges
9. `QLearning` - 13 edges
10. `Parameters` - 13 edges

## Surprising Connections (you probably didn't know these)
- `QLearning` --uses--> `Parameters`  [INFERRED]
  workspace/rl_multi_rotor_landing/rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/custom_q_learning.py → workspace/rl_multi_rotor_landing/rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/parameters.py
- `get_discrete_rel_states_from_ros_msg()` --uses--> `Parameters`  [INFERRED]
  workspace/rl_multi_rotor_landing/rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_multiresolution.py → workspace/rl_multi_rotor_landing/rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/parameters.py
- `get_discrete_state_from_ros_msg()` --uses--> `Parameters`  [INFERRED]
  workspace/rl_multi_rotor_landing/rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_multiresolution.py → workspace/rl_multi_rotor_landing/rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/parameters.py
- `QLearning` --uses--> `Parameters`  [INFERRED]
  workspace/rl_multi_rotor_landing/rl_multi_rotor_landing_sim/src/training_q_learning/src/training_q_learning/custom_q_learning.py → workspace/rl_multi_rotor_landing/rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/parameters.py
- `LandingSimulationEnv` --uses--> `Parameters`  [INFERRED]
  workspace/rl_multi_rotor_landing/rl_multi_rotor_landing_sim/src/training_q_learning/src/training_q_learning/landing_simulation_env.py → workspace/rl_multi_rotor_landing/rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/parameters.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **ArUco vision perception flow** — workspace_ros2_ws_src_vision_node_readme_aruco_landing_target_node, workspace_ros2_ws_src_vision_node_readme_vision_relative_state_node, workspace_ros2_ws_src_vision_node_readme_rl_observation_topic, workspace_ros2_ws_src_vision_node_readme_target_lost_watchdog [EXTRACTED 1.00]
- **Moving platform simulation setup (node, Gazebo model, cmd_vel bridge)** — workspace_ros2_ws_src_moving_platform_readme_moving_platform_node, workspace_ros2_ws_src_moving_platform_readme_gazebo_model, workspace_ros2_ws_src_moving_platform_readme_cmd_vel_bridge [EXTRACTED 1.00]
- **px4_msgs automated release pipeline** — workspace_ros2_ws_src_px4_msgs_github_workflows_create_release, workspace_ros2_ws_src_px4_msgs_github_workflows_package, workspace_ros2_ws_src_px4_msgs_github_workflows_release, workspace_ros2_ws_src_px4_msgs_github_workflows_release_bloom [EXTRACTED 1.00]
- **ROS 2 landing pipeline: px4_bridge -> relative_state -> RL agent -> landing_controller** — workspace_uav_rl_landing_readme_px4_bridge_uav_state_node, workspace_uav_rl_landing_readme_relative_state_node, workspace_uav_rl_landing_agent_q_learning, workspace_uav_rl_landing_readme_landing_controller_node [EXTRACTED 1.00]
- **px4_msgs quality assurance gates (CI, pre-commit, quality declaration)** — workspace_ros2_ws_src_px4_msgs_github_workflows_build, workspace_ros2_ws_src_px4_msgs_pre_commit_config, workspace_ros2_ws_src_px4_msgs_quality_declaration, workspace_ros2_ws_src_px4_msgs_github_dependabot [INFERRED 0.75]

## Communities (130 total, 38 thin omitted)

### Community 0 - "rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_multiresolution.py"
Cohesion: 0.08
Nodes (24): Function creates a numpy.ndarray that can be indexed according to a…, discretize_action(), discretize_relative_state(), get_discrete_action_state_from_ros_msg(), get_discrete_rel_states_from_ros_msg(), get_discrete_state_from_ros_msg(), get_latest_cur_step_for_state(), initialize_grid_list() (+16 more)

### Community 1 - "LandingSimulationObject"
Cohesion: 0.05
Nodes (21): LandingSimulationObjectState, ObservationRelativeStateMsg, CascadedPIDData, CascadedPIDInterface, Class for setting up a gym based training environment that can be used in…, LandingSimulationObject, Bool, ContactsState (+13 more)

### Community 2 - "RL Landing Repo Overview"
Cohesion: 0.08
Nodes (27): LandingCommand.msg, LandingTarget.msg, interfaces ament package, PlatformState.msg, RLObservation.msg, TakeoffSetpoint.msg, UAVState.msg, ros_gz_bridge cmd_vel bridge (+19 more)

### Community 3 - "rospy"
Cohesion: 0.13
Nodes (23): geometry_msgs_msg, librepilot_msg, mav_msgs_msg, rospy, std_msgs_msg, tf_transformations, training_q_learning_msg, training_q_learning_parameters (+15 more)

### Community 4 - "QLearning"
Cohesion: 0.09
Nodes (14): ndarray, QLearning, Function scales the values of a Q-table. Two options are available. - Mode…, Function adds num_ref_steps new curriculum steps to the sequential curriculum…, Function resets table values to predefined integer value., Function creates a numpy.ndarray that can be indexed according to a…, Class contains different functions to perform RL training for landing a multi-…, Function sets up the training environment and performs intial reset (+6 more)

### Community 5 - "patch_x500_camera.py"
Cohesion: 0.26
Nodes (11): argparse, Path, re, find_link_anchor(), find_model_sdf(), _is_file_safe(), main(), patch() (+3 more)

### Community 6 - "LandingSimulationEnv"
Cohesion: 0.15
Nodes (10): LandingSimulationEnv, Bool, Function maps an action integer number to an action string, updates the new…, Function resets the training environment and updates logging data, Function sends out a boolean value indicating that a reset has been requested.…, Function sends out a boolean value indicating that a reset has been comnpleted.…, Function performs the normalization of observations of the environment and…, Function publishes the action values that are currently set to the ROS network. (+2 more)

### Community 7 - "Sim Analysis Node"
Cohesion: 0.07
Nodes (18): AnalysisNode, Function publishes basic statistics over the ROS framework for the movement in…, Function publishes basic statistics over the ROS framework for the movement in…, Function logs and computes basic statistics for motion in x-direction., Function logs and computes basic statistics for motion in y-direction., Function prints statistics to the terminal window, Function reads the current discrete states of the longitudinal motion., Function reads the current discrete states of the lateral motion. (+10 more)

### Community 8 - "rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/custom_q_learning.py"
Cohesion: 0.22
Nodes (8): gym, rospkg, training_q_learning_utils_q_learning, This script defines a class that contains all necessary methods to perform the…, create_log_dir_path(), This script copies all the files that are necessary to determine the settings…, This is a variation of the create_log_dir_path_function in the utils script.…, This script defines a class that contains all necessary methods to perform the…

### Community 9 - "Vicon Launch Scripts"
Cohesion: 0.07
Nodes (20): src_rl_multi_rotor_landing_rl_multi_rotor_landing_gcs_other_files_setup_bash, ROS_IP, launch_audio_feedback.sh script, ROS_IP, launch_vicon_action_to_uavpose.sh script, launch_vicon_compute_relative_information.sh script, ROS_IP, launch_vicon_filter_platform_data.sh script (+12 more)

### Community 10 - "Platform Trajectory Generator"
Cohesion: 0.08
Nodes (16): Function computes a straight trajectory for the moving platform., Function computes a rectiliar periodic trajectory for the moving platform., Function computes a vertical, straight trajectory for the moving platform, Function computes a rectiliar periodic trajectory., Function computes the trajectory based on arguments trajectory_type,…, Function publishes the updated platform position to the ROS network., Function resets time to a random value within an interval of episode_length…, Function handles the service request to reset the seed for the random number… (+8 more)

### Community 11 - "time"
Cohesion: 0.10
Nodes (21): fileinput, shutil, sys, time, This script automizes the execution of the evaluation of an agent for all…, get_last_final_result_path(), get_last_parameters_file(), This script automizes the execution of the evaluation of an agent. (+13 more)

### Community 12 - "px4_msgs CI & Release"
Cohesion: 0.14
Nodes (26): px4_msgs CHANGELOG (tracks PX4 release lines 1.16, 1.17), px4_msgs CMakeLists.txt, rosidl_generate_interfaces (msg/srv glob to C++/Python/IDL), px4_msgs Code of Conduct, px4_msgs Contributing guide and release process, DCO sign-off and Conventional Commits policy, Dependabot config (github-actions updates), Pull request template (+18 more)

### Community 13 - "ActionManager"
Cohesion: 0.17
Nodes (7): ActionManager, node : rclpy.node.Node The owning node, used to create the publisher.…, Reset actions to their initial values., Update action values using the discrete action selected by the RL agent. Only…, Publish the current control command., Return the current action values., Handles UAV actions. Responsibilities ---------------- - Maintain current…

### Community 14 - "Vicon ENU-NED Conversion"
Cohesion: 0.13
Nodes (10): Convert quaterion defined in ENU frame to NED frame, Convert PoseStamped message from ENU to NED frame., Converts twist stamped message from ENU frame to NED frame., Publishes auxposition, auxvelocity in NED frame only when a new message was…, Function stores the pose and twist information together with the reference…, Reads vicon drone pose message, performs the frame conversion from ENU to NED…, Reads vicon drone pose message, performs the frame conversion from ENU to NED…, Reads vicon moving platform pose message, performs the frame conversion from… (+2 more)

### Community 15 - "QLearning"
Cohesion: 0.07
Nodes (19): ndarray, QLearning, Function scales the values of a Q-table. Two options are available. - Mode…, Function adds num_ref_steps new curriculum steps to the sequential curriculum…, Function resets table values to predefined integer value., Class contains different functions to perform RL training for landing a multi-…, Function sets up the logging system for the training environment. It handles…, Function sets up the training environment and performs intial reset (+11 more)

### Community 16 - "Episode Reset Manager"
Cohesion: 0.12
Nodes (8): True once /uav/state has converged on `pose` within tolerance., Hand control back to the RL agent's velocity commands., Disarm landing_controller (see its "disarm" mode) so the UAV actually sits…, Deliberately a no-op: moving_platform_node.py now drives the platform on a…, node : rclpy.node.Node The owning node, used to create subscriptions/publishers., Generate the UAV's initial (x, y, altitude-AGL) target for this episode.…, Command landing_controller into position-hold mode, targeting `pose`., ResetManager

### Community 17 - "numpy"
Cohesion: 0.12
Nodes (16): copy, csv, numpy, os, os_path, pandas, rosbag, socketserver (+8 more)

### Community 18 - "Vicon Relative State"
Cohesion: 0.11
Nodes (16): tf2_geometry_msgs, compute_landing_simulation_object_state_msg(), compute_relative_pos_msg(), compute_relative_vel_msg(), This scripts defines a ROS node that provides information about the moving…, Reads pose message of moving platform and stores data in storage class., Reads twist message of moving platform and stores data in storage class., Function computes the relative velocity vector between the moving platform and… (+8 more)

### Community 19 - "Vicon Debug Interface"
Cohesion: 0.14
Nodes (9): Converts twist stamped message from ENU frame to NED frame., Class containing debugging functions and required variables, Reads vicon drone pose message., Reads state estimate drone pose message., Reads vicon drone twist message., Reads state estimate drone twist message., Convert quaterion defined in ENU frame to NED frame?, Convert PoseStamped message from ENU to NED frame. (+1 more)

### Community 20 - "Sim Relative State Node"
Cohesion: 0.12
Nodes (15): compute_landing_simulation_object_state_msg(), compute_relative_acc_msg(), compute_relative_pos_msg(), compute_relative_vel_msg(), Function reads drone imu message and saves it to data class of drone., Function reads moving platform imu message and saves it to data class of moving…, Function computes the relative velocity vector between the moving platform and…, Function computes the relative position vector between the moving platform and… (+7 more)

### Community 21 - "Training Logger (Sim)"
Cohesion: 0.15
Nodes (9): Function sets up the logging system for the training environment. It handles…, LogTraining, Function saves the training and logging data, Function saves the logging data, Function handles the logging of data at the end of each episode., Class contains functions for printing out training information and for data…, Function performs operation that is executed in each timestep., Function prints info to the terminal when verbose is set to true. (+1 more)

### Community 22 - "aruco_landing_target_node.py"
Cohesion: 0.13
Nodes (12): LandingTarget, math, ArucoLandingTargetNode, build_detector_params(), euler_to_rotation_matrix(), main(), Node, World-from-body rotation matrix for the 3-2-1 (yaw, pitch, roll) Euler… (+4 more)

### Community 23 - "Sim Observation Generator"
Cohesion: 0.12
Nodes (15): compute_observation_action_msg(), compute_relative_observation_msg(), This script defines a ROS node that computes the relative information between…, Function sets a flag when the simulation is reset., Function reads the relative position message and stores the message in the…, Function reads the relative velocity message and stores the message in the…, Function reads the relative acceleration message and stores the message in the…, Function reads the setpoints for the action values of the drone. (+7 more)

### Community 24 - "Exploration Manager"
Cohesion: 0.14
Nodes (9): ExplorationManager, Choose action using epsilon-greedy policy., Update epsilon according to schedule., Restore epsilon from checkpoint., Current exploration rate., Handles epsilon-greedy exploration., decay_rate_from_schedule(), schedule.py Utility functions for learning-rate and exploration-rate scheduling. (+1 more)

### Community 25 - "grid_utils.py"
Cohesion: 0.21
Nodes (10): Create: Q(s,a) DoubleQ(s,a) VisitCounter(s,a), create_double_q_tables(), create_empty_q_table(), create_visit_counter(), initialize_grid_list(), Grid utilities. This module contains helper functions used for multi-resolution…, Create a nested numpy array whose shape matches the discretization grid.…, Create an empty Q-table. The last dimension corresponds to actions. (+2 more)

### Community 26 - "Vicon Observation Generator"
Cohesion: 0.13
Nodes (14): sensor_msgs_msg, compute_observation_action_msg(), compute_relative_observation_msg(), This script defines a ROS node that computes the relative information between…, Function reads the relative position message and stores the message in the…, Function reads the relative velocity message and stores the message in the…, Function reads the relative acceleration message and stores the message in the…, Function reads the setpoints for the action values of the drone. (+6 more)

### Community 27 - "One-Euro Platform Filter"
Cohesion: 0.19
Nodes (5): OneEuroFilter, Function stores the pose and twist data of the platform received via the vicon…, Initialize the one euro filter. Based on https://jaantollander.com/post/noise-…, Compute the filtered signal., SmoothPlatformData

### Community 28 - "rl_multi_rotor_landing_sim/src/training_q_learning/src/training_q_learning/utils_multiresolution.py"
Cohesion: 0.18
Nodes (15): discretize_action(), discretize_relative_state(), get_discrete_action_state_from_ros_msg(), get_discrete_rel_states_from_ros_msg(), get_discrete_state_from_ros_msg(), get_latest_cur_step_for_state(), Action, ObservationRelativeState (+7 more)

### Community 29 - "training_action_interface.py"
Cohesion: 0.11
Nodes (19): process_action(), publish_roll_pitch_yawrate_thrust_msg(), publish_setpoint_v_z(), publish_setpoint_yaw(), This script creates an interface node which fuses the setpoints for the roll,…, Function reads the message containing the relative pose information of moving…, Function publishes the setpoint for the PID controller of v_z based on the…, Function publishes the setpoint for the PID controller of the yaw angle based… (+11 more)

### Community 30 - "ament_flake8_main"
Cohesion: 0.15
Nodes (10): ament_flake8_main, flake8, linter, test_flake8(), flake8, linter, test_flake8(), flake8 (+2 more)

### Community 31 - "rclpy"
Cohesion: 0.25
Nodes (4): rclpy, main(), Node, RelativeStateNode

### Community 32 - "rl_multi_rotor_landing_sim/src/training_q_learning/src/training_q_learning/utils.py"
Cohesion: 0.13
Nodes (12): rosgraph, create_log_dir_path(), _get_subscribers(), Script contains functions that are generally useful to realize the training…, Function gets the list of subscribers to a topic. Source:…, Function determines a unique path where the training data should be stored…, create_log_dir_path(), detect_contact_in_msg() (+4 more)

### Community 33 - "Cascaded PID + Flight Mode"
Cohesion: 0.15
Nodes (4): CascadedPIDInterface, FlightActivated, Class stores information RL controlled flight is activated., Reads the status of the ROS controlled parameters and stores the value in the…

### Community 34 - "Parameters"
Cohesion: 0.09
Nodes (18): Parameters, get_publisher(), add_cur_step_lims_of_state(), Function reads the limit value for the different discretization steps defined…, Function gets a publisher and returns an error if the publisher is not up.…, Class for setting up a gym based training environment that can be used in…, ViconEnv, Function reads observation from corresponding topic and updates old observation… (+10 more)

### Community 35 - "LandingController"
Cohesion: 0.23
Nodes (3): LandingController, Node, Switch PX4 into its own AUTO.LAND flight mode instead of us trying to fake a…

### Community 36 - "Project Architecture & Status"
Cohesion: 0.08
Nodes (28): ArUco vision pipeline (vision_node), Double Q-learning agent with curriculum discretization, FYP UAV: Autonomous Landing of Multi-Rotor on Moving Platform, Gazebo Harmonic, Reinforcement Learning based Autonomous Multi-Rotor Landing on Moving Platforms (Goldschmid & Ahmad), Micro XRCE-DDS Agent, PX4 SITL (x500 model), pymavlink headless GCS heartbeat (+20 more)

### Community 37 - "Sim Training Parameters"
Cohesion: 0.23
Nodes (7): This script contains the parameters to set up a training case…, Class provides data about the vehicle, Class provides parameter affecting the training and values generated from the…, Class provides variables that affect the reinforcement learning algorithm and…, RLParameters, SimulationParameters, UAVParameters

### Community 38 - "config/parameters.py"
Cohesion: 0.21
Nodes (7): Parameters for the uav_rl_landing training case. Ported from the original…, # NOTE: there is no contact sensor wired up yet (no Gazebo contact, Vehicle / action-space configuration., Reinforcement-learning / curriculum configuration., RLParameters, SimulationParameters, UAVParameters

### Community 39 - "Landing Gym Env"
Cohesion: 0.24
Nodes (5): LandingEnv, Node, Apply one discrete action, advance one control period, and return (state,…, Spin this node's callbacks for approximately duration_sec, so subscription…, Reset the episode: sample a target pose, fly there for real and hold (position-…

### Community 40 - "training.py"
Cohesion: 0.29
Nodes (5): roslaunch, training_q_learning_custom_q_learning, Script creates the simulation environment that is required in order to use 4…, This script starts a training session., This script starts a training session.

### Community 41 - "landing_env.py"
Cohesion: 0.16
Nodes (7): Reinforcement learning environment for UAV landing on a moving platform. This…, reset_manager.py Handles episode reset / takeoff logic. Flow per episode…, State Discretizer Converts continuous observations (an…, Build discretization limits for every observation according to the current…, Convert one continuous value into a discrete bin index (evenly-spaced bins over…, Convert a continuous observation into a discrete state tuple. `observation`…, StateDiscretizer

### Community 42 - "ament_pep257_main"
Cohesion: 0.22
Nodes (7): ament_pep257_main, linter, pep257, test_pep257(), linter, pep257, test_pep257()

### Community 43 - "vicon_publish_stability_axes.py"
Cohesion: 0.19
Nodes (11): tf2_ros, uav_msgs_msg, publish_stability_axes_as_tf_frame(), Function publishes the stability axes frame w.r.t. the world frame., Function reads the pose messages of the copter in the vicon system., read_pose_msg(), publish_tf_transform_from_world_frame_to_copter_frame(), This script publishes the copter frame based on the state estimate of the fx as… (+3 more)

### Community 44 - "World-Base TF Publisher"
Cohesion: 0.24
Nodes (8): PositionOrientationState, publish_transform_message(), publish_world_to_world_link_transform_message(), Class for storing the current position and orientation of the moving platform, Read model state of moving platform., Function publishes the required tf transform from world frame to an additional…, Publish the transformation message to describe the motion of the moving…, read_model_state()

### Community 45 - "main"
Cohesion: 0.18
Nodes (11): copyright, linter, skip, test_copyright(), copyright, linter, skip, test_copyright() (+3 more)

### Community 47 - "Platform State Publisher (C++)"
Cohesion: 0.22
Nodes (5): jointstate, model, ros, string, transform_broadcaster

### Community 48 - "Changelog Generator"
Cohesion: 0.42
Nodes (8): contributors(), emit(), forthcoming_block(), generate(), join_csv(), names(), generate_changelog.sh script, underline()

### Community 49 - "Action to UAV Pose"
Cohesion: 0.29
Nodes (5): ActionMsg, ActionToUavPose, Class stores all data that is required to convert roll pitch yawrate thrust to…, Funcion assigns the values of roll, pitch and yaw to the velocity field of the…, Function processes the msgs received on the topic

### Community 52 - "landing_simulation_env.py"
Cohesion: 0.18
Nodes (10): gazebo_msgs_msg, gazebo_msgs_srv, gym_envs_registration, rostopic, std_srvs_srv, tf, training_q_learning_srv, This script contains the definition of a node that can be used for testing and… (+2 more)

### Community 53 - "q_learning.py"
Cohesion: 0.19
Nodes (9): build_grid(), main(), QLearning, q_learning.py Double Q-learning training loop (Hasselt 2010), ported from the…, Log/save/decay after an episode. Returns True if training should stop., Load previously saved Q-tables (as produced by save())., QTableManager, q_table.py Creates and manages the Q-Tables used by Double Q-Learning. (+1 more)

### Community 55 - "Stability Axes TF"
Cohesion: 0.33
Nodes (6): nav_msgs_msg, publish_stability_axes_as_tf_frame(), Function publishes the stability axes as tf frame. The stability axes xy-plane…, Function publishes the stability axes frame w.r.t. the world frame., Function reads the odometry messages of the drone and triggers publishing of…, read_odom_msg()

### Community 57 - "moving_platform_node.py"
Cohesion: 0.33
Nodes (4): main(), MovingPlatformNode, Node, Publishes the moving platform's ground-truth state (PlatformState, the RL…

### Community 58 - "Relative State Node"
Cohesion: 0.22
Nodes (4): termination.py Episode termination / success logic. This has no equivalent file…, Call at the start of every episode., Returns (done: bool, outcome: str, success: bool). outcome is one of:…, TerminationManager

### Community 59 - "interfaces_msg"
Cohesion: 0.22
Nodes (5): interfaces_msg, main(), Node, Vision-based drop-in alternative to relative_state package's…, VisionRelativeStateNode

### Community 60 - "Catkin Packages"
Cohesion: 0.33
Nodes (6): training_q_learning catkin package (GCS/Vicon), Vicon scripts (vicon_interface, vicon_test_model_2D, vicon_cascaded_pid_controller, ...), training_q_learning catkin package (simulation), ResetRandomSeed.srv, Custom ROS messages (Action, ObservationRelativeState, TwistModified, LandingSimulationObjectState), Simulation scripts (training.py, observation_generator.py, test_model_2D.py, cascaded_pid_controller.py, ...)

### Community 61 - "UAV Pose From State Estimate"
Cohesion: 0.40
Nodes (3): Class stores all data that is required to convert roll pitch yawrate thrust to…, Function processes the msgs received on the topic, UAVPoseFromStateEstimate

### Community 62 - "write_data_to_csv"
Cohesion: 0.19
Nodes (6): LogTopicFreqs, This is a variation of the create_log_dir_path_function in the utils script.…, LogTopicFreqs, This is a variation of the create_log_dir_path_function in the utils script.…, Functions writes a list of values as a row to a .csv file., write_data_to_csv()

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

### Community 84 - "rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_q_learning.py"
Cohesion: 0.18
Nodes (10): datetime, pickle, rosnode, torch_utils_tensorboard, decay_rate_from_schedule(), This script contains the definitions of classes and function that are required…, Function determines the decay rate that has been defined using a dictionary.…, decay_rate_from_schedule() (+2 more)

### Community 85 - "rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/parameters.py"
Cohesion: 0.23
Nodes (7): This script contains the parameters to set up a training case…, Class provides data about the vehicle, Class provides parameter affecting the training and values generated from the…, Class provides variables that affect the reinforcement learning algorithm and…, RLParameters, SimulationParameters, UAVParameters

### Community 87 - "Sim Environment Setup"
Cohesion: 0.50
Nodes (3): setup.bash script, ROS_PACKAGE_PATH, ROS_PROJECT_ROOT

### Community 88 - "plot_topic_freq_from_flight.py"
Cohesion: 0.36
Nodes (6): matplotlib_pyplot, calcualte_windowed_freqs_over_time(), create_plot(), decompose_vector(), plot_topic_frequency(), This script can be used to plot the frequencies of the ROS topics that were…

### Community 89 - "test_marker_detection.py"
Cohesion: 0.33
Nodes (4): cv2, pathlib, Generates the ArUco marker image used as the visual landing target on top of…, Standalone sanity check for the ArUco detection logic in…

### Community 90 - "Copyright Lint Tests"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 91 - "Copyright Lint Tests"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 92 - "flake8 Lint Tests (relative_state)"
Cohesion: 0.50
Nodes (3): flake8, linter, test_flake8()

### Community 93 - "pep257 Lint Tests (relative_state)"
Cohesion: 0.50
Nodes (3): linter, pep257, test_pep257()

### Community 94 - "Copyright Lint Tests"
Cohesion: 0.50
Nodes (4): copyright, linter, skip, test_copyright()

### Community 95 - "landing_controller_node.py"
Cohesion: 0.38
Nodes (5): px4_msgs_msg, rclpy_node, rclpy_qos, main(), main()

### Community 101 - "test_pep257"
Cohesion: 0.50
Nodes (3): linter, pep257, test_pep257()

### Community 104 - "Issue template chooser config"
Cohesion: 0.67
Nodes (3): Bug report issue template, Issue template chooser config, Feature request issue template

### Community 127 - "px4_bridge/test/test_flake8.py"
Cohesion: 0.50
Nodes (3): flake8, linter, test_flake8()

### Community 128 - "test_pep257"
Cohesion: 0.50
Nodes (3): linter, pep257, test_pep257()

## Knowledge Gaps
- **127 isolated node(s):** `archive_training_results.sh script`, `init_workspaces.sh script`, `kill_vicon.sh script`, `prepare_terminal_window.sh script`, `record_rosbag.bash script` (+122 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 621 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **38 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `main()` connect `main` to `test_pep257`, `test_pep257`, `ament_pep257_main`, `test_marker_detection.py`, `Copyright Lint Tests`, `Copyright Lint Tests`, `pep257 Lint Tests (relative_state)`, `Copyright Lint Tests`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Why does `RLObservation.msg` connect `RL Landing Repo Overview` to `q_learning.py`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `Parameters` (e.g. with `QLearning` and `get_discrete_rel_states_from_ros_msg()`) actually correct?**
  _`Parameters` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `archive_training_results.sh script`, `init_workspaces.sh script`, `kill_vicon.sh script` to the rest of the system?**
  _127 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `rl_multi_rotor_landing_gcs/src/training_q_learning/src/training_q_learning/utils_multiresolution.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07862903225806452 - nodes in this community are weakly interconnected._
- **Should `LandingSimulationObject` be split into smaller, more focused modules?**
  _Cohesion score 0.047474747474747475 - nodes in this community are weakly interconnected._
- **Should `RL Landing Repo Overview` be split into smaller, more focused modules?**
  _Cohesion score 0.082010582010582 - nodes in this community are weakly interconnected._