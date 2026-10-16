"""
Platform tracker: a separate terminal that shows where the moving platform is NOW and keeps a history of where it has been.

It only LISTENS to /platform/state (published by moving_platform_node), so it can be started, stopped or restarted at any
time without touching the simulation. Run it in its own terminal:

    ros2 run moving_platform platform_tracker                    # live dashboard (redraws in place)
    ros2 run moving_platform platform_tracker --ros-args -p use_sim_time:=true -p csv_path:=/workspace/platform_track.csv
    ros2 run moving_platform platform_tracker --ros-args -p plain:=true     # no screen redraw: one scrolling line per sample

Parameters: history_period [s, 1.0] spacing of the history rows, history_rows [int, 14] rows shown, csv_path [str, ''] write
a CSV (every csv_period seconds, default 0.1) for later analysis, plain [bool, false], map_width/map_height [56/22].

The dashboard shows the position in BOTH frames used in this project: Gazebo ENU (east, north: what the platform node and
trajectories.py use) and the mission's PX4 NED (north, east: what the mission logs print). Bearing is a compass bearing
(0 = north, 90 = east). A top-down map of the whole path so far is drawn below the table (S = start, @ = now).

Preview without ROS or Gazebo (replays a random path faster than real time):
    python3 -m moving_platform.platform_tracker --demo --seconds 60 --seed 5 --speed 1.0 [--plain]
"""
import math
import sys
import time
from collections import deque

CLEAR = "\x1b[H\x1b[J"
EOL = "\x1b[K"


def bearing_deg(vx, vy):
    """Compass bearing of the velocity (0 = north, 90 = east); vx east, vy north."""
    return math.degrees(math.atan2(vx, vy)) % 360.0


def _wrap(a):
    return (a + 180.0) % 360.0 - 180.0


class TrailLog:
    """Keeps the platform's track and renders it. No ROS in here, so it can be tested and previewed on its own."""

    def __init__(self, history_period=1.0, rows=14, map_width=56, map_height=22, csv_path="", csv_period=0.1):
        self.history_period, self.rows = history_period, rows
        self.map_w, self.map_h = map_width, map_height
        self.history = []                 # (t_since_start, x_east, y_north, speed, bearing)
        self.trail = []                   # (x_east, y_north) every ~0.1 s: a finer path for the map
        self.t0 = None                    # time of the first sample
        self.moved_at = None              # time the platform first moved
        self.last = None                  # newest sample (t, x, y, vx, vy)
        self.distance = 0.0
        self._prev_xy = None
        self._next_hist = 0.0
        self._next_trail = 0.0
        self._next_csv = 0.0
        self.csv_period = csv_period
        self._csv = open(csv_path, "w", buffering=1) if csv_path else None
        if self._csv:
            self._csv.write("t,x_east,y_north,ned_north,ned_east,vx_east,vy_north,speed,bearing_deg\n")
        self.bounds = None                # (xmin, xmax, ymin, ymax) of everything seen

    def add(self, t, x, y, vx, vy):
        if self.t0 is None:
            self.t0 = t
        if self.moved_at is None and math.hypot(vx, vy) > 0.02:
            self.moved_at = t
            self.distance, self._prev_xy = 0.0, None
        rel = t - self.t0
        if self._prev_xy is not None and self.moved_at is not None:
            self.distance += math.hypot(x - self._prev_xy[0], y - self._prev_xy[1])
        self._prev_xy = (x, y)
        self.last = (t, x, y, vx, vy)
        b = self.bounds
        self.bounds = (x, x, y, y) if b is None else (min(b[0], x), max(b[1], x), min(b[2], y), max(b[3], y))
        speed = math.hypot(vx, vy)
        if rel >= self._next_trail:
            self._next_trail = rel + 0.1
            self.trail.append((x, y))
            if len(self.trail) > 30000:
                del self.trail[:5000]
        if rel >= self._next_hist:
            while self._next_hist <= rel:                 # fixed grid: rows at 0, 1, 2 ... s, no drift
                self._next_hist += self.history_period
            self.history.append((rel, x, y, speed, bearing_deg(vx, vy) if speed > 0.02 else float("nan")))
        if self._csv and rel >= self._next_csv:
            self._next_csv = rel + self.csv_period
            self._csv.write(f"{rel:.3f},{x:.3f},{y:.3f},{y:.3f},{x:.3f},{vx:.3f},{vy:.3f},{speed:.3f},"
                            f"{bearing_deg(vx, vy) if speed > 0.02 else float('nan'):.1f}\n")

    def turn_rate(self):
        """Turn rate [deg/s] from the bearings of the last history rows ~1 s apart; positive = turning right (clockwise)."""
        h = [r for r in self.history[-4:] if r[4] == r[4]]
        if len(h) < 2 or h[-1][0] - h[0][0] < 0.5:
            return 0.0
        return _wrap(h[-1][4] - h[0][4]) / (h[-1][0] - h[0][0])

    def motion_label(self):
        if self.last is None or math.hypot(self.last[3], self.last[4]) <= 0.02:
            return "HOLDING STILL (waiting for /moving_platform/start)" if self.moved_at is None else "stopped"
        w = self.turn_rate()
        if abs(w) < 4.0:
            return "going straight"
        return f"turning {'right' if w > 0 else 'left'} ({abs(w):.0f} deg/s, radius {math.hypot(self.last[3], self.last[4]) / math.radians(abs(w)):.1f} m)"

    def render_map(self):
        if not self.trail or self.bounds is None:
            return ["(no samples yet)"]
        xmin, xmax, ymin, ymax = self.bounds
        pad = 0.05 * max(xmax - xmin, ymax - ymin, 1.0)
        xmin, xmax, ymin, ymax = xmin - pad, xmax + pad, ymin - pad, ymax + pad
        # A character cell is about twice as tall as wide, so one row spans twice the metres of one column: that keeps
        # circles round on screen.
        sx = max((xmax - xmin) / (self.map_w - 1), (ymax - ymin) / (2 * (self.map_h - 1)), 0.02)
        grid = [[" "] * self.map_w for _ in range(self.map_h)]

        def cell(x, y):
            return (min(self.map_h - 1, max(0, int((ymax - y) / (2 * sx)))),
                    min(self.map_w - 1, max(0, int((x - xmin) / sx))))
        for x, y in self.trail:
            r, c = cell(x, y)
            grid[r][c] = "."
        r, c = cell(self.trail[0][0], self.trail[0][1])
        grid[r][c] = "S"
        if self.last:
            r, c = cell(self.last[1], self.last[2])
            grid[r][c] = "@"
        top = f"  north {ymax:.1f} m"
        bottom = f"  south {ymin:.1f} m   (west {xmin:.1f} m ... east {xmax:.1f} m; one column = {sx:.2f} m)"
        return [top] + ["  |" + "".join(row) + "|" for row in grid] + [bottom]

    def render(self):
        if self.last is None:
            return "Waiting for /platform/state ... (is moving_platform_node running?)"
        t, x, y, vx, vy = self.last
        speed = math.hypot(vx, vy)
        since = (t - self.moved_at) if self.moved_at is not None else 0.0
        out = [
            "PLATFORM TRACKER",
            f"  now        Gazebo ENU  east {x:8.2f} m   north {y:8.2f} m      mission NED  north {y:8.2f} m   east {x:8.2f} m",
            f"  motion     speed {speed:5.2f} m/s   bearing {bearing_deg(vx, vy) if speed > 0.02 else float('nan'):5.0f} deg   {self.motion_label()}",
            f"  journey    moving for {since:6.1f} s   distance travelled {self.distance:7.1f} m   "
            f"mean speed {(self.distance / since) if since > 1 else 0.0:4.2f} m/s",
            f"  extent     east {self.bounds[0]:.1f} .. {self.bounds[1]:.1f} m   north {self.bounds[2]:.1f} .. {self.bounds[3]:.1f} m   "
            f"({len(self.history)} history rows, one every {self.history_period:g} s)",
            "",
            "  HISTORY (newest last)      t [s]    east [m]   north [m]   speed [m/s]   bearing",
        ]
        for rel, hx, hy, sp, br in self.history[-self.rows:]:
            out.append(f"                            {rel:7.1f}   {hx:9.2f}   {hy:9.2f}   {sp:10.2f}   "
                       f"{('%6.0f' % br) if br == br else '     -'}")
        out.append("")
        out += self.render_map()
        return "\n".join(out)


def _demo(argv):
    import argparse
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from moving_platform.trajectories import random_state
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--seconds", type=float, default=60.0)
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--turn", type=float, default=1.0)
    ap.add_argument("--plain", action="store_true")
    ap.add_argument("--csv", default="")
    a = ap.parse_args(argv)
    log = TrailLog(csv_path=a.csv)
    t = 0.0
    while t <= a.seconds:
        x, y, vx, vy = random_state(t, 9.0, 6.0, 3.0, 7.0, a.speed, a.seed, a.turn, 3.0, 8.0)
        log.add(t, x, y, vx, vy)
        if a.plain:
            if abs(t - round(t)) < 1e-9:
                print(f"t {t:6.1f} s  east {x:7.2f}  north {y:7.2f}  speed {math.hypot(vx, vy):4.2f}  "
                      f"bearing {bearing_deg(vx, vy):5.0f}  {log.motion_label()}")
        elif abs(t * 2 - round(t * 2)) < 1e-9:
            sys.stdout.write(CLEAR + log.render().replace("\n", EOL + "\n") + EOL + "\n")
            sys.stdout.flush()
            time.sleep(0.05)
        t += 0.05
    if not a.plain:
        print()


def main(args=None):
    argv = sys.argv[1:]
    if "--demo" in argv:
        return _demo(argv)
    import rclpy
    from rclpy.node import Node
    from interfaces.msg import PlatformState

    class PlatformTracker(Node):
        def __init__(self):
            super().__init__("platform_tracker")
            self.declare_parameter("history_period", 1.0)
            self.declare_parameter("history_rows", 14)
            self.declare_parameter("csv_path", "")
            self.declare_parameter("csv_period", 0.1)
            self.declare_parameter("plain", False)
            self.declare_parameter("map_width", 56)
            self.declare_parameter("map_height", 22)
            g = lambda n: self.get_parameter(n).value
            self.plain = bool(g("plain"))
            self.log = TrailLog(float(g("history_period")), int(g("history_rows")), int(g("map_width")),
                                int(g("map_height")), str(g("csv_path")), float(g("csv_period")))
            self._printed = 0
            self.create_subscription(PlatformState, "/platform/state", self._on_state, 10)

        def _now(self):
            return self.get_clock().now().nanoseconds * 1e-9

        def _on_state(self, m):
            self.log.add(self._now(), m.x, m.y, m.vx, m.vy)

        def draw(self):
            if self.plain:
                while self._printed < len(self.log.history):
                    rel, x, y, sp, br = self.log.history[self._printed]
                    print(f"t {rel:7.1f} s  east {x:7.2f}  north {y:7.2f}  speed {sp:4.2f}  "
                          f"bearing {('%5.0f' % br) if br == br else '    -'}  {self.log.motion_label()}", flush=True)
                    self._printed += 1
                return
            sys.stdout.write(CLEAR + self.log.render().replace("\n", EOL + "\n") + EOL + "\n")
            sys.stdout.flush()

    import os
    import signal
    rclpy.init(args=args)
    node = PlatformTracker()
    stop = {"asked": False}

    def _stop(signum, frame):
        # First Ctrl+C (or SIGTERM): leave the loop cleanly. A second one exits at once, whatever state we are in.
        if stop["asked"]:
            os._exit(130)
        stop["asked"] = True

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    next_draw = 0.0
    try:
        # A short spin_once loop (not rclpy.spin) so Ctrl+C is noticed within 0.2 s, and the screen is redrawn on the WALL
        # clock whatever the sim clock is doing.
        while rclpy.ok() and not stop["asked"]:
            rclpy.spin_once(node, timeout_sec=0.2)
            if time.monotonic() >= next_draw:
                next_draw = time.monotonic() + 0.5
                node.draw()
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\nplatform_tracker stopped.\n")
        try:
            node.destroy_node()
            if rclpy.ok():
                rclpy.shutdown()
        except Exception:
            pass


if __name__ == "__main__":
    main()
