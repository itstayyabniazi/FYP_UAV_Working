#!/usr/bin/env python3
"""
Standalone sanity check for the ArUco detection logic in
aruco_landing_target_node.py, decoupled from the live Gazebo camera/ROS2
pipeline -- useful when that pipeline isn't producing data (e.g. a host
GPU/driver limitation blocking Gazebo's headless sensor rendering) but you
still want to confirm the detection algorithm itself works against a real
image of the marker as actually rendered (lighting, the new cross border,
etc, not just the flat source PNG).

Usage:
    python3 test_marker_detection.py path/to/screenshot.png

Take the input image any way that's convenient -- a screenshot of the
Gazebo GUI zoomed in on the platform, a phone photo of a printed marker,
whatever. This doesn't need to be an actual camera-topic frame; it's
checking the same cv2.aruco.detectMarkers() call the real node makes,
against real pixels.

Writes <input>_annotated.png next to the input, with detected marker(s)
outlined, so you can visually confirm it found the right one.
"""
import sys
from pathlib import Path

import cv2

# Keep in sync with aruco_landing_target_node.py.
ARUCO_DICT = cv2.aruco.DICT_4X4_50
MARKER_ID = 0


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 test_marker_detection.py path/to/image.png")
        sys.exit(1)

    image_path = Path(sys.argv[1])
    frame = cv2.imread(str(image_path))
    if frame is None:
        print(f"Could not read image: {image_path}")
        sys.exit(1)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if hasattr(cv2.aruco, "ArucoDetector"):
        dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
        detector = cv2.aruco.ArucoDetector(dictionary, cv2.aruco.DetectorParameters())
        corners, ids, rejected = detector.detectMarkers(gray)
    else:
        dictionary = cv2.aruco.Dictionary_get(ARUCO_DICT)
        parameters = cv2.aruco.DetectorParameters_create()
        corners, ids, rejected = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)

    print(f"Image size: {frame.shape[1]}x{frame.shape[0]}")
    print(f"Candidate shapes considered (rejected + accepted): {len(rejected) + (len(corners) if corners else 0)}")

    if ids is None:
        print("NO markers detected at all.")
        sys.exit(0)

    detected_ids = ids.flatten().tolist()
    print(f"Detected marker IDs: {detected_ids}")

    if MARKER_ID in detected_ids:
        print(f"Target marker (id={MARKER_ID}) FOUND.")
    else:
        print(f"Marker(s) found, but not id={MARKER_ID} (the one the platform uses).")

    annotated = cv2.aruco.drawDetectedMarkers(frame.copy(), corners, ids)
    out_path = image_path.with_name(image_path.stem + "_annotated" + image_path.suffix)
    cv2.imwrite(str(out_path), annotated)
    print(f"Wrote {out_path} -- open it to visually confirm the detection.")


if __name__ == "__main__":
    main()
