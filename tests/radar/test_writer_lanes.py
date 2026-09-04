import importlib
import json
from pathlib import Path
import subprocess

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


def write_staged_topology_and_cutover(tmp_path: Path) -> tuple[Path, Path]:
    topology = tmp_path / "staged-topology.json"
    topology.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "required_writer_lanes": {
                    "one": {
                        "writer": "One",
                        "branch": "bus/one-v1",
                        "legacy_spelling": False,
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    cutover = tmp_path / "cutover.json"
    cutover.write_text(
        json.dumps(
            {
                "status": "PRE_MERGE_PLANNED",
                "successor_branches_created": False,
                "topology_switched": False,
                "planned_current_writer_lanes": {"one": "bus/one-v2"},
            }
        ),
        encoding="utf-8",
    )
    return topology, cutover


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def make_lane_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "lane"
    repo.mkdir()
    subprocess.check_call(["git", "-C", str(repo), "init", "-q"])
    subprocess.check_call(["git", "-C", str(repo), "config", "user.email", "test@example.com"])
    subprocess.check_call(["git", "-C", str(repo), "config", "user.name", "Test"])
    (repo / "messages").mkdir()
    (repo / "README.md").write_text("canonical inherited file\n", encoding="utf-8")
    subprocess.check_call(["git", "-C", str(repo), "add", "."])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "base"])
    return repo


def commit_file(repo: Path, path: str, content: str, message: str) -> str:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    subprocess.check_call(["git", "-C", str(repo), "add", "-A"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", message])
    return git(repo, "rev-parse", "HEAD")


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


def test_current_lane_may_only_add_new_message(tmp_path):
    m = _writer_lanes()
    topology = write_topology(tmp_path)
    repo = make_lane_repo(tmp_path)
    head = commit_file(repo, "messages/0001.md", "message_id: one-0001\nwriter: One\n", "message")
    assert m.validate_writer_lane_commit(repo, "refs/heads/bus/one-v2", head, topology) == "one"


def test_current_lane_rejects_shared_file_change(tmp_path):
    m = _writer_lanes()
    topology = write_topology(tmp_path)
    repo = make_lane_repo(tmp_path)
    head = commit_file(repo, "README.md", "writer changed this\n", "bad")
    with pytest.raises(m.WriterLaneError, match="WRITER_LANE_PATH_FORBIDDEN:README.md"):
        m.validate_writer_lane_commit(repo, "refs/heads/bus/one-v2", head, topology)


def test_current_lane_rejects_modified_existing_message(tmp_path):
    m = _writer_lanes()
    topology = write_topology(tmp_path)
    repo = make_lane_repo(tmp_path)
    first = commit_file(repo, "messages/0001.md", "message_id: one-0001\nwriter: One\n", "message")
    assert m.validate_writer_lane_commit(repo, "refs/heads/bus/one-v2", first, topology) == "one"
    head = commit_file(repo, "messages/0001.md", "rewritten\n", "rewrite")
    with pytest.raises(m.WriterLaneError, match="WRITER_LANE_MESSAGE_NOT_APPEND_ONLY:messages/0001.md"):
        m.validate_writer_lane_commit(repo, "refs/heads/bus/one-v2", head, topology)


def test_current_lane_rejects_deleted_existing_message(tmp_path):
    m = _writer_lanes()
    topology = write_topology(tmp_path)
    repo = make_lane_repo(tmp_path)
    first = commit_file(repo, "messages/0001.md", "message_id: one-0001\nwriter: One\n", "message")
    assert m.validate_writer_lane_commit(repo, "refs/heads/bus/one-v2", first, topology) == "one"
    (repo / "messages" / "0001.md").unlink()
    subprocess.check_call(["git", "-C", str(repo), "add", "-A"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "delete"])
    head = git(repo, "rev-parse", "HEAD")
    with pytest.raises(m.WriterLaneError, match="WRITER_LANE_MESSAGE_NOT_APPEND_ONLY:messages/0001.md"):
        m.validate_writer_lane_commit(repo, "refs/heads/bus/one-v2", head, topology)


def test_multi_commit_push_rejects_earlier_shared_change_even_if_head_is_message(tmp_path):
    m = _writer_lanes()
    topology = write_topology(tmp_path)
    repo = make_lane_repo(tmp_path)
    base = git(repo, "rev-parse", "HEAD")
    commit_file(repo, "README.md", "forbidden intermediate change\n", "bad intermediate")
    head = commit_file(repo, "messages/0001.md", "message_id: one-0001\nwriter: One\n", "clean-looking head")
    with pytest.raises(m.WriterLaneError, match="WRITER_LANE_PATH_FORBIDDEN:README.md"):
        m.validate_writer_lane_commit(
            repo,
            "refs/heads/bus/one-v2",
            head,
            topology,
            base=base,
        )


def test_current_lane_rejects_declared_writer_mismatch(tmp_path):
    m = _writer_lanes()
    topology = write_topology(tmp_path)
    repo = make_lane_repo(tmp_path)
    head = commit_file(repo, "messages/0001.md", "message_id: one-0001\nwriter: Two\n", "spoofed writer")
    with pytest.raises(m.WriterLaneError, match="WRITER_LANE_WRITER_MISMATCH:messages/0001.md"):
        m.validate_writer_lane_commit(repo, "refs/heads/bus/one-v2", head, topology)


def test_current_lane_accepts_wrapped_matching_writer(tmp_path):
    m = _writer_lanes()
    topology = write_topology(tmp_path)
    repo = make_lane_repo(tmp_path)
    head = commit_file(repo, "messages/0001.md", "message_id: one-0001\nwriter: `One`\n", "wrapped writer")
    assert m.validate_writer_lane_commit(repo, "refs/heads/bus/one-v2", head, topology) == "one"


def test_planned_successor_branch_creation_accepts_exact_main_bootstrap_only(tmp_path):
    m = _writer_lanes()
    topology, cutover = write_staged_topology_and_cutover(tmp_path)
    repo = make_lane_repo(tmp_path)
    head = git(repo, "rev-parse", "HEAD")
    assert m.validate_writer_lane_commit(
        repo,
        "refs/heads/bus/one-v2",
        head,
        topology,
        base="0" * 40,
        cutover_path=cutover,
        bootstrap_main=head,
    ) == "one"


def test_planned_successor_bootstrap_rejects_noncanonical_head(tmp_path):
    m = _writer_lanes()
    topology, cutover = write_staged_topology_and_cutover(tmp_path)
    repo = make_lane_repo(tmp_path)
    head = git(repo, "rev-parse", "HEAD")
    with pytest.raises(m.WriterLaneError, match="WRITER_LANE_BOOTSTRAP_MAIN_MISMATCH"):
        m.validate_writer_lane_commit(
            repo,
            "refs/heads/bus/one-v2",
            head,
            topology,
            base="0" * 40,
            cutover_path=cutover,
            bootstrap_main="f" * 40,
        )


def test_planned_successor_cannot_accept_messages_before_topology_switch(tmp_path):
    m = _writer_lanes()
    topology, cutover = write_staged_topology_and_cutover(tmp_path)
    repo = make_lane_repo(tmp_path)
    base = git(repo, "rev-parse", "HEAD")
    head = commit_file(repo, "messages/0001.md", "message_id: one-0001\nwriter: One\n", "too early")
    with pytest.raises(m.WriterLaneError, match="UNREGISTERED_WRITER_LANE"):
        m.validate_writer_lane_commit(
            repo,
            "refs/heads/bus/one-v2",
            head,
            topology,
            base=base,
            cutover_path=cutover,
            bootstrap_main=base,
        )
