import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORD = ROOT / "architecture/reconstruction/EXODUS_WORKER_MUNE_V1.json"
CENSUS = ROOT / "architecture/contracts/EXODUS_WORKER_RECONSTRUCTION_CENSUS_V1.json"

FINAL_MUNE_HEAD = "ded4326c727ea4613079e21bc26f3bf82ec7aa01"
PACKAGE_PATH = "archive/training-sources/build-team-2.0/mune/v1.0.1"
PACKAGE_TREE = "5e8c87021bfda9a6fc44fa121c32410ddc6aedf9"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_mune_reconstruction_binds_canonical_package_not_retired_chat():
    record = load(RECORD)
    package = record["immutable_role_package"]
    assert record["identity_id"] == "mune"
    assert record["reconstruction_status"] == "READY"
    assert record["retired_chat_required"] is False
    assert package["repository"] == "thebrazenbeard/bt2"
    assert package["path"] == PACKAGE_PATH
    assert package["package_tree"] == PACKAGE_TREE
    assert package["qualification_state"] == "QUALIFICATION_UNPROVEN"
    assert "No dedicated immutable package entry exists" not in record["qualification_gap"]


def test_mune_census_pins_final_retirement_cut():
    census = load(CENSUS)
    mune = next(worker for worker in census["workers"] if worker["identity_id"] == "mune")
    assert mune["reconstruction_status"] == "READY"
    assert mune["missing_reconstruction_fields"] == []
    assert mune["observed_head"] == FINAL_MUNE_HEAD
    assert "checkpoints/mune/MUNE_EXODUS_FINAL_20260920T0713-0400.md" in mune["durable_evidence"]
