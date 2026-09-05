from __future__ import annotations

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

    with pytest.raises(m.WriterLaneError, match="WRITER_LANE_MESSAGE_ID_DUPLICATE"):
        m.validate_writer_lane_commit(
            repo,
            "refs/heads/bus/one-v2",
            head,
            topology,
            base=first,
        )
