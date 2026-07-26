#!/usr/bin/env python3
"""
Detects the ArUco marker on the moving platform (see
../../moving_platform/models/moving_platform/model.sdf's "aruco_marker"
visual + scripts/generate_aruco_marker.py) from the UAV's downward-facing
camera, and publishes its pose relative to the UAV as interfaces/msg/
LandingTarget -- the vision-based counterpart to the ground-truth
/platform/state used during training.

This is the "deployment/demo" perception path, not the training path:
training still runs against ground truth (relative_state package) exactly as
before, since that's what the RL pipeline has actually been validated
against. This node exists so the same downstream (vision_relative_state_node
-> RLObservation -> landing_controller) can be driven from a real/simulated
camera instead, for demonstrating the open-world "land on a moving car"
scenario the paper never attempted (it used Vicon in a controlled room).

Frame convention (read this before trusting any sign here):
  - OpenCV/ROS "optical frame" convention for the undistorted camera image:
    X right, Y down, Z forward (into the scene) -- this is what solvePnP's
    tvec is expressed in.
  - The camera is mounted rigidly on the UAV body, pointing straight down
    (see patch_x500_camera.py / scripts/patch_x500_camera.py's pose pitch of
    +90deg), with the image's "up" edge (informally: -Y in optical
    convention) facing the UAV's nose (+X, body FRD). CAMERA_TO_BODY below
    encodes exactly that one fixed assumption as a 3x3 rotation matrix --
    if your physical/SDF mount ends up rotated differently (e.g. the camera
    is clocked 90/180 degrees), this is the one constant to fix.
  - The UAV's current roll/pitch/yaw (from /uav/state, same source
    relative_state_node's ground-truth path uses) rotates the resulting
    body-frame vector into the world/PX4-local-NED-consistent frame that the
    rest of the pipeline (rel_x = platform.x - uav.x, etc.) already assumes.

VERIFY THIS IN SIM BEFORE TRUSTING IT: hover directly above the marker at a
known height with ~zero roll/pitch/yaw and confirm rel_x/rel_y print near 0
and rel_z prints near the known height; then translate/rotate and sanity
check the signs match your expectation. If X/Y come out swapped or
sign-flipped, that's CAMERA_TO_BODY (or the marker's assumed mounting
orientation) needing a one-line fix, not a bug in the attitude-rotation
logic.
"""
import math

import numpy as np
import cv2

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image, CameraInfo
from interfaces.msg import LandingTarget, UAVState

from rclpy.qos import QoSProfile
from rclpy.qos import ReliabilityPolicy
from rclpy.qos import HistoryPolicy
from rclpy.qos import DurabilityPolicy


ARUCO_DICT = cv2.aruco.DICT_4X4_50
MARKER_ID = 0
MARKER_SIZE_M = 0.5  # must match model.sdf's aruco_marker visual box size

# See the module docstring: encodes the fixed camera-mount-to-body rotation.
# Columns are the camera's own X/Y/Z axes (optical convention), expressed in
# UAV body (FRD) coordinates.
CAMERA_TO_BODY = np.array([
    [0.0, -1.0, 0.0],
    [1.0,  0.0, 0.0],
    [0.0,  0.0, 1.0],
])

# How long a marker can go undetected before LandingTarget.detected is
# reported False (rather than silently repeating the last known pose, which
# would make a lost target look like a stationary one to the consumer).
DETECTION_TIMEOUT_SEC = 0.5


def euler_to_rotation_matrix(roll, pitch, yaw):
    """World-from-body rotation matrix for the 3-2-1 (yaw, pitch, roll)
    Euler convention used elsewhere in this repo (see px4_bridge's
    quaternion_to_euler) -- R = Rz(yaw) @ Ry(pitch) @ Rx(roll)."""

    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)

    rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
    rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])

    return rz @ ry @ rx


class ArucoLandingTargetNode(Node):

    def __init__(self):
        super().__init__("aruco_landing_target_node")

        if hasattr(cv2.aruco, "ArucoDetector"):
            dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
            self._detector = cv2.aruco.ArucoDetector(dictionary, cv2.aruco.DetectorParameters())
            self._detect = lambda gray: self._detector.detectMarkers(gray)
        else:
            # OpenCV < 4.7 fallback API.
            dictionary = cv2.aruco.Dictionary_get(ARUCO_DICT)
            parameters = cv2.aruco.DetectorParameters_create()
            self._detect = lambda gray: cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)

        half = MARKER_SIZE_M / 2.0
        self._object_points = np.array([
            [-half,  half, 0],
            [ half,  half, 0],
            [ half, -half, 0],
            [-half, -half, 0],
        ], dtype=np.float32)

        self._camera_matrix = None
        self._dist_coeffs = None

        self._uav_attitude = None  # (roll, pitch, yaw), latest from /uav/state

        self._last_valid_t = None
        self._last_valid_rel = None  # (rel_x, rel_y, rel_z)

        px4_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        self.create_subscription(Image, "/drone_camera", self._on_image, px4_qos)
        self.create_subscription(CameraInfo, "/drone_camera/camera_info", self._on_camera_info, px4_qos)
        self.create_subscription(UAVState, "/uav/state", self._on_uav_state, 10)

        self.publisher = self.create_publisher(LandingTarget, "/landing_target", 10)

        self.get_logger().info("ArUco Landing Target Node Started")

    def _on_uav_state(self, msg):
        self._uav_attitude = (msg.roll, msg.pitch, msg.yaw)

    def _on_camera_info(self, msg):
        self._camera_matrix = np.array(msg.k, dtype=np.float64).reshape(3, 3)
        self._dist_coeffs = np.array(msg.d, dtype=np.float64)

    def _decode_image(self, msg):
        """Manual sensor_msgs/Image -> BGR numpy array, avoiding a cv_bridge
        dependency for the two encodings Gazebo's camera sensor actually
        bridges to (rgb8/bgr8)."""

        arr = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, -1)

        if msg.encoding == "rgb8":
            return cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
        elif msg.encoding == "bgr8":
            return arr
        elif msg.encoding == "mono8":
            return cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)
        else:
            raise ValueError(f"Unsupported image encoding: {msg.encoding!r}")

    def _on_image(self, msg):
        if self._camera_matrix is None:
            return  # no CameraInfo yet -- can't solvePnP without intrinsics
        if self._uav_attitude is None:
            return  # no attitude yet -- can't rotate camera-frame pose into world frame

        now = self.get_clock().now().nanoseconds / 1e9

        frame = self._decode_image(msg)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        corners, ids, _ = self._detect(gray)

        target = LandingTarget()

        if ids is None or MARKER_ID not in ids.flatten():
            self._publish_not_detected(target, now)
            return

        index = list(ids.flatten()).index(MARKER_ID)
        marker_corners = corners[index][0]  # 4x2, order: TL, TR, BR, BL

        ok, rvec, tvec = cv2.solvePnP(
            self._object_points, marker_corners, self._camera_matrix, self._dist_coeffs,
        )
        if not ok:
            self._publish_not_detected(target, now)
            return

        tvec_camera = tvec.flatten()

        roll, pitch, yaw = self._uav_attitude
        r_world_from_body = euler_to_rotation_matrix(roll, pitch, yaw)

        rel_body = CAMERA_TO_BODY @ tvec_camera
        rel_world = r_world_from_body @ rel_body

        rel_x, rel_y, rel_z = float(rel_world[0]), float(rel_world[1]), float(rel_world[2])

        # Best-effort relative yaw from the marker's in-image rotation --
        # not currently consumed by the (1D-only) RL observation set, and
        # unlike rel_x/rel_y/rel_z above, hasn't been validated against a
        # known-orientation hover test. Treat as approximate.
        rot_matrix, _ = cv2.Rodrigues(rvec)
        marker_yaw_in_camera = math.atan2(rot_matrix[1, 0], rot_matrix[0, 0])
        rel_yaw = math.atan2(math.sin(marker_yaw_in_camera), math.cos(marker_yaw_in_camera))

        target.relative_x = rel_x
        target.relative_y = rel_y
        target.relative_z = rel_z
        target.relative_yaw = rel_yaw
        target.detected = True

        self._last_valid_t = now
        self._last_valid_rel = (rel_x, rel_y, rel_z)

        self.publisher.publish(target)

    def _publish_not_detected(self, target: LandingTarget, now: float):
        """Report the marker as lost rather than silently repeating a stale
        pose -- vision_relative_state_node treats `detected=False` as "no
        fresh observation", not "target hasn't moved"."""

        if self._last_valid_t is not None and (now - self._last_valid_t) < DETECTION_TIMEOUT_SEC:
            return  # brief dropout (a frame or two) -- don't spam "lost" yet

        target.relative_x = 0.0
        target.relative_y = 0.0
        target.relative_z = 0.0
        target.relative_yaw = 0.0
        target.detected = False
        self.publisher.publish(target)


def main():
    rclpy.init()

    node = ArucoLandingTargetNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
