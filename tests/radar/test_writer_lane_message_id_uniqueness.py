from __future__ import annotations

import json
import subprocess

import pytest

from tests.radar.test_writer_lanes import commit_file, make_lane_repo, write_topology


def test_current_lane_rejects_reused_message_id_under_new_path(tmp_path):
    from radar import writer_lanes as m

    topology = write_topology(tmp_path)
    repo = make_lane_repo(tmp_path)
    first = commit_file(
        repo,
        "messages/0001.md",
        "message_id: one-0001\nwriter: One\n",
        "first message",
    )
    assert (
        m.validate_writer_lane_commit(
            repo,
            "refs/heads/bus/one-v2",
            first,
            topology,
        )
        == "one"
    )

    head = commit_file(
        repo,
        "messages/0002.md",
        "message_id: one-0001\nwriter: One\n",
        "reuse id under different path",
    )

    with pytest.raises(m.WriterLaneError, match="DUPLICATE_NEW_MESSAGE_ID:one-0001"):
        m.validate_writer_lane_commit(
            repo,
            "refs/heads/bus/one-v2",
            head,
            topology,
            base=first,
        )


def test_grandfathered_duplicate_ids_do_not_block_new_unique_append(tmp_path):
    from radar import writer_lanes as m

    topology = write_topology(tmp_path)
    repo = make_lane_repo(tmp_path)
    (repo / "messages" / "legacy-a.md").write_text(
        "message_id: one-0001\nwriter: One\n", encoding="utf-8"
    )
    (repo / "messages" / "legacy-b.md").write_text(
        "message_id: one-0001\nwriter: One\n", encoding="utf-8"
    )
    subprocess.check_call(["git", "-C", str(repo), "add", "messages"])
    subprocess.check_call(
        ["git", "-C", str(repo), "commit", "-qm", "grandfathered duplicate history"]
    )
    grandfathered_head = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()

    current_head = commit_file(
        repo,
        "messages/current.md",
        "message_id: one-0002\nwriter: One\n",
        "new unique message",
    )

    assert (
        m.validate_writer_lane_commit(
            repo,
            "refs/heads/bus/one-v2",
            current_head,
            topology,
            base=grandfathered_head,
        )
        == "one"
    )


def test_current_lane_rejects_message_id_reused_from_historical_lane_snapshot(tmp_path):
    from radar import writer_lanes as m

    topology = write_topology(tmp_path)
    repo = make_lane_repo(tmp_path)
    base = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()

    subprocess.check_call(
        ["git", "-C", str(repo), "checkout", "-qb", "bus/one-v1", base]
    )
    historical_head = commit_file(
        repo,
        "messages/historical.md",
        "message_id: one-0042\nwriter: One\n",
        "historical message",
    )

    subprocess.check_call(
        ["git", "-C", str(repo), "checkout", "-qb", "bus/one-v2", base]
    )
    current_head = commit_file(
        repo,
        "messages/current.md",
        "message_id: one-0042\nwriter: One\n",
        "reuse historical id",
    )

    cutover = tmp_path / "cutover.json"
    cutover.write_text(
        json.dumps(
            {
                "planned_current_writer_lanes": {"one": "bus/one-v2"},
                "historical_writer_lanes": {
                    "one": {
                        "branch": "bus/one-v1",
                        "head_sha": historical_head,
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(m.WriterLaneError, match="DUPLICATE_NEW_MESSAGE_ID:one-0042"):
        m.validate_writer_lane_commit(
            repo,
            "refs/heads/bus/one-v2",
            current_head,
            topology,
            base=base,
            cutover_path=cutover,
        )
