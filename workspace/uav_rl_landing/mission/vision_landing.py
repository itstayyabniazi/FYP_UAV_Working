"""
vision_landing.py

Phase 2 mission: take off, SEARCH for the platform's ArUco marker with the
downward camera, centre over it, descend, and land -- without being told where
the platform is.

    PATROL  fly the corners of a square (A -> B -> C -> D) at the search
            altitude, hovering briefly at each. The moment the marker is
            confirmed (several frames, not one) -- mid-leg or at a corner --
            the patrol stops and the drone goes for it.
    TRACK   servo x/y onto the marker's estimated position; descend only while
            aligned (hysteresis), hold altitude otherwise. Below
            servo_min_altitude the marker leaves the camera's field of view, so
            it keeps descending on the last estimate.
    LOST    marker gone for lost_timeout while still high: climb over the last
            known position to widen the view; re-acquire -> TRACK, else PATROL.
    LAND    hand the last stretch to PX4's AUTO.LAND (lands at the current x/y).

The marker position it aims at is ABSOLUTE (UAV position at detection time +
the camera's relative measurement), which is what makes averaging several
detections safe: for a static platform the estimate has no lag.

This module is pure logic. All I/O goes through an `io` object (ros_io.py in the
sim, a fake in tests) providing:
    now(), sleep(dt)                    time (wall clock; sleep spins callbacks)
    uav_position() -> (x, y, altitude)  PX4 local NED x/y, altitude AGL (up)
    start(x, y, altitude)               enter position mode, first setpoint
    command(x, y, altitude)             new position setpoint
    confirmed(count, window) -> bool    >= count detections in the last window s
    estimate() -> (x, y) | None         mean marker position over fresh detections
    land()                              hand over to PX4 AUTO.LAND
    wait_landed(timeout) -> (x, y, altitude)
"""
import math
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class VisionLandingConfig:
    search_altitude: float = 5.0     # [m] marker is ~38 px wide here (0.5 m marker, 640 px, 80 deg FOV)
    # Corners of the patrol square, PX4 local NED (x = north, y = east) [m], flown
    # in order. The camera's USABLE footprint at 5 m is only ~5 m east-west (the
    # UAV's own rotor arms/props block the outer ~130 px on each side of the
    # 640 px image) x ~6.3 m north-south, so a leg only "sees" the marker if it
    # passes within ~2 m east-west / ~3 m north-south of it. Edit these to cover
    # your search area. The default 9 m square is placed so its B->C leg passes
    # the sim platform at (north 3, east 10).
    patrol_corners: Tuple[Tuple[float, float], ...] = (
        (0.0, 0.0), (0.0, 9.0), (9.0, 9.0), (9.0, 0.0))
    corner_tolerance: float = 0.5    # [m] how close counts as "at the corner"
    corner_timeout: float = 30.0     # [s] give up waiting to reach a corner
    dwell_time: float = 2.0          # [s] hover at each corner, looking
    progress_period: float = 5.0     # [s] between progress log lines
    search_speed: float = 1.5        # [m/s] setpoint speed along the patrol
    climb_speed: float = 1.0         # [m/s]
    approach_speed: float = 1.5      # [m/s] setpoint speed while centring on the marker
    descent_rate: float = 0.35       # [m/s]
    align_tol: float = 0.25          # [m] start/continue descending below this offset
    realign_tol: float = 0.5         # [m] stop descending above this offset (hysteresis)
    servo_min_altitude: float = 1.0  # [m] below this the marker leaves the FOV; go blind on last estimate
    handoff_altitude: float = 0.5    # [m] hand over to PX4 AUTO.LAND
    confirm_count: int = 3           # detections needed ...
    confirm_window: float = 1.0      # ... within this many seconds to accept the marker
    lost_timeout: float = 5.0        # [s] no detections while above servo_min_altitude -> LOST
    recover_wait: float = 8.0        # [s] wait at search altitude before restarting the PATROL
    takeoff_timeout: float = 40.0    # [s]
    mission_timeout: float = 300.0   # [s]
    dt: float = 0.1                  # [s] control period
    # Only for logging a comparison at the end / a sanity warning on first
    # sight (sim ground truth). NEVER used to steer.
    expected_xy: Optional[Tuple[float, float]] = None


class MissionTimeout(Exception):
    pass


class VisionLander:

    def __init__(self, io, config: VisionLandingConfig = None, log=print):
        self.io = io
        self.cfg = config or VisionLandingConfig()
        self.log = log
        self.sp = [0.0, 0.0, 0.0]        # current position setpoint: x, y, altitude
        self.target = None               # last marker estimate (x, y)
        self._t0 = None

    # ---------------------------------------------------------
    # Setpoint motion
    # ---------------------------------------------------------

    def _check_timeout(self):
        if self.io.now() - self._t0 > self.cfg.mission_timeout:
            raise MissionTimeout()

    def _step(self, tx, ty, talt, hspeed, vspeed):
        """Slide the setpoint toward the target by one control period (a plain
        jump would make PX4 fly at full speed and tilt the camera off the
        marker). Returns True once the setpoint has reached the target."""
        dt = self.cfg.dt
        dx, dy = tx - self.sp[0], ty - self.sp[1]
        dist = math.hypot(dx, dy)
        step = hspeed * dt
        if dist <= step:
            self.sp[0], self.sp[1] = tx, ty
            arrived_xy = True
        else:
            self.sp[0] += dx / dist * step
            self.sp[1] += dy / dist * step
            arrived_xy = False
        dz = talt - self.sp[2]
        vstep = vspeed * dt
        self.sp[2] += max(-vstep, min(vstep, dz))
        arrived_z = abs(talt - self.sp[2]) < 1e-9
        self.io.command(*self.sp)
        self.io.sleep(dt)
        return arrived_xy and arrived_z

    def goto(self, tx, ty, talt, hspeed=None, vspeed=None, tol=0.3, timeout=60.0):
        """Fly to a point and wait until the UAV (not just the setpoint) is
        there. Returns False on timeout."""
        hspeed = hspeed or self.cfg.search_speed
        vspeed = vspeed or self.cfg.climb_speed
        start = self.io.now()
        while True:
            self._check_timeout()
            arrived = self._step(tx, ty, talt, hspeed, vspeed)
            x, y, alt = self.io.uav_position()
            if arrived and math.hypot(x - tx, y - ty) <= tol and abs(alt - talt) <= tol:
                return True
            if self.io.now() - start > timeout:
                return False

    # ---------------------------------------------------------
    # States
    # ---------------------------------------------------------

    @staticmethod
    def _label(index):
        return chr(ord("A") + index) if index < 26 else str(index + 1)

    def _seen(self):
        return self.io.confirmed(self.cfg.confirm_count, self.cfg.confirm_window)

    def _patrol(self):
        """Fly the corners in order, hovering `dwell_time` at each; return
        "TRACK" the instant the marker is confirmed, "NOT_FOUND" if the last
        corner is done without it."""
        cfg = self.cfg
        corners = cfg.patrol_corners
        route = "  ".join(f"{self._label(i)}=({x:.1f}, {y:.1f})" for i, (x, y) in enumerate(corners))
        self.log(f"PATROL at {cfg.search_altitude} m: {route}")
        for index, (cx, cy) in enumerate(corners):
            name = self._label(index)
            self.log(f"--- Point {name}: flying to NED ({cx:.1f}, {cy:.1f}) at {cfg.search_altitude} m")
            if self._fly_to_corner(cx, cy, name):
                return self._acquired()
            x, y, alt = self.io.uav_position()
            self.log(f"  at point {name} ({x:.1f}, {y:.1f}, {alt:.1f} m); hovering "
                     f"{cfg.dwell_time:.0f} s, looking for the marker")
            end = self.io.now() + cfg.dwell_time
            while self.io.now() < end:
                self._check_timeout()
                self._step(cx, cy, cfg.search_altitude, cfg.search_speed, cfg.climb_speed)
                if self._seen():
                    return self._acquired()
        return "NOT_FOUND"

    def _fly_to_corner(self, cx, cy, name):
        """Fly to a corner, checking for the marker on every control tick, and
        logging progress so a slow leg doesn't look like a hung mission.
        Returns True if the marker was confirmed on the way."""
        cfg = self.cfg
        start = last_log = self.io.now()
        while True:
            self._check_timeout()
            arrived = self._step(cx, cy, cfg.search_altitude, cfg.search_speed, cfg.climb_speed)
            if self._seen():
                return True
            x, y, alt = self.io.uav_position()
            now = self.io.now()
            if arrived and math.hypot(x - cx, y - cy) <= cfg.corner_tolerance:
                return False
            if now - start > cfg.corner_timeout:
                self.log(f"  gave up waiting to reach point {name} after {cfg.corner_timeout:.0f} s")
                return False
            if now - last_log >= cfg.progress_period:
                last_log = now
                self.log(f"  ... UAV at ({x:.1f}, {y:.1f}, {alt:.1f} m), "
                         f"{math.hypot(x - cx, y - cy):.1f} m to point {name}, no marker yet")

    @staticmethod
    def _axis_hint(expected_rel, measured_rel, tol=0.75):
        """Swapped / sign-flipped north-east axes, judged from the expected vs
        measured marker offset (north, east) relative to the UAV."""
        ex, ey = expected_rel
        mx, my = measured_rel
        hints = []
        if abs(ex - ey) > 2 * tol and abs(mx - ey) <= tol and abs(my - ex) <= tol:
            hints.append("north/east look SWAPPED")
        if abs(ex) > 2 * tol and abs(mx + ex) <= tol:
            hints.append("north (X) sign looks FLIPPED")
        if abs(ey) > 2 * tol and abs(my + ey) <= tol:
            hints.append("east (Y) sign looks FLIPPED")
        return ", ".join(hints)

    def _acquired(self):
        est = self.io.estimate()
        if est is None:  # detections aged out between the check and here
            return "PATROL"
        self.target = est
        x, y, alt = self.io.uav_position()
        self.log(f"MARKER DETECTED at UAV NED ({x:.1f}, {y:.1f}, {alt:.1f} m) -- patrol stopped, "
                 "landing on it.")
        measure = getattr(self.io, "relative_measurement", None)
        rel = measure(0.4) if measure else None  # short window: the UAV is moving
        if rel is not None:
            self.log(f"  measured rel (N, E, D) = ({rel[0]:+.2f}, {rel[1]:+.2f}, {rel[2]:.2f}) "
                     f"[{rel[3]} detections]; marker estimated at NED ({est[0]:.2f}, {est[1]:.2f})")
        else:
            self.log(f"  marker estimated at NED ({est[0]:.2f}, {est[1]:.2f})")
        expected = self.cfg.expected_xy
        if expected is not None:
            error = math.hypot(est[0] - expected[0], est[1] - expected[1])
            if error <= 1.0:
                self.log(f"  sim ground truth ({expected[0]:.2f}, {expected[1]:.2f}): "
                         f"estimate {error:.2f} m off -- OK (camera axes/signs check out)")
            else:
                hint = ""
                if rel is not None:
                    hint = self._axis_hint((expected[0] - x, expected[1] - y), rel[:2])
                self.log(f"  MISMATCH: sim ground truth says the platform is at ({expected[0]:.2f}, "
                         f"{expected[1]:.2f}), {error:.1f} m from the camera's estimate. Either the "
                         "platform is elsewhere (update platform_world_x/y in parameters.py, or run with "
                         "--no-ground-truth), or the camera axes/signs are wrong (CAMERA_TO_BODY"
                         + (f": {hint}" if hint else "") + "). Not following the estimate -- landing here.")
                return "MISMATCH"
        return "TRACK"

    def _track(self):
        cfg = self.cfg
        last_seen = self.io.now()
        descending = False
        while True:
            self._check_timeout()
            now = self.io.now()
            x, y, alt = self.io.uav_position()
            est = self.io.estimate()
            if est is not None:
                self.target = est
                last_seen = now
            fresh = est is not None
            blind = alt <= cfg.servo_min_altitude
            if not fresh and not blind and now - last_seen > cfg.lost_timeout:
                self.log(f"Marker lost for {cfg.lost_timeout:.0f} s at {alt:.1f} m.")
                return "LOST"

            tx, ty = self.target
            err = math.hypot(x - tx, y - ty)
            if err <= cfg.align_tol:
                descending = True
            elif err >= cfg.realign_tol:
                descending = False
            if not fresh and not blind:
                descending = False  # never sink blind above the servo floor

            talt = cfg.handoff_altitude if descending else self.sp[2]
            self._step(tx, ty, talt, cfg.approach_speed, cfg.descent_rate)

            if descending and alt <= cfg.handoff_altitude + 0.15 and err <= 0.3:
                self.log(f"Reached {alt:.2f} m, {err:.2f} m from the marker estimate.")
                return "FINAL"

    def _recover(self):
        cfg = self.cfg
        tx, ty = self.target
        self.log("RECOVER: climbing over the last known marker position.")
        deadline = None
        while True:
            self._check_timeout()
            arrived = self._step(tx, ty, cfg.search_altitude, cfg.approach_speed, cfg.climb_speed)
            if self.io.confirmed(cfg.confirm_count, cfg.confirm_window):
                return self._acquired()
            if arrived:
                deadline = deadline or self.io.now() + cfg.recover_wait
                if self.io.now() > deadline:
                    return "PATROL"

    # ---------------------------------------------------------
    # Mission
    # ---------------------------------------------------------

    def run(self):
        cfg = self.cfg
        self._t0 = self.io.now()
        x0, y0, _ = self.io.uav_position()
        outcome = "ERROR"
        try:
            self.log(f"TAKEOFF to {cfg.search_altitude} m.")
            self.io.start(x0, y0, cfg.search_altitude)
            self.sp = [x0, y0, cfg.search_altitude]
            start = self.io.now()
            while abs(self.io.uav_position()[2] - cfg.search_altitude) > 0.3:
                self.io.sleep(cfg.dt)
                self._check_timeout()
                if self.io.now() - start > cfg.takeoff_timeout:
                    self.log("Never reached the search altitude -- landing.")
                    outcome = "TAKEOFF_FAILED"
                    break
            else:
                state = "PATROL"
                while state not in ("FINAL", "NOT_FOUND", "MISMATCH"):
                    state = {"PATROL": self._patrol, "TRACK": self._track,
                             "LOST": self._recover}[state]()
                outcome = {"FINAL": "LANDED", "NOT_FOUND": "NOT_FOUND",
                           "MISMATCH": "ESTIMATE_MISMATCH"}[state]
                if state == "NOT_FOUND":
                    self.log("Patrol finished without seeing the marker -- landing here.")
        except MissionTimeout:
            outcome = "TIMEOUT"
            self.log(f"Mission timeout ({cfg.mission_timeout:.0f} s) -- landing here.")

        self.log("LAND: handing over to PX4 AUTO.LAND.")
        self.io.land()
        fx, fy, falt = self.io.wait_landed(timeout=30.0)
        summary = {"outcome": outcome, "final_xy": (fx, fy), "final_altitude": falt,
                   "marker_estimate": self.target}
        if self.target is not None:
            summary["error_to_estimate"] = math.hypot(fx - self.target[0], fy - self.target[1])
        if cfg.expected_xy is not None:
            summary["error_to_ground_truth"] = math.hypot(fx - cfg.expected_xy[0], fy - cfg.expected_xy[1])
        return summary
