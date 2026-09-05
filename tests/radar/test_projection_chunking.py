from __future__ import annotations

import base64
import importlib.util
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "radar_emit_bus_projection.py"
CURRENT_REF = "refs/heads/bus/one-v2"


def load_emitter():
    spec = importlib.util.spec_from_file_location("radar_emit_bus_projection_chunking", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def make_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "lane"
    repo.mkdir()
    subprocess.check_call(["git", "-C", str(repo), "init", "-q"])
    subprocess.check_call(["git", "-C", str(repo), "config", "user.email", "chunking@example.com"])
    subprocess.check_call(["git", "-C", str(repo), "config", "user.name", "Chunking Test"])
    (repo / "messages").mkdir()
    (repo / "README.md").write_text("base\n", encoding="utf-8")
    subprocess.check_call(["git", "-C", str(repo), "add", "."])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "base"])
    return repo, git(repo, "rev-parse", "HEAD")


def write_topology(tmp_path: Path) -> Path:
    topology = tmp_path / "topology.json"
    topology.write_text(
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
    return topology


def add_messages(repo: Path, count: int, *, body_size: int = 4) -> str:
    body = "x" * body_size
    for index in range(count):
        (repo / "messages" / f"{index:04d}.md").write_text(
            "# One -> Radar\n\n"
            f"message_id: one-chunk-{index:04d}\n"
            "writer: One\n"
            "created_at: 2026-09-05T19:00:00Z\n\n"
            f"{body}\n",
            encoding="utf-8",
        )
    subprocess.check_call(["git", "-C", str(repo), "add", "messages"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", f"add {count} messages"])
    return git(repo, "rev-parse", "HEAD")


def _paths(batches: tuple[dict[str, object], ...]) -> list[str]:
    return [item["path"] for batch in batches for item in batch["files"]]


def _decoded_bytes(batch: dict[str, object]) -> int:
    return sum(len(base64.b64decode(item["content_base64"])) for item in batch["files"])


def test_501_message_push_is_split_losslessly_inside_edge_file_limit(tmp_path):
    emitter = load_emitter()
    repo, base = make_repo(tmp_path)
    head = add_messages(repo, 501)
    topology = write_topology(tmp_path)

    batches = emitter.collect_projection_batches(
        repo,
        repository="thebrazenbeard/chat-communication-bus",
        ref=CURRENT_REF,
        branch_head=head,
        base_commit=base,
        topology_path=topology,
        max_files=500,
    )

    assert len(batches) == 2
    assert all(len(batch["files"]) <= 500 for batch in batches)
    paths = _paths(batches)
    assert len(paths) == 501
    assert len(set(paths)) == 501
    assert paths == sorted(paths)
    assert all(batch["projection_chunk_count"] == 2 for batch in batches)
    assert [batch["projection_chunk_index"] for batch in batches] == [1, 2]


def test_projection_chunks_honor_total_decoded_byte_limit_without_dropping_files(tmp_path):
    emitter = load_emitter()
    repo, base = make_repo(tmp_path)
    head = add_messages(repo, 5, body_size=120)
    topology = write_topology(tmp_path)

    # First collect once with a generous limit so the test can derive a safe
    # threshold that requires more than one chunk while still fitting one file.
    logical = emitter.collect_projection_batches(
        repo,
        repository="thebrazenbeard/chat-communication-bus",
        ref=CURRENT_REF,
        branch_head=head,
        base_commit=base,
        topology_path=topology,
        max_files=500,
        max_total_bytes=10_000,
    )
    sizes = [len(base64.b64decode(item["content_base64"])) for item in logical[0]["files"]]
    limit = max(sizes) * 2

    batches = emitter.collect_projection_batches(
        repo,
        repository="thebrazenbeard/chat-communication-bus",
        ref=CURRENT_REF,
        branch_head=head,
        base_commit=base,
        topology_path=topology,
        max_files=500,
        max_total_bytes=limit,
    )

    assert len(batches) >= 3
    assert all(_decoded_bytes(batch) <= limit for batch in batches)
    assert len(_paths(batches)) == 5
    assert len(set(_paths(batches))) == 5


def test_main_posts_every_chunk_and_reports_combined_success(monkeypatch, tmp_path, capsys):
    emitter = load_emitter()
    monkeypatch.setattr(emitter, "planned_successor_bootstrap_identity", lambda *args, **kwargs: None)
    batches = (
        {"files": [{"path": "messages/a.md"}], "projection_chunk_index": 1, "projection_chunk_count": 2},
        {"files": [{"path": "messages/b.md"}], "projection_chunk_index": 2, "projection_chunk_count": 2},
    )
    monkeypatch.setattr(emitter, "collect_projection_batches", lambda *args, **kwargs: batches)
    monkeypatch.setattr(emitter, "request_oidc_token", lambda *args, **kwargs: "test-token")
    posted: list[dict[str, object]] = []

    def post(_endpoint, _token, batch):
        posted.append(batch)
        return {"ok": True, "projected": 1, "results": [{"path": batch["files"][0]["path"], "result": "INSERTED"}]}

    monkeypatch.setattr(emitter, "post_projection_batch", post)

    rc = emitter.main(
        [
            "--repo-dir", str(tmp_path),
            "--repository", "thebrazenbeard/chat-communication-bus",
            "--ref", CURRENT_REF,
            "--head", "1" * 40,
            "--base", "2" * 40,
            "--topology", str(tmp_path / "topology.json"),
            "--cutover", str(tmp_path / "cutover.json"),
        ]
    )

    assert rc == 0
    assert posted == list(batches)
    result = json.loads(capsys.readouterr().out)
    assert result["ok"] is True
    assert result["chunks"] == 2
    assert result["projected"] == 2
    assert [row["path"] for row in result["results"]] == ["messages/a.md", "messages/b.md"]


def test_main_stops_and_returns_failure_when_any_chunk_conflicts(monkeypatch, tmp_path):
    emitter = load_emitter()
    monkeypatch.setattr(emitter, "planned_successor_bootstrap_identity", lambda *args, **kwargs: None)
    batches = (
        {"files": [{"path": "messages/a.md"}], "projection_chunk_index": 1, "projection_chunk_count": 2},
        {"files": [{"path": "messages/b.md"}], "projection_chunk_index": 2, "projection_chunk_count": 2},
    )
    monkeypatch.setattr(emitter, "collect_projection_batches", lambda *args, **kwargs: batches)
    monkeypatch.setattr(emitter, "request_oidc_token", lambda *args, **kwargs: "test-token")
    calls = 0

    def post(_endpoint, _token, batch):
        nonlocal calls
        calls += 1
        if batch["projection_chunk_index"] == 2:
            return {"ok": True, "results": [{"path": "messages/b.md", "result": "CONFLICT"}]}
        return {"ok": True, "results": [{"path": "messages/a.md", "result": "INSERTED"}]}

    monkeypatch.setattr(emitter, "post_projection_batch", post)

    rc = emitter.main(
        [
            "--repo-dir", str(tmp_path),
            "--repository", "thebrazenbeard/chat-communication-bus",
            "--ref", CURRENT_REF,
            "--head", "1" * 40,
            "--base", "2" * 40,
            "--topology", str(tmp_path / "topology.json"),
            "--cutover", str(tmp_path / "cutover.json"),
        ]
    )

    assert rc == 1
    assert calls == 2
