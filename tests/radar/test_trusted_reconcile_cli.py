from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from radar.trusted_reconciler import ReconcileError


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "radar_trusted_reconcile.py"


def _load_script_module():
    spec = importlib.util.spec_from_file_location("radar_trusted_reconcile_test_module", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _contracts(tmp_path: Path):
    topology = tmp_path / "topology.json"
    topology.write_text(
        json.dumps(
            {
                "required_writer_lanes": {
                    "yin": {
                        "writer": "Yin",
                        "branch": "bus/yin-v2",
                        "lifecycle": "ACTIVE",
                    },
                    "parallax": {
                        "writer": "Parallax",
                        "branch": "bus/parallax-v1",
                        "lifecycle": "REGISTERED_INERT",
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    cutover = tmp_path / "cutover.json"
    cutover.write_text(
        json.dumps(
            {
                "planned_current_writer_lanes": {"yin": "bus/yin-v2"},
                "current_writer_lanes": {"yin": "bus/yin-v2"},
                "verified_successor_heads": {"yin": "a0"},
                "historical_writer_lanes": {
                    "yin": {"branch": "bus/yin-v1", "head_sha": "old0"}
                },
            }
        ),
        encoding="utf-8",
    )
    return topology, cutover


class FakeGit:
    def branch_head(self, branch: str) -> str:
        assert branch == "bus/yin-v2"
        return "a2"

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        order = {"a0": 0, "a1": 1, "a2": 2}
        return ancestor in order and descendant in order and order[ancestor] <= order[descendant]

    def commits_between(self, base: str, head: str) -> tuple[str, ...]:
        assert base == "a0" and head == "a2"
        return ("a1", "a2")


def test_workflow_run_head_is_observation_hint_not_projection_authority(tmp_path, monkeypatch) -> None:
    module = _load_script_module()
    topology, cutover = _contracts(tmp_path)
    monkeypatch.setattr(module, "LocalGitRepository", lambda _repo: FakeGit())

    report = module.build_validation_report(
        repo_dir=tmp_path,
        topology_path=topology,
        cutover_path=cutover,
        event_name="workflow_run",
        event={
            "workflow_run": {
                "head_branch": "bus/yin-v2",
                "head_sha": "f" * 40,
            }
        },
        repository="thebrazenbeard/chat-communication-bus",
    )

    target = report["targets"][0]
    assert target["observed_head"] == "a2"
    assert target["workflow_run_head_hint"] == "f" * 40
    assert target["hint_matches_observed_head"] is False
    assert target["commits"] == ("a1", "a2")


def test_schedule_enumerates_only_active_topology_lanes(tmp_path, monkeypatch) -> None:
    module = _load_script_module()
    topology, cutover = _contracts(tmp_path)
    monkeypatch.setattr(module, "LocalGitRepository", lambda _repo: FakeGit())

    report = module.build_validation_report(
        repo_dir=tmp_path,
        topology_path=topology,
        cutover_path=cutover,
        event_name="schedule",
        event={},
        repository="thebrazenbeard/chat-communication-bus",
    )

    assert [target["identity"] for target in report["targets"]] == ["yin"]


def test_registered_inert_branch_cannot_wake_reconciliation(tmp_path) -> None:
    module = _load_script_module()
    topology, _cutover = _contracts(tmp_path)

    with pytest.raises(ReconcileError, match="WAKEUP_BRANCH_NOT_ACTIVE"):
        module._requested_identities(
            event_name="workflow_run",
            event={
                "workflow_run": {
                    "head_branch": "bus/parallax-v1",
                    "head_sha": "e" * 40,
                }
            },
            topology_path=topology,
        )


def test_untrusted_repository_and_non_sha_wakeup_fail_closed(tmp_path) -> None:
    module = _load_script_module()
    topology, cutover = _contracts(tmp_path)

    with pytest.raises(ReconcileError, match="UNTRUSTED_CALLER_REPOSITORY"):
        module.build_validation_report(
            repo_dir=tmp_path,
            topology_path=topology,
            cutover_path=cutover,
            event_name="schedule",
            event={},
            repository="other/repository",
        )

    with pytest.raises(ReconcileError, match="WORKFLOW_RUN_HEAD_INVALID"):
        module._requested_identities(
            event_name="workflow_run",
            event={"workflow_run": {"head_branch": "bus/yin-v2", "head_sha": "main"}},
            topology_path=topology,
        )
