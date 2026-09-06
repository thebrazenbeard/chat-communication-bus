import json
from pathlib import Path

import pytest

from radar.writer_lanes import (
    WriterLaneError,
    load_registered_writer_lanes,
    load_writer_lanes,
)


ROOT = Path(__file__).resolve().parents[2]
TOPOLOGY = ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json"
ONBOARDING = ROOT / "architecture" / "contracts" / "RADAR_WRITER_LANE_ONBOARDING_V1.json"


def test_active_view_excludes_registered_inert_parallax() -> None:
    active = load_writer_lanes(TOPOLOGY)
    registered = load_registered_writer_lanes(TOPOLOGY)
    assert "parallax" not in active
    assert registered["parallax"].branch == "bus/parallax-v1"
    assert registered["parallax"].lifecycle == "REGISTERED_INERT"
    assert registered["radar"].lifecycle == "ACTIVE"


def test_parallax_currentness_is_topology_merged_but_first_append_still_inert() -> None:
    topology = json.loads(TOPOLOGY.read_text())
    onboarding = json.loads(ONBOARDING.read_text())
    lane = topology["required_writer_lanes"]["parallax"]
    assert lane["lifecycle"] == "REGISTERED_INERT"
    assert lane["onboarding_status"] == "FIRST_APPEND_PENDING"
    assert onboarding["status"] == "FIRST_APPEND_PENDING"
    assert onboarding["topology_pr_merged"] is True
    assert onboarding["first_append_guard_verified"] is False


def test_unknown_lifecycle_fails_closed(tmp_path: Path) -> None:
    raw = json.loads(TOPOLOGY.read_text())
    raw["required_writer_lanes"]["radar"]["lifecycle"] = "MAYBE_ACTIVE"
    candidate = tmp_path / "topology.json"
    candidate.write_text(json.dumps(raw))
    with pytest.raises(WriterLaneError, match="WRITER_LANE_LIFECYCLE_INVALID"):
        load_registered_writer_lanes(candidate)
