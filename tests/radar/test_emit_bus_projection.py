import base64
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "radar_emit_bus_projection.py"
CURRENT_REF = "refs/heads/bus/one-v2"


def load_emitter():
    spec = importlib.util.spec_from_file_location("radar_emit_bus_projection", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


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
                    }
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


def make_repo(tmp_path: Path) -> tuple[Path, str, bytes]:
    repo = tmp_path / "lane"
    repo.mkdir()
    subprocess.check_call(["git", "-C", str(repo), "init", "-q"])
    subprocess.check_call(["git", "-C", str(repo), "config", "user.email", "test@example.com"])
    subprocess.check_call(["git", "-C", str(repo), "config", "user.name", "Test"])
    (repo / "messages").mkdir()
    (repo / "README.md").write_text("canonical inherited file\n", encoding="utf-8")
    subprocess.check_call(["git", "-C", str(repo), "add", "."])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "canonical cut"])

    content = b"# One -> Radar\n\nmessage_id: one-9999\nwriter: One\ncreated_at: 2026-09-02T20:00:00Z\n\nhello\n"
    (repo / "messages" / "0001.md").write_bytes(content)
    subprocess.check_call(["git", "-C", str(repo), "add", "messages/0001.md"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "message"])
    head = git(repo, "rev-parse", "HEAD")
    return repo, head, content


def collect(emitter, repo: Path, head: str, topology: Path, **limits):
    return emitter.collect_projection_batch(
        repo,
        repository="thebrazenbeard/chat-communication-bus",
        ref=CURRENT_REF,
        branch_head=head,
        topology_path=topology,
        **limits,
    )


def test_build_oidc_url_preserves_existing_query_and_sets_audience():
    emitter = load_emitter()
    url = emitter.build_oidc_url("https://oidc.example/token?foo=bar", "chat-communication-bus-supabase")
    assert "foo=bar" in url
    assert "audience=chat-communication-bus-supabase" in url


def test_resolve_base_commit_prefers_explicit_cli_base(tmp_path):
    emitter = load_emitter()
    event = tmp_path / "event.json"
    event.write_text(json.dumps({"before": "b" * 40}), encoding="utf-8")
    assert emitter.resolve_base_commit("a" * 40, event) == "a" * 40


def test_resolve_base_commit_recovers_github_push_before_for_legacy_workflow(tmp_path):
    emitter = load_emitter()
    event = tmp_path / "event.json"
    event.write_text(json.dumps({"before": "b" * 40}), encoding="utf-8")
    assert emitter.resolve_base_commit(None, event) == "b" * 40


def test_planned_successor_bootstrap_skips_provider_projection(tmp_path, capsys):
    emitter = load_emitter()
    topology, cutover = write_staged_topology_and_cutover(tmp_path)
    repo, head, _ = make_repo(tmp_path)
    rc = emitter.main(
        [
            "--repo-dir",
            str(repo),
            "--repository",
            "thebrazenbeard/chat-communication-bus",
            "--ref",
            CURRENT_REF,
            "--head",
            head,
            "--base",
            "0" * 40,
            "--topology",
            str(topology),
            "--cutover",
            str(cutover),
            "--bootstrap-main",
            head,
        ]
    )
    assert rc == 0
    assert "PLANNED_SUCCESSOR_BOOTSTRAP_SKIPPED" in capsys.readouterr().out


def test_collect_batch_carries_git_evidence_raw_bytes_and_lane_identity(tmp_path):
    emitter = load_emitter()
    topology = write_topology(tmp_path)
    repo, head, content = make_repo(tmp_path)
    batch = collect(emitter, repo, head, topology)
    assert batch["repository"] == "thebrazenbeard/chat-communication-bus"
    assert batch["ref"] == CURRENT_REF
    assert batch["branch_head"] == head
    assert batch["lane_identity"] == "one"
    assert len(batch["files"]) == 1
    item = batch["files"][0]
    assert item["path"] == "messages/0001.md"
    assert item["source_commit"] == head
    assert item["source_committed_at"]
    assert item["blob_sha"] == git(repo, "rev-parse", f"{head}:messages/0001.md")
    assert base64.b64decode(item["content_base64"]) == content
    assert "message_id" not in item
    assert "writer" not in item
    assert "body" not in item


def test_collect_batch_keeps_prior_message_source_commit_when_new_message_is_added(tmp_path):
    emitter = load_emitter()
    topology = write_topology(tmp_path)
    repo, first_head, _ = make_repo(tmp_path)
    second = b"# One -> Six\n\nmessage_id: one-10000\nwriter: One\ncreated_at: 2026-09-02T20:01:00Z\n\nsecond\n"
    (repo / "messages" / "0002.md").write_bytes(second)
    subprocess.check_call(["git", "-C", str(repo), "add", "messages/0002.md"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "second message"])
    current_head = git(repo, "rev-parse", "HEAD")
    batch = collect(emitter, repo, current_head, topology)
    by_path = {item["path"]: item for item in batch["files"]}
    assert by_path["messages/0001.md"]["source_commit"] == first_head
    assert by_path["messages/0002.md"]["source_commit"] == current_head


def test_collect_batch_rejects_shared_file_change_on_current_lane(tmp_path):
    emitter = load_emitter()
    topology = write_topology(tmp_path)
    repo, _, _ = make_repo(tmp_path)
    (repo / "README.md").write_text("writer changed this\n", encoding="utf-8")
    subprocess.check_call(["git", "-C", str(repo), "add", "README.md"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "bad shared change"])
    head = git(repo, "rev-parse", "HEAD")
    with pytest.raises(emitter.EmitterError, match="WRITER_LANE_PATH_FORBIDDEN:README.md"):
        collect(emitter, repo, head, topology)


def test_collect_batch_rejects_new_message_id_that_already_exists_in_parent(tmp_path):
    emitter = load_emitter()
    topology = write_topology(tmp_path)
    repo, _, _ = make_repo(tmp_path)
    duplicate = b"# One -> Six\n\nmessage_id: one-9999\nwriter: One\ncreated_at: 2026-09-02T20:01:00Z\n\nduplicate id\n"
    (repo / "messages" / "0002.md").write_bytes(duplicate)
    subprocess.check_call(["git", "-C", str(repo), "add", "messages/0002.md"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "duplicate"])
    head = git(repo, "rev-parse", "HEAD")
    with pytest.raises(emitter.EmitterError, match="DUPLICATE_NEW_MESSAGE_ID:one-9999"):
        collect(emitter, repo, head, topology)


def test_collect_batch_rejects_recovery_checkpoint_consuming_message_namespace(tmp_path):
    emitter = load_emitter()
    topology = write_topology(tmp_path)
    repo, _, _ = make_repo(tmp_path)
    checkpoint = b"# One numerical identity checkpoint\n\nmessage_id: one-10000\nwriter: One\nstatus: recovery-checkpoint\nintended_recipient: replacement-instance / coordinator recovery\n\nidentity hint\n"
    (repo / "messages" / "10000-one-numerical-identity-checkpoint.md").write_bytes(checkpoint)
    subprocess.check_call(["git", "-C", str(repo), "add", "messages/10000-one-numerical-identity-checkpoint.md"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "checkpoint"])
    head = git(repo, "rev-parse", "HEAD")
    with pytest.raises(emitter.EmitterError, match="RECOVERY_CHECKPOINT_MESSAGE_NAMESPACE"):
        collect(emitter, repo, head, topology)


def test_collect_batch_enforces_per_file_limit(tmp_path):
    emitter = load_emitter()
    topology = write_topology(tmp_path)
    repo, head, _ = make_repo(tmp_path)
    with pytest.raises(emitter.EmitterError, match="MESSAGE_FILE_TOO_LARGE"):
        collect(emitter, repo, head, topology, max_file_bytes=8)


def test_collect_batch_enforces_total_limit(tmp_path):
    emitter = load_emitter()
    topology = write_topology(tmp_path)
    repo, head, content = make_repo(tmp_path)
    with pytest.raises(emitter.EmitterError, match="BATCH_TOO_LARGE"):
        collect(emitter, repo, head, topology, max_total_bytes=len(content) - 1)


def test_collect_batch_rejects_unregistered_lookalike_lane(tmp_path):
    emitter = load_emitter()
    topology = write_topology(tmp_path)
    repo, head, _ = make_repo(tmp_path)
    with pytest.raises(emitter.EmitterError, match="UNREGISTERED_WRITER_LANE"):
        emitter.collect_projection_batch(
            repo,
            repository="thebrazenbeard/chat-communication-bus",
            ref="refs/heads/bus/one-v2-lookalike",
            branch_head=head,
            topology_path=topology,
        )
