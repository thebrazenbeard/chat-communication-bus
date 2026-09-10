from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from radar.trusted_reconciler import AncestryDisposition, ReconcileTarget
from radar.writer_lanes import WriterLaneError


def _load_entrypoint():
    script = Path(__file__).resolve().parents[2] / "scripts" / "radar_trusted_reconcile.py"
    spec = importlib.util.spec_from_file_location("radar_trusted_reconcile_entrypoint", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _FakeReconciler:
    def __init__(self, *args, **kwargs) -> None:
        pass

    def derive_target(self, identity: str) -> ReconcileTarget:
        assert identity == "yin"
        return ReconcileTarget(
            identity="yin",
            branch="bus/yin-v2",
            projected_head="a0",
            base_head="a0",
            observed_head="a2",
            commits=("a1", "a2"),
            disposition=AncestryDisposition.FORWARD,
            bootstrap=False,
        )


def _patch_target_derivation(monkeypatch, module) -> None:
    monkeypatch.setattr(
        module,
        "requested_identities",
        lambda **_kwargs: (("yin",), None),
    )
    monkeypatch.setattr(
        module,
        "LocalGitRepository",
        lambda *_args, **_kwargs: object(),
    )
    monkeypatch.setattr(module, "TrustedReconciler", _FakeReconciler)


def test_validate_only_revalidates_forward_writer_range_before_reporting(
    monkeypatch, tmp_path
) -> None:
    module = _load_entrypoint()
    _patch_target_derivation(monkeypatch, module)
    calls: list[dict[str, object]] = []

    def validate_range(repo_dir, **kwargs):
        calls.append({"repo_dir": repo_dir, **kwargs})
        return ("a1", "a2")

    monkeypatch.setattr(module, "validate_active_writer_range", validate_range)

    report = module.build_validation_report(
        repo_dir=tmp_path,
        topology_path=tmp_path / "topology.json",
        cutover_path=tmp_path / "cutover.json",
        event_name="schedule",
        event={},
        repository="thebrazenbeard/chat-communication-bus",
    )

    assert len(calls) == 1
    assert calls[0]["identity"] == "yin"
    assert calls[0]["base"] == "a0"
    assert calls[0]["head"] == "a2"
    assert report["targets"][0]["commits"] == ("a1", "a2")
    assert report["targets"][0]["writer_range_validated"] is True


def test_validate_only_propagates_logical_message_id_collision(monkeypatch, tmp_path) -> None:
    module = _load_entrypoint()
    _patch_target_derivation(monkeypatch, module)

    def reject_collision(*_args, **_kwargs):
        raise WriterLaneError(
            "DUPLICATE_NEW_MESSAGE_ID:yin-race:messages/alternate-name.md"
        )

    monkeypatch.setattr(module, "validate_active_writer_range", reject_collision)

    with pytest.raises(WriterLaneError, match="DUPLICATE_NEW_MESSAGE_ID"):
        module.build_validation_report(
            repo_dir=tmp_path,
            topology_path=tmp_path / "topology.json",
            cutover_path=tmp_path / "cutover.json",
            event_name="schedule",
            event={},
            repository="thebrazenbeard/chat-communication-bus",
        )
