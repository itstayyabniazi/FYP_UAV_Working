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
from collections import deque
from dataclasses import dataclass

from mission.target_tracker import TargetState, TargetTracker
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
    max_speed: float = 2.5           # [m/s] horizontal velocity command limit -- the UAV's OWN flight authority
    # The tracker's own velocity-ESTIMATE clip, separate from max_speed above. These used to be the
    # same field (TargetTracker was constructed with max_speed directly) -- harmless while both were
    # small, but once max_speed is raised well past the platform's real speed (e.g. --fast's 4.0 m/s
    # for a 1.39 m/s platform, so the UAV has spare authority to catch up), a noisy/bad camera fit
    # can report a velocity up to max_speed as "the platform's velocity", nowhere near physically
    # plausible for this platform, and the control loop trusts it directly as feedforward
    # (cmd = state.vx + kp*error). A real PX4-controlled vehicle chasing that bad estimate is a real
    # flight-safety risk, not just a bad landing -- confirmed by a real Gazebo crash immediately
    # after the tracker reported ~3 m/s for a platform that never exceeds ~1.4-2 m/s. Keep this near
    # the platform's actual expected speed with headroom for noise, well below max_speed.
    tracker_max_speed: float = 2.5   # [m/s] tracker velocity-estimate clip -- keep near the REAL platform speed
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
    # Extrapolate the tracker along a turning arc instead of a straight line (see
    # target_tracker.py's module docstring) -- for a platform moving on a curve (Phase 3
    # circular motion), not a straight line. Off by default: False reproduces the exact
    # straight-line extrapolation this (hardware-validated, straight-line) mission was tuned
    # against, byte for byte.
    tracker_curvature: bool = False
    # Learned motion predictor (prediction/, opt-in; None = off = the behaviour above, unchanged). With a weights file
    # the BLIND stretch (below servo_min_altitude, where the marker is out of view) flies the LSTM-MDN's prediction
    # instead of the tracker's straight-line / constant-turn extrapolation. With mdn_gate_sigma set, the descent also
    # PAUSES in the band just above the blind floor while the predictor says the platform's position a
    # mdn_gate_horizon s from now is too uncertain (spread = sqrt(trace of the whole mixture's covariance)), for at
    # most mdn_gate_max_hold seconds in total, then goes down anyway.
    mdn_path: str = None
    mdn_gate_sigma: float = None     # [m] hold the descent while the predicted spread exceeds this (None = no gate)
    mdn_gate_horizon: float = 2.5    # [s] how far ahead the gate looks: about the blind stretch plus the touchdown
    mdn_gate_band: float = 0.5       # [m] the gate acts between servo_min_altitude and servo_min_altitude + this
    mdn_gate_max_hold: float = 15.0  # [s]
    mdn_point: str = "mean"          # which point of the predicted mixture to fly: "mean", "best" (top-weight mode) or "peak" (densest)


class MovingPlatformLander(VisionLander):

    def __init__(self, io, config: MovingLandingConfig = None, log=print):
        super().__init__(io, config or MovingLandingConfig(), log)
        c = self.cfg
        self.tracker = TargetTracker(c.tracker_window, c.tracker_min_samples, c.tracker_min_span,
                                     c.tracker_max_speed, c.max_extrapolation, curvature=c.tracker_curvature)
        self.offset_at_contact = None         # [m] UAV vs ground-truth platform centre at the moment of contact
        self.mdn = None
        self._mdn_hist = deque()              # (t, north, east) detections, ~3 s: the predictor needs more than the tracker keeps
        self._mdn_ctx = (None, None, None)    # (key, context, t_ref) cache: the network input only changes with new samples
        self.gate_held = 0.0                  # [s] total time the MDN gate has paused the descent
        if c.mdn_path:
            from prediction.mdn_numpy import MDNPredictor     # imported here so a run without the predictor needs nothing extra
            self.mdn = MDNPredictor.load(c.mdn_path)

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
            if self.mdn is not None:
                self._mdn_hist.append((t, x, y))
                while self._mdn_hist and self._mdn_hist[0][0] < t - 3.0:
                    self._mdn_hist.popleft()

    def _mdn_predict(self, now, ahead=0.0):
        """The predictor's view of the platform at `now + ahead`: (Prediction, H) or (None, None). The tracker works
        in NED (x = north, y = east); the predictor in ENU, so the axes are swapped on the way in and out."""
        if self.mdn is None or len(self._mdn_hist) < 4:
            return None, None
        key = (len(self._mdn_hist), self._mdn_hist[-1][0])
        if self._mdn_ctx[0] != key:
            h = list(self._mdn_hist)
            ctx, t_ref = self.mdn.prepare([e[0] for e in h], [e[2] for e in h], [e[1] for e in h])
            self._mdn_ctx = (key, ctx, t_ref)
        _, ctx, t_ref = self._mdn_ctx
        if ctx is None:
            return None, None
        H = now + ahead - t_ref
        if not 0.0 <= H <= 4.0:                      # outside what it was trained on: let the tracker handle it
            return None, None
        return self.mdn.predict_from(ctx, H), H

    def _mdn_state(self, now):
        """TargetState from the predictor for the blind stretch (None = fall back to the tracker)."""
        pred, H = self._mdn_predict(now)
        if pred is None:
            return None
        later, _ = self._mdn_predict(now, 0.25)
        pick = {"mean": lambda p: (p.x, p.y), "best": lambda p: (p.best_x, p.best_y),
                "peak": lambda p: (p.peak_x, p.peak_y)}[self.cfg.mdn_point]
        x, y = pick(pred)
        vn = ve = 0.0
        if later is not None:
            lx, ly = pick(later)
            ve, vn = (lx - x) / 0.25, (ly - y) / 0.25
        return TargetState(y, x, vn, ve, True, len(self._mdn_hist), now - self._mdn_hist[-1][0])

    # -- LOCK / DESCEND -----------------------------------------------------

    def _track(self):
        cfg, io = self.cfg, self.io
        io.enter_velocity_mode()
        self._feed_tracker()
        x, y, alt = io.uav_position()
        sp_alt = alt                          # altitude setpoint, slid down while aligned
        last_seen = io.now()
        last_seen_alt = alt
        lock_started = last_seen
        descending = False
        locked = False
        last_log = io.now()
        vn0, ve0, _ = io.uav_velocity()
        cmd_prev = (vn0, ve0)                 # last horizontal command, for the acceleration limit
        last_state = None
        touchdown_since = None                # set when the touchdown phase begins
        contact_since = None
        warned_slow_gains = False
        gate_holding = False
        tilt_of = getattr(io, "uav_tilt", None)      # log-only diagnostic (the fake world has no attitude)
        was_fresh, last_drop_log = False, -10.0
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
                last_seen_alt = alt
            blind = alt <= cfg.servo_min_altitude
            if tilt_of is not None and was_fresh and not fresh and not blind and now - last_drop_log > 2.0:
                # Is the marker leaving the camera's view because the UAV tilts (fixed downward camera)?
                last_drop_log = now
                self.log(f"  Marker dropped out of view at {alt:.1f} m: UAV tilt {tilt_of():.0f} deg, speed "
                         f"{math.hypot(vn, ve):.1f} m/s, error to the predicted position {math.hypot(state.x - x, state.y - y):.2f} m."
                         if state is not None else f"  Marker dropped out of view at {alt:.1f} m: UAV tilt {tilt_of():.0f} deg.")
            was_fresh = fresh
            if blind and self.mdn is not None:
                mdn_state = self._mdn_state(now)
                if mdn_state is not None:
                    state = mdn_state
            if state is None and blind and last_state is not None:
                state = last_state            # blind and out of samples: finish the landing on the last estimate
            if state is None or (not fresh and not blind and now - last_seen > cfg.lost_timeout):
                self.log(f"Marker lost at {alt:.1f} m (no detection for {now - last_seen:.1f} s).")
                return "LOST"
            if not locked and now - lock_started > cfg.lock_timeout:
                self.log(f"Could not lock on within {cfg.lock_timeout:.0f} s (tracking unstable?) -- giving up this attempt.")
                return "LOST"
            last_state = state
            if (not warned_slow_gains and state.velocity_valid and cfg.max_accel <= 1.0
                    and math.hypot(state.vx, state.vy) > 0.75):
                warned_slow_gains = True
                self.log(f"  WARNING: the platform is moving at ~{math.hypot(state.vx, state.vy):.2f} m/s, faster than the "
                         "default gains can follow (offline they never lock above ~0.8 m/s). If this run does not lock "
                         "on, restart the mission with --fast (circular_landing_main.py).")

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

            # MDN descent gate: in the band just above the blind floor, pause while the predictor is unsure where the
            # platform will be by the time we have crossed the blind stretch (hysteresis: resume below 0.8 x sigma).
            gate_hold = False
            if (self.mdn is not None and cfg.mdn_gate_sigma is not None and descending and fresh
                    and cfg.servo_min_altitude < alt <= cfg.servo_min_altitude + cfg.mdn_gate_band):
                gate_pred, _ = self._mdn_predict(now, cfg.mdn_gate_horizon)
                if gate_pred is not None and self.gate_held < cfg.mdn_gate_max_hold:
                    limit = cfg.mdn_gate_sigma * (0.8 if gate_holding else 1.0)
                    gate_hold = gate_pred.spread > limit
                    if gate_hold != gate_holding:
                        self.log(f"  MDN gate: predicted spread {gate_pred.spread:.2f} m {'>' if gate_hold else '<='} "
                                 f"{limit:.2f} m at {alt:.2f} m -> {'holding the descent' if gate_hold else 'descending'}"
                                 f" ({self.gate_held:.1f} s held so far).")
                    gate_holding = gate_hold
                    if gate_hold:
                        self.gate_held += cfg.dt
                elif gate_holding:
                    gate_holding = False
                    self.log(f"  MDN gate: hold limit of {cfg.mdn_gate_max_hold:.0f} s reached -- descending anyway.")

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
            elif descending and not gate_hold:
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
                    # The line above is measured against the tracker's OWN prediction, so it cannot show an error in
                    # that prediction -- and below ~1 m the marker is out of view, so the prediction is all the UAV
                    # has. A platform that turns during that blind stretch makes the two numbers disagree by metres.
                    # This one compares against the ground truth at the same instant (no post-landing sampling delay);
                    # it is only meaningful when the platform node runs on sim time (-p use_sim_time:=true).
                    truth = io.platform_truth() if cfg.use_ground_truth else None
                    if truth is not None:
                        ux, uy, _ = io.uav_position()
                        self.offset_at_contact = math.hypot(ux - truth[0], uy - truth[1])
                        self.log(f"  Ground truth at that instant: {self.offset_at_contact:.2f} m from the platform "
                                 "centre (half-width 0.75 m). Meaningful only with the platform node on sim time.")
                        # Who was right in the blind stretch? Each prediction's distance to the ground truth right now.
                        parts = [f"UAV {self.offset_at_contact:.2f}"]
                        tr = self.tracker.state(now)
                        if tr is not None:
                            parts.append(f"tracker extrapolation {math.hypot(tr.x - truth[0], tr.y - truth[1]):.2f}")
                        ms = self._mdn_state(now) if self.mdn is not None else None
                        if ms is not None:
                            parts.append(f"MDN prediction {math.hypot(ms.x - truth[0], ms.y - truth[1]):.2f}")
                        self.log("  Distance to the ground-truth platform centre at contact [m]: " + ", ".join(parts))
                        self.log(f"  The marker was last detected {now - last_seen:.1f} s before contact, at {last_seen_alt:.2f} m "
                                 "altitude: that is how long the UAV flew on a prediction.")
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
        summary["offset_at_contact"] = self.offset_at_contact
        summary["gate_held"] = self.gate_held
        return summary
