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

    python3 patch_x500_camera.py [path/to/model.sdf] [--link LINK_NAME]

With no path argument, it searches the default PX4-Autopilot layout under
$HOME and /workspace for Tools/simulation/gz/models/x500/model.sdf.
--link defaults to "base_link"; pass a different one if your PX4 version
names it something else (see the error message below for how to check).

What it does: inserts a <sensor type="camera"> block, pointed straight down
(pose pitch=+90deg -- the standard convention for a downward-mounted camera
in PX4/Gazebo, e.g. the optical-flow/precision-landing camera examples),
into the target <link> right before its closing </link> tag. Since SDF links
can't contain a nested <link>, the first "</link>" found after the opening
tag unambiguously closes it -- no full XML parser needed, and the rest of
the file's formatting/comments are left untouched.

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
import argparse
import re
from pathlib import Path

SENSOR_NAME = "downward_camera"
DEFAULT_LINK = "base_link"

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


def _is_file_safe(path: Path) -> bool:
    """Path.is_file() raises PermissionError (rather than returning False)
    when an ancestor directory isn't readable by the current user -- e.g.
    /root/PX4-Autopilot when running as a non-root user with /root cloned
    for someone else. Treat "can't even tell" the same as "not found"."""
    try:
        return path.is_file()
    except OSError:
        return False


def find_model_sdf() -> Path:
    for root in DEFAULT_SEARCH_ROOTS:
        candidate = root / RELATIVE_MODEL_PATH
        if _is_file_safe(candidate):
            return candidate
    # Fall back to a recursive search, in case PX4-Autopilot was cloned
    # somewhere non-standard.
    for root in DEFAULT_SEARCH_ROOTS:
        try:
            if not root.is_dir():
                continue
            matches = list(root.rglob("Tools/simulation/gz/models/x500/model.sdf"))
        except OSError:
            continue  # e.g. permission denied partway through the walk
        if matches:
            return matches[0]
    raise FileNotFoundError(
        "Could not find PX4-Autopilot's x500/model.sdf automatically. "
        "Pass the path explicitly: "
        "python3 patch_x500_camera.py /path/to/PX4-Autopilot/Tools/simulation/gz/models/x500/model.sdf"
    )


def find_link_anchor(text: str, link_name: str):
    """Returns (anchor_start, anchor_end) for the opening `<link name=...>`
    tag, tolerant of single vs double quotes and extra whitespace -- SDF
    files across PX4 versions aren't all formatted identically."""

    pattern = re.compile(
        r'<link\s+name\s*=\s*[\'"]' + re.escape(link_name) + r'[\'"]\s*>'
    )
    match = pattern.search(text)
    if match is None:
        return None
    return match.start(), match.end()


def patch(model_sdf_path: Path, link_name: str):
    text = model_sdf_path.read_text()

    if SENSOR_NAME in text:
        print(f"'{SENSOR_NAME}' sensor already present in {model_sdf_path} -- nothing to do.")
        return

    anchor = find_link_anchor(text, link_name)
    if anchor is None:
        all_links = re.findall(r'<link\s+name\s*=\s*[\'"]([^\'"]+)[\'"]', text)
        raise ValueError(
            f'Could not find a `<link name="{link_name}">` (in either quote style) in '
            f"{model_sdf_path}. Links actually present in this file: {all_links or '(none found)'}. "
            "Re-run with `--link <name>` picking one of those (the camera should attach to "
            "whichever link represents the vehicle's main body), or insert the sensor block "
            "manually -- see this script's CAMERA_SENSOR_SDF constant."
        )
    _, anchor_end = anchor

    close_index = text.find("</link>", anchor_end)
    if close_index == -1:
        raise ValueError(f"Found the `{link_name}` link but no matching `</link>` in {model_sdf_path}.")

    backup_path = model_sdf_path.with_suffix(model_sdf_path.suffix + ".orig")
    if not backup_path.exists():
        backup_path.write_text(text)
        print(f"Backed up original to {backup_path}")

    patched = text[:close_index] + CAMERA_SENSOR_SDF + text[close_index:]
    model_sdf_path.write_text(patched)
    print(f"Inserted '{SENSOR_NAME}' sensor into the '{link_name}' link of {model_sdf_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "model_sdf_path", nargs="?", default=None,
        help="Path to the x500 model.sdf. Auto-detected under $HOME and /workspace if omitted.",
    )
    parser.add_argument(
        "--link", default=DEFAULT_LINK,
        help=f"Link to attach the camera sensor to (default: {DEFAULT_LINK}).",
    )
    args = parser.parse_args()

    model_sdf_path = Path(args.model_sdf_path) if args.model_sdf_path else find_model_sdf()

    patch(model_sdf_path, args.link)


if __name__ == "__main__":
    main()
