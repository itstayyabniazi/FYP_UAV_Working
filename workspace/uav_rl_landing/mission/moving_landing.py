"""
moving_landing.py

Phase 3 mission: land on a platform that MOVES (straight line, constant speed,
optionally back and forth). Same front half as Phase 2 -- take off, patrol the
corners of a square, stop at the first marker sighting -- then:

    LOCK    estimate the marker's position and VELOCITY (target_tracker.py) and
            fly in velocity mode: v_cmd = v_platform + Kp * (p_platform - p_uav).
            The feed-forward term is what "aligns with its motion": once locked,
            the UAV moves with the platform and the remaining error is small and
            steady, instead of trailing behind it.
    DESCEND only while aligned (position error and velocity mismatch both
            small); hold altitude otherwise. Below servo_min_altitude the marker
            leaves the camera's field of view, so the descent continues on the
            constant-velocity PREDICTION of where the platform is.
    TOUCH   from handoff_altitude keep matching the platform's velocity and
            sink slowly until CONTACT (vertical speed drops to ~0 while still
            commanding descent), THEN hand over to PX4 AUTO.LAND to disarm. Handing
            over earlier would leave the UAV stopped in the air while the platform
            slides on: ~1 s of AUTO.LAND descent x platform speed = up to a metre
            of drift at 1 m/s (0.25 m at 0.4 m/s), against a 0.75 m half-width.
    LOST    marker gone while still high: climb toward the predicted position
            (position mode) to widen the view; re-acquire -> LOCK, else PATROL.

Assumes constant velocity between samples. A reversal or turn shows up as a
tracking error for about one tracker window (1.2 s) before the fit catches up --
harmless while the marker is visible, but BELOW servo_min_altitude the UAV is
blind and a reversal in that last ~2 s (or during AUTO.LAND) can cost up to about
a metre of offset. The blind stretch is crossed at blind_descent_rate to keep it
short; it cannot be removed with this camera geometry.

Uses the same `io` interface as vision_landing.py plus:
    enter_velocity_mode()               switch the flight controller to velocity setpoints
    command_velocity(vn, ve, vd)        NED velocity setpoint [m/s] (vd positive = down)
    uav_velocity() -> (vn, ve, vd)
    drain_samples() -> [(t_capture, x, y, t_received)]   new absolute marker samples since the last call
    platform_truth() -> (x, y, vx, vy) | None   sim ground truth, NED, evaluation only
    start_platform()                    tell the platform node to begin moving
"""
import math
from dataclasses import dataclass

from mission.target_tracker import TargetTracker
from mission.vision_landing import VisionLander, VisionLandingConfig


@dataclass
class MovingLandingConfig(VisionLandingConfig):
    handoff_altitude: float = 0.3    # [m] start of the velocity-matched TOUCHDOWN phase (not an AUTO.LAND hand-off)
    touchdown_rate: float = 0.5      # [m/s] sink rate during the touchdown phase (faster = shorter blind window, harder contact)
    contact_speed_tol: float = 0.08  # [m/s] vertical speed below this while commanding descent = in contact
    contact_min_time: float = 0.3    # [s] ignore "no vertical speed" this soon after the phase starts
    contact_floor: float = -0.3      # [m] altitude at which contact is assumed regardless
    touchdown_timeout: float = 6.0   # [s] assume contact after this long in the touchdown phase
    # The camera is compared with /platform/state, which can drift from the real Gazebo model (real-time
    # factor < 1 vs a wall-clock node), so this is looser than Phase 2's 1 m. A flipped axis is metres off.
    mismatch_tolerance: float = 2.0  # [m]
    kp: float = 1.0                  # [1/s] position error -> velocity correction
    kz: float = 1.0                  # [1/s] altitude error -> vertical velocity
    max_speed: float = 2.5           # [m/s] horizontal velocity command limit
    # Limits how fast the velocity COMMAND may change. The camera estimate of the platform's velocity is
    # contaminated by (latency error) x (the UAV's own acceleration); capping the acceleration bounds that bias,
    # which is what keeps a slightly wrong camera_latency from destabilising the lock.
    max_accel: float = 1.0           # [m/s^2]
    lock_timeout: float = 25.0       # [s] give up (-> LOST) if not aligned within this long of starting the LOCK
    max_climb: float = 1.0           # [m/s]
    max_sink: float = 1.2            # [m/s]
    # Below servo_min_altitude the UAV is blind (marker out of the camera's view)
    # and cannot see the platform change speed or direction, so cross that last
    # stretch quickly to keep the blind window short.
    blind_descent_rate: float = 1.0  # [m/s]
    align_speed_tol: float = 0.3     # [m/s] UAV-vs-platform velocity mismatch allowed while descending
    fresh_age: float = 0.5           # [s] a sample this recent counts as "seeing the marker right now"
    tracker_window: float = 1.2      # [s]
    tracker_min_samples: int = 8
    tracker_min_span: float = 0.5    # [s]
    max_extrapolation: float = 6.0   # [s] how long to keep predicting without a detection
    start_platform: bool = False     # send /moving_platform/start when airborne
    use_ground_truth: bool = True    # cross-check + evaluate against /platform/state (never steers)


class MovingPlatformLander(VisionLander):

    def __init__(self, io, config: MovingLandingConfig = None, log=print):
        super().__init__(io, config or MovingLandingConfig(), log)
        c = self.cfg
        self.tracker = TargetTracker(c.tracker_window, c.tracker_min_samples, c.tracker_min_span,
                                     c.max_speed, c.max_extrapolation)

    # -- hooks ------------------------------------------------------------

    def _on_airborne(self):
        if self.cfg.start_platform:
            self.log("Airborne at search altitude -- telling the platform to start moving.")
            self.io.start_platform()

    def _expected_now(self):
        if not self.cfg.use_ground_truth:
            return None
        truth = self.io.platform_truth()
        return None if truth is None else (truth[0], truth[1])

    def _feed_tracker(self):
        for t, x, y, received in self.io.drain_samples():
            self.tracker.update(t, x, y, received)

    # -- LOCK / DESCEND -----------------------------------------------------

    def _track(self):
        cfg, io = self.cfg, self.io
        io.enter_velocity_mode()
        self._feed_tracker()
        x, y, alt = io.uav_position()
        sp_alt = alt                          # altitude setpoint, slid down while aligned
        last_seen = io.now()
        lock_started = last_seen
        descending = False
        locked = False
        last_log = io.now()
        vn0, ve0, _ = io.uav_velocity()
        cmd_prev = (vn0, ve0)                 # last horizontal command, for the acceleration limit
        last_state = None
        touchdown_since = None                # set when the touchdown phase begins
        contact_since = None
        self.log("LOCK: tracking the platform in velocity mode "
                 f"(kp={cfg.kp}, descent {cfg.descent_rate} m/s while aligned).")

        while True:
            self._check_timeout()
            now = io.now()
            self._feed_tracker()
            x, y, alt = io.uav_position()
            vn, ve, _ = io.uav_velocity()
            state = self.tracker.state(now)
            fresh = self.tracker.fresh(now, cfg.fresh_age)
            if fresh:
                last_seen = now
            blind = alt <= cfg.servo_min_altitude
            if state is None and blind and last_state is not None:
                state = last_state            # blind and out of samples: finish the landing on the last estimate
            if state is None or (not fresh and not blind and now - last_seen > cfg.lost_timeout):
                self.log(f"Marker lost at {alt:.1f} m (no detection for {now - last_seen:.1f} s).")
                return "LOST"
            if not locked and now - lock_started > cfg.lock_timeout:
                self.log(f"Could not lock on within {cfg.lock_timeout:.0f} s (tracking unstable?) -- giving up this attempt.")
                return "LOST"
            last_state = state

            ex, ey = state.x - x, state.y - y
            err = math.hypot(ex, ey)
            rel_speed = math.hypot(state.vx - vn, state.vy - ve)
            self.target = (state.x, state.y)

            aligned = state.velocity_valid and err <= cfg.align_tol and rel_speed <= cfg.align_speed_tol
            loose = (not state.velocity_valid) or err >= cfg.realign_tol
            if aligned:
                descending = True
            elif loose and not (blind and descending):
                descending = False            # (a descent already under way below the floor is finished, not cancelled)
            if not fresh and not blind:
                descending = False            # never sink blind above the servo floor

            if aligned and not locked:
                locked = True
                self.log(f"LOCKED on the platform: moving at ({state.vx:+.2f} N, {state.vy:+.2f} E) m/s, "
                         f"tracking error {err:.2f} m, velocity mismatch {rel_speed:.2f} m/s. Descending.")
                truth = io.platform_truth()
                if truth is not None and math.hypot(truth[2], truth[3]) > 0.15:
                    # Tracked speed is measured in wall-clock; a wall-clock platform node commands the same speed per
                    # WALL second, but Gazebo moves the model per SIM second, so the ratio is the real-time factor.
                    rtf = math.hypot(state.vx, state.vy) / math.hypot(truth[2], truth[3])
                    if rtf < 0.97 or rtf > 1.03:
                        self.ground_truth_unreliable = True
                        self.log(f"  NOTE: the tracked platform speed is {rtf:.0%} of /platform/state's, i.e. the "
                                 f"simulation runs at ~{rtf:.0%} of real time, so /platform/state drifts from the "
                                 "real platform and the final 'offset from platform centre' below will be "
                                 "unreliable -- watch the 'Contact at ... from the predicted platform position' "
                                 "line instead, that one is not affected. Run moving_platform_node with "
                                 "-p use_sim_time:=true (vision_node README).")

            # Horizontal: feed-forward the platform's velocity, correct the position error.
            cmd_n = state.vx + cfg.kp * ex
            cmd_e = state.vy + cfg.kp * ey
            speed = math.hypot(cmd_n, cmd_e)
            if speed > cfg.max_speed:
                cmd_n, cmd_e = cmd_n * cfg.max_speed / speed, cmd_e * cfg.max_speed / speed
            step = cfg.max_accel * cfg.dt                       # acceleration limit on the command
            dn, de = cmd_n - cmd_prev[0], cmd_e - cmd_prev[1]
            change = math.hypot(dn, de)
            if change > step:
                cmd_n, cmd_e = cmd_prev[0] + dn * step / change, cmd_prev[1] + de * step / change
            cmd_prev = (cmd_n, cmd_e)

            # Vertical: slide the altitude setpoint down while aligned, P-control onto it.
            if touchdown_since is None and descending and alt <= cfg.handoff_altitude + 0.05 and err <= 0.35:
                touchdown_since = now
                self.log(f"TOUCHDOWN phase at {alt:.2f} m: matching the platform's velocity and sinking at "
                         f"{cfg.touchdown_rate} m/s until contact.")
            if touchdown_since is not None:
                sp_alt = max(cfg.contact_floor, sp_alt - cfg.touchdown_rate * cfg.dt)
            elif descending:
                rate = cfg.blind_descent_rate if blind else cfg.descent_rate
                sp_alt = max(cfg.handoff_altitude, sp_alt - rate * cfg.dt)
            climb = max(-cfg.max_sink, min(cfg.max_climb, cfg.kz * (sp_alt - alt)))
            io.command_velocity(cmd_n, cmd_e, -climb)          # NED: down is positive
            io.sleep(cfg.dt)

            if touchdown_since is not None:
                _, _, vd = io.uav_velocity()
                in_contact = (now - touchdown_since) >= cfg.contact_min_time and abs(vd) <= cfg.contact_speed_tol
                contact_since = (contact_since or now) if in_contact else None
                if ((contact_since is not None and now - contact_since >= 0.2) or alt <= cfg.contact_floor
                        or now - touchdown_since > cfg.touchdown_timeout):
                    self.log(f"Contact at {alt:.2f} m ({now - touchdown_since:.1f} s into the touchdown phase), "
                             f"{err:.2f} m from the predicted platform position. Handing over to PX4 to disarm.")
                    return "FINAL"

            if now - last_log >= cfg.progress_period:
                last_log = now
                self.log(f"  ... alt {alt:.1f} m, error {err:.2f} m, platform ({state.vx:+.2f}, "
                         f"{state.vy:+.2f}) m/s{'' if fresh else ' [predicted, not visible]'}"
                         f"{' [descending]' if descending else ' [holding altitude]'}")


    # -- LOST ---------------------------------------------------------------

    def _recover(self):
        """Climb toward where the platform should be NOW (constant-velocity
        prediction) in position mode; re-lock on sight, else patrol again."""
        cfg, io = self.cfg, self.io
        x, y, alt = io.uav_position()
        io.start(x, y, alt)                    # back to position mode, holding here
        self.sp = [x, y, alt]
        self.log("RECOVER: climbing toward the platform's predicted position.")
        deadline = None
        while True:
            self._check_timeout()
            self._feed_tracker()
            state = self.tracker.state(io.now())
            tx, ty = (state.x, state.y) if state is not None else self.target
            arrived = self._step(tx, ty, cfg.search_altitude, cfg.approach_speed, cfg.climb_speed)
            if self._seen():
                return self._acquired()
            if arrived:
                deadline = deadline or io.now() + cfg.recover_wait
                if io.now() > deadline:
                    self.tracker.reset()
                    return "PATROL"

    # -- result -------------------------------------------------------------

    def run(self):
        self.ground_truth_unreliable = False
        summary = super().run()
        truth = self.io.platform_truth() if self.cfg.use_ground_truth else None
        if truth is not None and summary.get("final_xy") is not None:
            dn, de = summary["final_xy"][0] - truth[0], summary["final_xy"][1] - truth[1]
            summary["offset_from_platform_centre"] = (dn, de)
        summary["ground_truth_unreliable"] = self.ground_truth_unreliable
        return summary
