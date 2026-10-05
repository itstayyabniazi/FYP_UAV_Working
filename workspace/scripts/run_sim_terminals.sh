#!/usr/bin/env bash
#
# run_sim_terminals.sh — open one terminal window per simulation node.
#
# Assumes Gazebo / PX4 SITL / QGroundControl are already running (whatever
# you use for "Terminal 1-3"); this script covers the platform spawn +
# cmd_vel bridge, platform motion node, camera bridge, UAV state node,
# landing controller and vision node — the six terminals you listed.
#
# Re-running the script closes everything from the previous run (windows +
# the ROS nodes inside them) before opening fresh ones.
#
# Usage:
#   ./run_sim_terminals.sh          # stop any previous run, then start fresh
#   ./run_sim_terminals.sh stop     # just stop everything, don't restart

set -uo pipefail

ROS2_WS="${ROS2_WS:-/workspace/ros2_ws}"
ROS_DISTRO_SETUP="${ROS_DISTRO_SETUP:-/opt/ros/humble/setup.bash}"
TITLE_PREFIX="UAVSIM"
PIDFILE="/tmp/uav_sim_terminals.pid"

# label -> command run inside that terminal, in launch order
LABELS=(
  "1-Spawn-Landmarks"
  "2-Spawn-Platform"
  "3-Platform-Motion"
  "4-Camera-Bridge"
  "5-UAV-State"
  "6-Landing-Controller"
  "7-Vision-Node"
)

CMDS=(
  'ros2 run ros_gz_sim create -world default -file $(ros2 pkg prefix moving_platform)/share/moving_platform/models/landmark_post/model.sdf -name landmark_A -x 11.0 -y 50.0 -z 0.0 && ros2 run ros_gz_sim create -world default -file $(ros2 pkg prefix moving_platform)/share/moving_platform/models/landmark_post/model.sdf -name landmark_B -x 9.0 -y 0.0 -z 0.0 && ros2 run ros_gz_sim create -world default -file $(ros2 pkg prefix moving_platform)/share/moving_platform/models/landmark_post/model.sdf -name landmark_C -x 11.0 -y 9.0 -z 0.0 && ros2 run ros_gz_sim create -world default -file $(ros2 pkg prefix moving_platform)/share/moving_platform/models/landmark_post/model.sdf -name landmark_D -x 0.0 -y 9.0 -z 0.0'
  #'ros2 run ros_gz_sim create -world default -file $(ros2 pkg prefix moving_platform)/share/moving_platform/models/moving_platform/model.sdf -name moving_platform -x 11.0 -y 3.0 -z 0.025 && ros2 run ros_gz_bridge parameter_bridge /model/moving_platform/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'
  'ros2 run ros_gz_sim create -world default -file $(ros2 pkg prefix moving_platform)/share/moving_platform/models/moving_platform/model.sdf -name moving_platform -x 10.0 -y 0.0 -z 0.025 && ros2 run ros_gz_bridge parameter_bridge /model/moving_platform/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist'
  #'ros2 run moving_platform moving_platform_node --ros-args -p motion:=circular -p center_x:=9.5 -p center_y:=3.0 -p radius:=1.5 -p angular_speed:=0.3 -p wait_for_start:=true'
  'ros2 run moving_platform moving_platform_node --ros-args -p motion:=linear -p start_x:=10.0 -p start_y:=0.0 -p heading_deg:=90.0 -p speed:=1.39 -p travel_length:=50.0 -p wait_for_start:=true'
  'ros2 run ros_gz_bridge parameter_bridge /drone_camera@sensor_msgs/msg/Image@gz.msgs.Image /drone_camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo'
  'ros2 run px4_bridge uav_state_node'
  'ros2 run landing_controller landing_controller_node'
  'ros2 run vision_node aruco_landing_target_node'
)

# distinctive substrings used to pkill leftover ROS nodes from a previous run
KILL_PATTERNS=(
  "ros_gz_sim create -world default -file .*moving_platform"
  "ros_gz_bridge parameter_bridge /model/moving_platform/cmd_vel"
  "moving_platform_node --ros-args"
  "ros_gz_bridge parameter_bridge /drone_camera"
  "px4_bridge uav_state_node"
  "landing_controller_node"
  "aruco_landing_target_node"
)

find_terminal() {
  for t in gnome-terminal tilix konsole xfce4-terminal terminator xterm; do
    command -v "$t" >/dev/null 2>&1 && { echo "$t"; return; }
  done
}

open_terminal() {
  local term="$1" title="$2" cmd="$3"
  local inner="source ${ROS_DISTRO_SETUP}; source ${ROS2_WS}/install/setup.bash; clear; ${cmd}; echo; echo '--- process exited, press Enter to close ---'; read"
  case "$term" in
    gnome-terminal)
      gnome-terminal --title="${TITLE_PREFIX}:${title}" -- bash -c "$inner" &
      ;;
    tilix)
      tilix --title="${TITLE_PREFIX}:${title}" -e bash -c "$inner" &
      ;;
    konsole)
      konsole --new-tab -p tabtitle="${TITLE_PREFIX}:${title}" -e bash -c "$inner" &
      ;;
    xfce4-terminal)
      xfce4-terminal --title="${TITLE_PREFIX}:${title}" -x bash -c "$inner" &
      ;;
    terminator)
      terminator --title="${TITLE_PREFIX}:${title}" -e bash -c "$inner" &
      ;;
    xterm)
      xterm -T "${TITLE_PREFIX}:${title}" -e bash -c "$inner" &
      ;;
  esac
  echo $! >> "$PIDFILE"
}

stop_all() {
  echo "Stopping previous run..."

  # close previously tracked terminal windows (best effort — gnome-terminal
  # is client/server so this PID may already be gone; wmctrl below covers it)
  if [[ -f "$PIDFILE" ]]; then
    while read -r pid; do
      [[ -n "$pid" ]] && kill "$pid" 2>/dev/null
    done < "$PIDFILE"
    rm -f "$PIDFILE"
  fi

  if command -v wmctrl >/dev/null 2>&1; then
    wmctrl -l | awk -v p="$TITLE_PREFIX" '$0 ~ p {print $1}' | while read -r wid; do
      wmctrl -ic "$wid"
    done
  fi

  # kill the actual ROS nodes regardless of how the window was closed, so a
  # restart never fights leftover processes from the previous run
  for pattern in "${KILL_PATTERNS[@]}"; do
    pkill -f "$pattern" 2>/dev/null
  done

  sleep 1
}

start_all() {
  local term
  term="$(find_terminal)"
  if [[ -z "$term" ]]; then
    echo "No supported terminal emulator found (tried gnome-terminal, tilix, konsole, xfce4-terminal, terminator, xterm)." >&2
    exit 1
  fi
  echo "Using terminal: $term"

  : > "$PIDFILE"
  for i in "${!LABELS[@]}"; do
    echo "Opening terminal for: ${LABELS[$i]}"
    open_terminal "$term" "${LABELS[$i]}" "${CMDS[$i]}"
    sleep 2
  done
}

case "${1:-}" in
  stop)
    stop_all
    ;;
  *)
    stop_all
    start_all
    ;;
esac
