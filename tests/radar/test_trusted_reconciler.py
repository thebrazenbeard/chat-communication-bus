from __future__ import annotations

import json

import pytest

from radar.trusted_reconciler import (
    AncestryDisposition,
    ReconcileError,
    TrustedReconciler,
)


class FakeGit:
    def __init__(self, heads, parents):
        self.heads = dict(heads)
        self.parents = dict(parents)

    def branch_head(self, branch):
        try:
            return self.heads[branch]
        except KeyError as exc:
            raise ReconcileError("MISSING_WRITER_BRANCH") from exc

    def is_ancestor(self, ancestor, descendant):
        current = descendant
        while current is not None:
            if current == ancestor:
                return True
            current = self.parents.get(current)
        return False

    def commits_between(self, base, head):
        if base == head:
            return ()
        commits = []
        current = head
        while current is not None and current != base:
            commits.append(current)
            current = self.parents.get(current)
        if current != base:
            raise ReconcileError("DIVERGED_HISTORY")
        return tuple(reversed(commits))


class FakeJournal:
    def __init__(self, cursors=None):
        self.cursors = dict(cursors or {})

    def projected_head(self, identity, branch):
        return self.cursors.get((identity, branch))


def _write_contracts(tmp_path, *, lifecycle="ACTIVE", branch="bus/yin-v2", anchor="a0"):
    topology = tmp_path / "topology.json"
    topology.write_text(
        json.dumps(
            {
                "required_writer_lanes": {
                    "yin": {
                        "writer": "Yin",
                        "branch": branch,
                        "lifecycle": lifecycle,
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    cutover = tmp_path / "cutover.json"
    cutover.write_text(
        json.dumps(
            {
                "planned_current_writer_lanes": {"yin": branch},
                "current_writer_lanes": {"yin": branch},
                "verified_successor_heads": {"yin": anchor},
                "historical_writer_lanes": {
                    "yin": {"branch": "bus/yin-v1", "head_sha": "old0"}
                },
            }
        ),
        encoding="utf-8",
    )
    return topology, cutover


def test_uninitialized_lane_bootstraps_from_lane_owned_anchor(tmp_path):
    topology, cutover = _write_contracts(tmp_path)
    git = FakeGit({"bus/yin-v2": "a2"}, {"a2": "a1", "a1": "a0", "a0": None})

    target = TrustedReconciler(
        topology_path=topology,
        cutover_path=cutover,
        git_repository=git,
        journal=FakeJournal(),
    ).derive_target("yin")

    assert target.disposition is AncestryDisposition.FORWARD
    assert target.projected_head is None
    assert target.base_head == "a0"
    assert target.observed_head == "a2"
    assert target.commits == ("a1", "a2")
    assert target.bootstrap is True


def test_equal_cursor_is_noop(tmp_path):
    topology, cutover = _write_contracts(tmp_path)
    git = FakeGit({"bus/yin-v2": "a2"}, {"a2": "a1", "a1": "a0"})
    journal = FakeJournal({("yin", "bus/yin-v2"): "a2"})

    target = TrustedReconciler(topology, cutover, git, journal).derive_target("yin")

    assert target.disposition is AncestryDisposition.NOOP
    assert target.commits == ()


def test_forward_cursor_returns_every_unseen_commit_in_order(tmp_path):
    topology, cutover = _write_contracts(tmp_path)
    git = FakeGit({"bus/yin-v2": "a3"}, {"a3": "a2", "a2": "a1", "a1": "a0"})
    journal = FakeJournal({("yin", "bus/yin-v2"): "a1"})

    target = TrustedReconciler(topology, cutover, git, journal).derive_target("yin")

    assert target.disposition is AncestryDisposition.FORWARD
    assert target.base_head == "a1"
    assert target.commits == ("a2", "a3")


def test_stale_observed_head_is_no_effect_stale_event(tmp_path):
    topology, cutover = _write_contracts(tmp_path)
    git = FakeGit({"bus/yin-v2": "a1"}, {"a3": "a2", "a2": "a1", "a1": "a0"})
    journal = FakeJournal({("yin", "bus/yin-v2"): "a3"})

    target = TrustedReconciler(topology, cutover, git, journal).derive_target("yin")

    assert target.disposition is AncestryDisposition.STALE_EVENT
    assert target.commits == ()


def test_diverged_history_fails_closed_as_disposition(tmp_path):
    topology, cutover = _write_contracts(tmp_path)
    git = FakeGit(
        {"bus/yin-v2": "right1"},
        {"left1": "a0", "right1": "a0", "a0": None},
    )
    journal = FakeJournal({("yin", "bus/yin-v2"): "left1"})

    target = TrustedReconciler(topology, cutover, git, journal).derive_target("yin")

    assert target.disposition is AncestryDisposition.DIVERGED_HISTORY
    assert target.commits == ()


def test_registered_inert_lane_cannot_be_reconciled(tmp_path):
    topology, cutover = _write_contracts(tmp_path, lifecycle="REGISTERED_INERT")
    git = FakeGit({"bus/yin-v2": "a0"}, {"a0": None})

    with pytest.raises(ReconcileError, match="NON_ACTIVE_WRITER_LANE"):
        TrustedReconciler(topology, cutover, git, FakeJournal()).derive_target("yin")


def test_missing_canonical_branch_fails_closed(tmp_path):
    topology, cutover = _write_contracts(tmp_path)

    with pytest.raises(ReconcileError, match="MISSING_WRITER_BRANCH"):
        TrustedReconciler(topology, cutover, FakeGit({}, {}), FakeJournal()).derive_target("yin")


def test_legacy_current_branch_uses_historical_snapshot_as_bootstrap_anchor(tmp_path):
    topology, cutover = _write_contracts(tmp_path, branch="bus/yin-v1", anchor="successor0")
    cutover.write_text(
        json.dumps(
            {
                "planned_current_writer_lanes": {"yin": "bus/yin-v2"},
                "current_writer_lanes": {"yin": "bus/yin-v1"},
                "verified_successor_heads": {"yin": "successor0"},
                "historical_writer_lanes": {
                    "yin": {"branch": "bus/yin-v1", "head_sha": "old0"}
                },
            }
        ),
        encoding="utf-8",
    )
    git = FakeGit({"bus/yin-v1": "old2"}, {"old2": "old1", "old1": "old0"})

    target = TrustedReconciler(topology, cutover, git, FakeJournal()).derive_target("yin")

    assert target.base_head == "old0"
    assert target.commits == ("old1", "old2")
