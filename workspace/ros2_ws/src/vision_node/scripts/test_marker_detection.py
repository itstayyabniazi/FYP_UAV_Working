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

Always writes <input>_annotated.png next to the input (even on a total
detection failure) -- green boxes/IDs for confirmed markers, red outlines
for candidate shapes the detector considered but rejected at the
bit-decoding stage. That distinction matters: red-but-no-green means the
detector is finding the marker's outline fine but failing to read its
internal pattern (blur, oblique angle, low contrast), a different problem
than finding nothing at all.
"""
import sys
from pathlib import Path

import cv2

# Keep in sync with aruco_landing_target_node.py.
ARUCO_DICT = cv2.aruco.DICT_4X4_50
MARKER_ID = 0


def build_detector_params():
    """Same tuning as aruco_landing_target_node.py's build_detector_params()
    -- see that docstring for why the defaults need loosening for synthetic
    renders. Duplicated here rather than imported since this script is meant
    to run standalone without the ROS 2 workspace necessarily sourced."""

    if hasattr(cv2.aruco, "DetectorParameters_create"):
        params = cv2.aruco.DetectorParameters_create()  # OpenCV < 4.7
    else:
        params = cv2.aruco.DetectorParameters()
    params.adaptiveThreshWinSizeMin = 3
    params.adaptiveThreshWinSizeMax = 53
    params.adaptiveThreshWinSizeStep = 4
    params.perspectiveRemovePixelPerCell = 8
    params.minOtsuStdDev = 2.0
    return params


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
    parameters = build_detector_params()

    if hasattr(cv2.aruco, "ArucoDetector"):
        dictionary = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
        detector = cv2.aruco.ArucoDetector(dictionary, parameters)
        corners, ids, rejected = detector.detectMarkers(gray)
    else:
        dictionary = cv2.aruco.Dictionary_get(ARUCO_DICT)
        corners, ids, rejected = cv2.aruco.detectMarkers(gray, dictionary, parameters=parameters)

    print(f"Image size: {frame.shape[1]}x{frame.shape[0]}")
    print(f"Confirmed markers: {0 if ids is None else len(ids)}")
    print(f"Candidate shapes rejected at bit-decoding: {len(rejected)}")

    annotated = frame.copy()
    for quad in rejected:
        cv2.polylines(annotated, [quad.astype(int)], isClosed=True, color=(0, 0, 255), thickness=2)

    if ids is not None:
        annotated = cv2.aruco.drawDetectedMarkers(annotated, corners, ids)
        detected_ids = ids.flatten().tolist()
        print(f"Detected marker IDs: {detected_ids}")
        if MARKER_ID in detected_ids:
            print(f"Target marker (id={MARKER_ID}) FOUND.")
        else:
            print(f"Marker(s) found, but not id={MARKER_ID} (the one the platform uses).")
    else:
        print("NO markers detected.")
        if rejected:
            print(
                f"But {len(rejected)} candidate shape(s) were found and rejected -- "
                "see the red outlines in the annotated image. That means the detector "
                "found something marker-shaped but couldn't read its internal pattern "
                "(likely blur, an oblique viewing angle, or low contrast -- try a "
                "closer/more top-down shot)."
            )

    out_path = image_path.with_name(image_path.stem + "_annotated" + image_path.suffix)
    cv2.imwrite(str(out_path), annotated)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
