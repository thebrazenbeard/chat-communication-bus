from __future__ import annotations

from pathlib import Path

import radar.trusted_lane_validation as validation
from radar.writer_lanes import WriterLane


def test_trusted_range_reuses_writer_guard_commit_validation(monkeypatch, tmp_path) -> None:
    lane = WriterLane(identity="yin", writer="Yin", branch="bus/yin-v2", lifecycle="ACTIVE")
    monkeypatch.setattr(validation, "load_writer_lanes", lambda _path: {"yin": lane})
    ancestry = []
    monkeypatch.setattr(validation, "_assert_ancestor", lambda _repo, base, head: ancestry.append((base, head)))
    monkeypatch.setattr(validation, "_git", lambda _repo, *args: "c1\nc2")
    monkeypatch.setattr(validation, "_historical_message_ids", lambda *_args: {"old-1"})
    calls = []

    def validate_commit(repo, commit, actual_lane, *, reserved_message_ids):
        calls.append((Path(repo), commit, actual_lane, set(reserved_message_ids)))

    monkeypatch.setattr(validation, "_validate_commit_paths", validate_commit)

    commits = validation.validate_active_writer_range(
        tmp_path,
        identity="yin",
        base="a0",
        head="a2",
        topology_path="topology.json",
        cutover_path="cutover.json",
    )

    assert commits == ("c1", "c2")
    assert ancestry == [("a0", "a2")]
    assert [call[1] for call in calls] == ["c1", "c2"]
    assert all(call[2] is lane and call[3] == {"old-1"} for call in calls)


def test_zero_commit_range_is_valid_without_git_walk(monkeypatch, tmp_path) -> None:
    lane = WriterLane(identity="yin", writer="Yin", branch="bus/yin-v2", lifecycle="ACTIVE")
    monkeypatch.setattr(validation, "load_writer_lanes", lambda _path: {"yin": lane})
    monkeypatch.setattr(validation, "_git", lambda *_args: (_ for _ in ()).throw(AssertionError("git walk")))

    assert validation.validate_active_writer_range(
        tmp_path,
        identity="yin",
        base="a0",
        head="a0",
        topology_path="topology.json",
        cutover_path="cutover.json",
    ) == ()
