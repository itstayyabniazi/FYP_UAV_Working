"""
Parameters for the uav_rl_landing training case.

Ported from the original paper's tabular Double Q-learning config, adapted to:
- the field names actually published on interfaces/msg/RLObservation
  (rel_x, rel_y, rel_z, rel_vx, rel_vy, rel_vz, rel_yaw) instead of the
  paper's rel_p_x/rel_v_x/rel_a_x naming
- a velocity-setpoint action (vx, matching interfaces/msg/LandingCommand)
  instead of the paper's attitude-setpoint (pitch) action, since PX4 offboard
  control here is driven with TrajectorySetpoint.velocity
- no relative-acceleration observation: the original repo derived rel_a_x by
  filtering, but nothing in this repo currently publishes/derives an
  acceleration signal, so the acceleration-based curriculum terms from the
  paper are dropped for this MVP. Extend observation_msg_strings /
  discretization_steps here (and relative_state_node.py) if you add it later.

Never change the content of this file while a training run is in progress.
"""
import numpy as np


class UAVParameters:
    def __init__(self):
        """Vehicle / action-space configuration."""

        # Setpoints applied at the beginning of each episode
        self.initial_action_values: dict = {
            "vx": 0.0,          # [m/s], commanded relative-frame forward velocity
            "vy": 0.0,          # [m/s], not controlled by the RL agent in this MVP
            "vz": 0.35,         # [m/s], constant commanded descent rate (PX4 NED: +z = down)
            "yaw_rate": 0.0,    # [rad/s], not controlled by the RL agent in this MVP
        }

        # Discrete actions available to the agent (mirrors the paper's
        # increase/decrease/do_nothing scheme, applied to vx instead of pitch)
        self.action_strings: dict = {
            0: "increase_vx",
            1: "decrease_vx",
            2: "do_nothing",   # must stay last
        }

        # Maximum / increment values for the controlled action
        self.action_max_values: dict = {"vx": 1.5}       # [m/s]
        self.action_delta_values: dict = {"vx": 0.15}    # [m/s]

        # Observations used to build the discretized RL state.
        # Kept to the longitudinal axis for the first working version, same as
        # the paper's default config; add "rel_y"/"rel_vy" here (and to
        # discretization_steps below) once the moving platform actually moves
        # laterally and the setup has been validated end to end in 1D.
        self.observation_msg_strings: dict = {
            0: "rel_x",   # [m]
            1: "rel_vx",  # [m/s]
        }

        # Bounds used to normalize/discretize each observation
        self.observation_max_values: dict = {
            "rel_x": 4.5,     # [m]
            "rel_y": 4.5,     # [m]
            "rel_vx": 3.0,    # [m/s]
            "rel_vy": 3.0,    # [m/s]
            "rel_yaw": np.pi,  # [rad]
        }
        return


class RLParameters:
    def __init__(self):
        """Reinforcement-learning / curriculum configuration."""
        # Load / resume ---------------------------------------------------
        self.load_data_from: str = ""
        self.proceed_from_last_episode: bool = False
        self.number_new_curriculum_steps: int = 0
        self.copy_table_list: list = ["Q_table", "Q_table_double", "state_action_counter"]

        # Training ----------------------------------------------------------
        self.curriculum_step: int = 0  # indexing starts at 0

        self.number_of_successful_episodes: int = 100
        self.successful_fraction: float = 0.96
        self.cur_step_success_duration: float = 1.0  # [s]

        # Discretization: bin range per observation, shrinking with each
        # successive curriculum step (index 0 = coarsest / first trained)
        self.discretization_steps: dict = {
            "rel_x":  [1.0, 0.64, 0.4096, 0.262144, 0.16777216],
            "rel_vx": [1.0, 0.8, 0.64, 0.512, 0.4096],
            "rel_y":  [1.0, 0.64, 0.4096, 0.262144, 0.16777216],
            "rel_vy": [1.0, 0.8, 0.64, 0.512, 0.4096],
        }

        # Number of discrete bins per observation
        self.n_r: int = 3

        # Agent frequency
        self.f_ag: float = 10.0  # [Hz] -- matches relative_state_node's 0.02s /
        # landing_controller's 0.05s timers; the RL step itself runs at 10 Hz
        self.running_step_time: float = 1.0 / self.f_ag

        self.max_num_timesteps: int = int(self.f_ag * 3600 * 24 * 2)
        self.t_max: float = 25.0  # [s] per episode
        self.max_num_timesteps_episode: int = int(self.f_ag * self.t_max)
        self.max_num_episodes: int = 50000

        # Learning rate
        self.learning_rate = "adaptive"  # 'adaptive' | dict schedule | float
        self.omega: float = 0.51
        self.alpha_min: float = 0.02949

        self.gamma: float = 0.99

        # Exploration schedule: {idx: [mode, start_episode, end_episode, start_eps, end_eps]}
        self.exploration_rate_schedule: dict = {
            0: ["lin", 0, 800, 1.0, 1.0],
            1: ["lin", 800, 3000, 1.0, 0.01],
        }
        self.exploration_initial_eps: float = 1.0

        self.seed_init = None

        # Logging -----------------------------------------------------------
        self.episode_save_freq: int = 50
        self.print_info_freq: int = 1
        self.print_info_mean_number: int = 20
        self.verbose: bool = True
        self.q_learning_algorithm: str = "double_q_learning"
        return


class SimulationParameters(UAVParameters):
    def __init__(self):
        super().__init__()

        # Initial UAV position at the beginning of each episode, drawn as an
        # offset from the platform's live position (see reset_manager.py's
        # generate_initial_pose()) -- not an absolute world position.
        self.init_distribution: str = "uniform"  # 'normal' | 'uniform'
        self.init_mu_x: float = 0.0
        self.init_sigma_x: float = 1.5
        self.init_min_x: float = -4.0
        self.init_max_x: float = 4.0
        self.init_min_y: float = 0.0
        self.init_max_y: float = 0.0

        self.init_altitude: float = 3.0  # [m] AGL

        # Below this altitude above the platform (rel_z), with no successful
        # landing criteria met, the episode ends as a failed/crash landing.
        # NOTE: there is no contact sensor wired up yet (no Gazebo contact
        # plugin bridged to ROS 2 in this repo), so "touchdown" is inferred
        # purely from rel_z crossing this threshold, not a real contact event.
        self.minimum_altitude: float = 0.3  # [m]

        # Reward weights (paper's shaping reward, same structure)
        self.w_p: float = -100.0
        self.w_v: float = -10.0
        self.w_theta: float = -1.55
        self.w_dur: float = -6.0
        self.w_fail: float = -2.6
        self.w_suc: float = 2.6

        self.done_criteria: dict = {
            "max_lon_distance": True,
            "max_lat_distance": True,
            "max_num_timesteps": True,
            "minimum_altitude": True,
            "success": True,
        }

        self.max_abs_p_x: float = 4.5  # [m]
        self.max_abs_p_y: float = 4.5  # [m]

        # Success criteria, checked once rel_z <= minimum_altitude
        self.success_horizontal_radius: float = 0.35  # [m]
        self.success_max_rel_speed: float = 0.5        # [m/s]

        # Reset/takeoff phase: how close (position, in m / velocity, in m/s)
        # the UAV must get to the sampled target pose before the RL-controlled
        # part of the episode is allowed to start, and how long to wait for
        # that before giving up and starting the episode anyway.
        self.takeoff_position_tolerance: float = 0.3   # [m]
        self.takeoff_velocity_tolerance: float = 0.3   # [m/s]
        self.takeoff_timeout: float = 15.0             # [s]


class Parameters:
    def __init__(self):
        self.uav_parameters = UAVParameters()
        self.rl_parameters = RLParameters()
        self.simulation_parameters = SimulationParameters()
        return
