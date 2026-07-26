#!/usr/bin/env python3
"""
Generates the ArUco marker image used as the visual landing target on top of
the moving platform (see ../models/moving_platform/model.sdf's
"aruco_marker" visual, which references the PNG this writes).

Run once, inside the Docker container (needs opencv-contrib-python, which
the Dockerfile installs for the vision pipeline anyway):

    python3 generate_aruco_marker.py

DICT_4X4_50 / marker id 0 was picked for robustness at typical landing
distances (a 4x4-bit dictionary has larger, easier-to-resolve cells than a
5x5/6x6 one when the marker is small in the camera's frame) and for having
plenty of spare IDs (0-49) if you ever need multiple distinguishable
platforms. If you change DICT/MARKER_ID here, keep it in sync with
aruco_landing_target_node.py's ARUCO_DICT/MARKER_ID constants -- they must
match for detection to work at all.
"""
import pathlib

import cv2

DICT = cv2.aruco.DICT_4X4_50
MARKER_ID = 0
IMAGE_SIZE_PX = 700  # high-res source image; Gazebo scales it to the visual's physical size

OUTPUT_PATH = (
    pathlib.Path(__file__).resolve().parent.parent
    / "models" / "moving_platform" / "materials" / "textures" / "aruco_marker.png"
)


def main():
    aruco_dict = cv2.aruco.getPredefinedDictionary(DICT)

    if hasattr(cv2.aruco, "generateImageMarker"):
        marker_image = cv2.aruco.generateImageMarker(aruco_dict, MARKER_ID, IMAGE_SIZE_PX)
    else:
        # OpenCV < 4.7 fallback
        marker_image = cv2.aruco.drawMarker(aruco_dict, MARKER_ID, IMAGE_SIZE_PX)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(OUTPUT_PATH), marker_image)

    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
