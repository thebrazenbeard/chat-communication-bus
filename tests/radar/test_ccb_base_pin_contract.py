import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
PIN_PATH = ROOT / "architecture" / "contracts" / "CCB_BASE_CONTROL_PIN_V1.json"
README = ROOT / "README.md"
WORKFLOWS = (
    ROOT / ".github" / "workflows" / "writer-lane-guard.yml",
    ROOT / ".github" / "workflows" / "radar-trusted-projector.yml",
)
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def test_ccb_base_pin_is_exact_and_consistent():
    pin = json.loads(PIN_PATH.read_text(encoding="utf-8"))
    assert pin["schema"] == "CHAT_COMMUNICATION_BUS_CCB_BASE_CONTROL_PIN_V1"
    assert pin["repository"] == "thebrazenbeard/ccb-core"
    assert SHA40.fullmatch(pin["commit"])
    assert SHA40.fullmatch(pin["tree"])

    readme = README.read_text(encoding="utf-8")
    assert pin["commit"] in readme

    for workflow in WORKFLOWS:
        source = workflow.read_text(encoding="utf-8")
        assert "repository: thebrazenbeard/ccb-core" in source
        assert f"ref: {pin['commit']}" in source


def test_private_overlay_paths_remain_explicit():
    pin = json.loads(PIN_PATH.read_text(encoding="utf-8"))
    required = set(pin["private_overlay_inputs"])
    writer = WORKFLOWS[0].read_text(encoding="utf-8")
    projector = WORKFLOWS[1].read_text(encoding="utf-8")

    assert "--topology overlay/architecture/contracts/RADAR_TOPOLOGY_V1.json" in writer
    assert "--cutover overlay/architecture/contracts/RADAR_WRITER_LANE_V2_CUTOVER.json" in writer
    assert "--topology canonical/architecture/contracts/RADAR_TOPOLOGY_V1.json" in projector
    assert "--cutover canonical/architecture/contracts/RADAR_WRITER_LANE_V2_CUTOVER.json" in projector
    assert required == {
        "architecture/contracts/RADAR_TOPOLOGY_V1.json",
        "architecture/contracts/RADAR_WRITER_LANE_V2_CUTOVER.json",
    }


def test_pin_does_not_grant_protected_effects():
    pin = json.loads(PIN_PATH.read_text(encoding="utf-8"))
    assert all(value is False for value in pin["authority"].values())
