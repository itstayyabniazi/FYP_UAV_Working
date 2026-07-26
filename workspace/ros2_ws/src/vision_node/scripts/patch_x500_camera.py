#!/usr/bin/env python3
"""
Adds a downward-facing camera sensor to the PX4 x500 model, for the ArUco
marker detection pipeline (see aruco_landing_target_node.py).

The x500 model lives inside the PX4-Autopilot checkout, not in this repo
(workspace/px4/ is gitignored -- see the top-level .gitignore -- since it's a
multi-GB vendored build tree, same reasoning as workspace/tools/). So instead
of maintaining a forked copy of PX4's model here, this script patches your
existing checkout directly, idempotently (safe to re-run) and with a backup.

Usage (inside the Docker container, wherever PX4-Autopilot was cloned):

    python3 patch_x500_camera.py [path/to/PX4-Autopilot/Tools/simulation/gz/models/x500/model.sdf]

With no argument, it searches the default PX4-Autopilot layout under
$HOME and /workspace for Tools/simulation/gz/models/x500/model.sdf.

What it does: inserts a <sensor type="camera"> block, pointed straight down
(pose pitch=+90deg -- the standard convention for a downward-mounted camera
in PX4/Gazebo, e.g. the optical-flow/precision-landing camera examples),
into <link name="base_link"> right before its closing </link> tag. Since SDF
links can't contain a nested <link>, the first "</link>" found after
"<link name=\"base_link\">" unambiguously closes it -- no full XML parser
needed, and the rest of the file's formatting/comments are left untouched.

After running this, the world's SDF also needs the Sensors system plugin
loaded for the camera to actually render/publish anything -- PX4's default
Gazebo worlds already load it (needed for optical flow / depth cameras in
other PX4 vehicle models), but if you get an empty/black image with no
errors, check the world file for:

    <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
      <render_engine>ogre2</render_engine>
    </plugin>

See vision_node/README.md for the full setup (marker generation, this patch,
the ros_gz_bridge camera bridge commands, and how to run the node).
"""
import sys
from pathlib import Path

SENSOR_NAME = "downward_camera"

CAMERA_SENSOR_SDF = f"""      <sensor name="{SENSOR_NAME}" type="camera">
        <!-- pitch = +pi/2: rotates the sensor's forward look direction from
             the body's nose (+X) to straight down (+Z, FRD down) -- the
             standard downward-camera mount convention. -->
        <pose>0 0 0 0 1.5707963267948966 0</pose>
        <camera>
          <horizontal_fov>1.3962634</horizontal_fov>
          <image>
            <width>640</width>
            <height>480</height>
            <format>R8G8B8</format>
          </image>
          <clip>
            <near>0.05</near>
            <far>20</far>
          </clip>
        </camera>
        <always_on>1</always_on>
        <update_rate>30</update_rate>
        <visualize>true</visualize>
        <topic>drone_camera</topic>
      </sensor>
"""

DEFAULT_SEARCH_ROOTS = [
    Path.home(),
    Path("/workspace"),
    Path("/root"),
]
RELATIVE_MODEL_PATH = Path("PX4-Autopilot/Tools/simulation/gz/models/x500/model.sdf")


def find_model_sdf() -> Path:
    for root in DEFAULT_SEARCH_ROOTS:
        candidate = root / RELATIVE_MODEL_PATH
        if candidate.is_file():
            return candidate
    # Fall back to a recursive search, in case PX4-Autopilot was cloned
    # somewhere non-standard.
    for root in DEFAULT_SEARCH_ROOTS:
        if not root.is_dir():
            continue
        matches = list(root.rglob("Tools/simulation/gz/models/x500/model.sdf"))
        if matches:
            return matches[0]
    raise FileNotFoundError(
        "Could not find PX4-Autopilot's x500/model.sdf automatically. "
        "Pass the path explicitly: "
        "python3 patch_x500_camera.py /path/to/PX4-Autopilot/Tools/simulation/gz/models/x500/model.sdf"
    )


def patch(model_sdf_path: Path):
    text = model_sdf_path.read_text()

    if SENSOR_NAME in text:
        print(f"'{SENSOR_NAME}' sensor already present in {model_sdf_path} -- nothing to do.")
        return

    anchor = '<link name="base_link">'
    anchor_index = text.find(anchor)
    if anchor_index == -1:
        raise ValueError(
            f'Could not find `{anchor}` in {model_sdf_path} -- the x500 model '
            "may have changed. Insert the camera sensor block manually; see "
            "this script's CAMERA_SENSOR_SDF constant."
        )

    close_index = text.find("</link>", anchor_index)
    if close_index == -1:
        raise ValueError(f"Found `{anchor}` but no matching `</link>` in {model_sdf_path}.")

    backup_path = model_sdf_path.with_suffix(model_sdf_path.suffix + ".orig")
    if not backup_path.exists():
        backup_path.write_text(text)
        print(f"Backed up original to {backup_path}")

    patched = text[:close_index] + CAMERA_SENSOR_SDF + text[close_index:]
    model_sdf_path.write_text(patched)
    print(f"Inserted '{SENSOR_NAME}' sensor into {model_sdf_path}")


def main():
    if len(sys.argv) > 1:
        model_sdf_path = Path(sys.argv[1])
    else:
        model_sdf_path = find_model_sdf()

    patch(model_sdf_path)


if __name__ == "__main__":
    main()
