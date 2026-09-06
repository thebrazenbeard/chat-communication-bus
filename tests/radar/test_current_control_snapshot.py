from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from radar.trusted_control_snapshot import (
    ControlSnapshotError,
    materialize_current_control_snapshot,
)


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def _commit(repo: Path, message: str) -> str:
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", message], check=True)
    return _git(repo, "rev-parse", "HEAD")


def _write_contracts(repo: Path, branch: str) -> None:
    contracts = repo / "architecture/contracts"
    contracts.mkdir(parents=True, exist_ok=True)
    (contracts / "RADAR_TOPOLOGY_V1.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "repository": "thebrazenbeard/chat-communication-bus",
                "required_writer_lanes": {
                    "yin": {
                        "writer": "Yin",
                        "branch": branch,
                        "lifecycle": "ACTIVE",
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    (contracts / "RADAR_WRITER_LANE_V2_CUTOVER.json").write_text(
        json.dumps({"planned_current_writer_lanes": {"yin": branch}}),
        encoding="utf-8",
    )


def test_snapshot_reads_current_remote_main_contracts_not_frozen_anchor_tree(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "radar@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Radar Test"], check=True)

    _write_contracts(repo, "bus/yin-v1")
    anchor = _commit(repo, "anchor")

    subprocess.run(["git", "-C", str(repo), "switch", "-qc", "main-current"], check=True)
    _write_contracts(repo, "bus/yin-v2")
    (repo / "must-not-materialize.py").write_text("raise RuntimeError('never execute')\n", encoding="utf-8")
    current_main = _commit(repo, "current main")
    topology_blob = _git(repo, "rev-parse", f"{current_main}:architecture/contracts/RADAR_TOPOLOGY_V1.json")
    cutover_blob = _git(repo, "rev-parse", f"{current_main}:architecture/contracts/RADAR_WRITER_LANE_V2_CUTOVER.json")

    subprocess.run(["git", "-C", str(repo), "update-ref", "refs/remotes/origin/main", current_main], check=True)
    subprocess.run(["git", "-C", str(repo), "checkout", "-q", anchor], check=True)

    output = tmp_path / "snapshot"
    snapshot = materialize_current_control_snapshot(repo, output)

    assert _git(repo, "rev-parse", "HEAD") == anchor
    assert snapshot.main_head_sha == current_main
    assert snapshot.topology_blob_sha == topology_blob
    assert snapshot.cutover_blob_sha == cutover_blob
    topology = json.loads(snapshot.topology_path.read_text(encoding="utf-8"))
    assert topology["required_writer_lanes"]["yin"]["branch"] == "bus/yin-v2"
    assert snapshot.cutover_path.is_file()
    assert not (output / "must-not-materialize.py").exists()


def test_snapshot_fails_closed_without_remote_main(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    with pytest.raises(ControlSnapshotError, match="CURRENT_MAIN_REF_MISSING"):
        materialize_current_control_snapshot(repo, tmp_path / "snapshot")


def test_snapshot_fails_closed_if_required_contract_missing(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "radar@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Radar Test"], check=True)
    (repo / "README.md").write_text("x\n", encoding="utf-8")
    head = _commit(repo, "missing contracts")
    subprocess.run(["git", "-C", str(repo), "update-ref", "refs/remotes/origin/main", head], check=True)

    with pytest.raises(ControlSnapshotError, match="CURRENT_CONTROL_CONTRACT_MISSING"):
        materialize_current_control_snapshot(repo, tmp_path / "snapshot")
