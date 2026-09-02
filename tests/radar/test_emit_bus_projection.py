import base64
import importlib.util
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "radar_emit_bus_projection.py"


def load_emitter():
    spec = importlib.util.spec_from_file_location("radar_emit_bus_projection", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def make_repo(tmp_path: Path) -> tuple[Path, str, bytes]:
    repo = tmp_path / "lane"
    repo.mkdir()
    subprocess.check_call(["git", "-C", str(repo), "init", "-q"])
    subprocess.check_call(["git", "-C", str(repo), "config", "user.email", "test@example.com"])
    subprocess.check_call(["git", "-C", str(repo), "config", "user.name", "Test"])
    (repo / "messages").mkdir()
    content = b"# One -> Radar\n\nmessage_id: one-9999\nwriter: One\ncreated_at: 2026-09-02T20:00:00Z\n\nhello\n"
    (repo / "messages" / "0001.md").write_bytes(content)
    (repo / "README.md").write_text("ignore me")
    subprocess.check_call(["git", "-C", str(repo), "add", "."])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "seed"])
    head = git(repo, "rev-parse", "HEAD")
    return repo, head, content


def test_build_oidc_url_preserves_existing_query_and_sets_audience():
    emitter = load_emitter()
    url = emitter.build_oidc_url("https://oidc.example/token?foo=bar", "chat-communication-bus-supabase")
    assert "foo=bar" in url
    assert "audience=chat-communication-bus-supabase" in url


def test_collect_batch_carries_git_evidence_and_raw_bytes_only(tmp_path):
    emitter = load_emitter()
    repo, head, content = make_repo(tmp_path)
    batch = emitter.collect_projection_batch(
        repo,
        repository="thebrazenbeard/chat-communication-bus",
        ref="refs/heads/bus/one-v1",
        branch_head=head,
    )
    assert batch["repository"] == "thebrazenbeard/chat-communication-bus"
    assert batch["ref"] == "refs/heads/bus/one-v1"
    assert batch["branch_head"] == head
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


def test_collect_batch_uses_last_touch_commit_not_current_unrelated_head(tmp_path):
    emitter = load_emitter()
    repo, first_head, _ = make_repo(tmp_path)
    (repo / "README.md").write_text("unrelated change")
    subprocess.check_call(["git", "-C", str(repo), "add", "README.md"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "unrelated"])
    current_head = git(repo, "rev-parse", "HEAD")
    assert current_head != first_head
    batch = emitter.collect_projection_batch(
        repo,
        repository="thebrazenbeard/chat-communication-bus",
        ref="refs/heads/bus/one-v1",
        branch_head=current_head,
    )
    assert batch["files"][0]["source_commit"] == first_head


def test_collect_batch_rejects_new_message_id_that_already_exists_in_parent(tmp_path):
    emitter = load_emitter()
    repo, _, _ = make_repo(tmp_path)
    duplicate = b"# One -> Six\n\nmessage_id: one-9999\nwriter: One\ncreated_at: 2026-09-02T20:01:00Z\n\nduplicate id\n"
    (repo / "messages" / "0002.md").write_bytes(duplicate)
    subprocess.check_call(["git", "-C", str(repo), "add", "messages/0002.md"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "duplicate"])
    head = git(repo, "rev-parse", "HEAD")

    with pytest.raises(emitter.EmitterError, match="DUPLICATE_NEW_MESSAGE_ID:one-9999"):
        emitter.collect_projection_batch(
            repo,
            repository="thebrazenbeard/chat-communication-bus",
            ref="refs/heads/bus/one-v1",
            branch_head=head,
        )


def test_collect_batch_tolerates_preexisting_duplicate_ids_when_head_adds_no_message(tmp_path):
    emitter = load_emitter()
    repo, _, _ = make_repo(tmp_path)
    duplicate = b"# One -> Six\n\nmessage_id: one-9999\nwriter: One\ncreated_at: 2026-09-02T20:01:00Z\n\nhistorical duplicate\n"
    (repo / "messages" / "0002.md").write_bytes(duplicate)
    subprocess.check_call(["git", "-C", str(repo), "add", "messages/0002.md"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "historical duplicate"])
    (repo / "README.md").write_text("non-message change")
    subprocess.check_call(["git", "-C", str(repo), "add", "README.md"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "unrelated"])
    head = git(repo, "rev-parse", "HEAD")

    batch = emitter.collect_projection_batch(
        repo,
        repository="thebrazenbeard/chat-communication-bus",
        ref="refs/heads/bus/one-v1",
        branch_head=head,
    )
    assert len(batch["files"]) == 2


def test_collect_batch_enforces_per_file_limit(tmp_path):
    emitter = load_emitter()
    repo, head, _ = make_repo(tmp_path)
    with pytest.raises(emitter.EmitterError, match="MESSAGE_FILE_TOO_LARGE"):
        emitter.collect_projection_batch(
            repo,
            repository="thebrazenbeard/chat-communication-bus",
            ref="refs/heads/bus/one-v1",
            branch_head=head,
            max_file_bytes=8,
        )


def test_collect_batch_enforces_total_limit(tmp_path):
    emitter = load_emitter()
    repo, head, content = make_repo(tmp_path)
    with pytest.raises(emitter.EmitterError, match="BATCH_TOO_LARGE"):
        emitter.collect_projection_batch(
            repo,
            repository="thebrazenbeard/chat-communication-bus",
            ref="refs/heads/bus/one-v1",
            branch_head=head,
            max_total_bytes=len(content) - 1,
        )
