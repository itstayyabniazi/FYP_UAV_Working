"""
vision_landing.py

Phase 2 mission: take off, SEARCH for the platform's ArUco marker with the
downward camera, centre over it, descend, and land -- without being told where
the platform is.

    SEARCH  fly an expanding-square spiral at the search altitude until the
            marker is detected (confirmed over several frames, not one).
    TRACK   servo x/y onto the marker's estimated position; descend only while
            aligned (hysteresis), hold altitude otherwise. Below
            servo_min_altitude the marker leaves the camera's field of view, so
            it keeps descending on the last estimate.
    LOST    marker gone for lost_timeout while still high: climb over the last
            known position to widen the view; re-acquire -> TRACK, else SEARCH.
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
    search_speed: float = 1.5        # [m/s] setpoint speed along the search pattern
    climb_speed: float = 1.0         # [m/s]
    spiral_step: float = 5.0         # [m] leg increment; camera footprint at 5 m is ~8.4 x 6.3 m
    spiral_max_leg: float = 30.0     # [m] give up once the spiral would exceed this leg length
    approach_speed: float = 1.5      # [m/s] setpoint speed while centring on the marker
    descent_rate: float = 0.35       # [m/s]
    align_tol: float = 0.25          # [m] start/continue descending below this offset
    realign_tol: float = 0.5         # [m] stop descending above this offset (hysteresis)
    servo_min_altitude: float = 1.0  # [m] below this the marker leaves the FOV; go blind on last estimate
    handoff_altitude: float = 0.5    # [m] hand over to PX4 AUTO.LAND
    confirm_count: int = 3           # detections needed ...
    confirm_window: float = 1.0      # ... within this many seconds to accept the marker
    lost_timeout: float = 5.0        # [s] no detections while above servo_min_altitude -> LOST
    recover_wait: float = 8.0        # [s] wait at search altitude before falling back to SEARCH
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
    def _spiral(x0, y0, step, max_leg):
        """Expanding square, x = north, y = east: N1 E1 S2 W2 N3 E3 ... (legs
        in units of `step`). Yields corner waypoints."""
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        x, y, leg, i = x0, y0, 1, 0
        while leg * step <= max_leg:
            for _ in range(2):
                dx, dy = directions[i % 4]
                x += dx * leg * step
                y += dy * leg * step
                yield x, y
                i += 1
            leg += 1

    def _search(self):
        cfg = self.cfg
        x0, y0, _ = self.io.uav_position()
        self.log(f"SEARCH: spiral from ({x0:.1f}, {y0:.1f}) at {cfg.search_altitude} m, "
                 f"step {cfg.spiral_step} m, max leg {cfg.spiral_max_leg} m")
        # Get to search altitude first (may be called from a lower altitude).
        waypoints = [(x0, y0)] + list(self._spiral(x0, y0, cfg.spiral_step, cfg.spiral_max_leg))
        for wx, wy in waypoints:
            while not self._step(wx, wy, cfg.search_altitude, cfg.search_speed, cfg.climb_speed):
                self._check_timeout()
                if self.io.confirmed(cfg.confirm_count, cfg.confirm_window):
                    return self._acquired()
            if self.io.confirmed(cfg.confirm_count, cfg.confirm_window):
                return self._acquired()
        return "NOT_FOUND"

    def _acquired(self):
        est = self.io.estimate()
        if est is None:  # detections aged out between the check and here
            return "SEARCH"
        self.target = est
        self.log(f"Marker acquired: estimated at ({est[0]:.2f}, {est[1]:.2f}).")
        expected = self.cfg.expected_xy
        if expected is not None and math.hypot(est[0] - expected[0], est[1] - expected[1]) > 1.0:
            self.log(f"WARNING: expected the platform near ({expected[0]:.2f}, {expected[1]:.2f}) "
                     "(sim ground truth). Either the platform is elsewhere, or the camera frame "
                     "convention is off -- run mission.vision_frame_check.")
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
                    return "SEARCH"

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
                state = "SEARCH"
                while state not in ("FINAL", "NOT_FOUND"):
                    state = {"SEARCH": self._search, "TRACK": self._track,
                             "LOST": self._recover}[state]()
                outcome = "LANDED" if state == "FINAL" else "NOT_FOUND"
                if state == "NOT_FOUND":
                    self.log("Search pattern finished without finding the marker -- landing here.")
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
