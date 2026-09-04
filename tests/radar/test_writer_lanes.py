import importlib
import json
from pathlib import Path

import pytest


def _writer_lanes():
    try:
        return importlib.import_module("radar.writer_lanes")
    except Exception as exc:
        pytest.fail(f"writer lane implementation missing: {exc}")


def write_topology(tmp_path: Path) -> Path:
    path = tmp_path / "topology.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "required_writer_lanes": {
                    "one": {
                        "writer": "One",
                        "branch": "bus/one-v2",
                        "legacy_spelling": False,
                    },
                    "brigit": {
                        "writer": "Brigit",
                        "branch": "bus/brigit-v2",
                        "legacy_spelling": False,
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    return path


def test_identity_for_ref_comes_only_from_registered_current_lane(tmp_path):
    m = _writer_lanes()
    topology = write_topology(tmp_path)
    assert m.identity_for_ref("refs/heads/bus/one-v2", topology) == "one"
    with pytest.raises(m.WriterLaneError, match="UNREGISTERED_WRITER_LANE"):
        m.identity_for_ref("refs/heads/bus/one-v1", topology)
    with pytest.raises(m.WriterLaneError, match="UNREGISTERED_WRITER_LANE"):
        m.identity_for_ref("refs/heads/bus/one-v2-lookalike", topology)


def test_duplicate_registered_branch_is_rejected(tmp_path):
    m = _writer_lanes()
    topology = tmp_path / "duplicate.json"
    topology.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "required_writer_lanes": {
                    "one": {"writer": "One", "branch": "bus/shared-v2"},
                    "two": {"writer": "Two", "branch": "bus/shared-v2"},
                },
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(m.WriterLaneError, match="DUPLICATE_WRITER_LANE_BRANCH"):
        m.load_writer_lanes(topology)
