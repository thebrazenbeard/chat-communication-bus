from __future__ import annotations

import json
import subprocess

from tests.radar.test_emit_bus_projection import CURRENT_REF, git, load_emitter, write_topology


def _repo_with_cross_generation_reuse(tmp_path):
    repo = tmp_path / "lane"
    repo.mkdir()
    subprocess.check_call(["git", "-C", str(repo), "init", "-q"])
    subprocess.check_call(["git", "-C", str(repo), "config", "user.email", "test@example.com"])
    subprocess.check_call(["git", "-C", str(repo), "config", "user.name", "Test"])
    (repo / "messages").mkdir()
    (repo / "README.md").write_text("canonical inherited file\n", encoding="utf-8")
    subprocess.check_call(["git", "-C", str(repo), "add", "."])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "base"])
    base = git(repo, "rev-parse", "HEAD")

    subprocess.check_call(["git", "-C", str(repo), "checkout", "-qb", "bus/one-v1", base])
    (repo / "messages" / "historical.md").write_text(
        "message_id: one-0042\nwriter: One\n", encoding="utf-8"
    )
    subprocess.check_call(["git", "-C", str(repo), "add", "messages/historical.md"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "historical"])
    historical_head = git(repo, "rev-parse", "HEAD")

    subprocess.check_call(["git", "-C", str(repo), "checkout", "-qb", "bus/one-v2", base])
    (repo / "messages" / "current.md").write_text(
        "message_id: one-0042\nwriter: One\n", encoding="utf-8"
    )
    subprocess.check_call(["git", "-C", str(repo), "add", "messages/current.md"])
    subprocess.check_call(["git", "-C", str(repo), "commit", "-qm", "reuse historical id"])
    current_head = git(repo, "rev-parse", "HEAD")
    return repo, base, historical_head, current_head


def test_main_applies_cutover_history_before_provider_projection(tmp_path, monkeypatch, capsys):
    emitter = load_emitter()
    topology = write_topology(tmp_path)
    repo, base, historical_head, current_head = _repo_with_cross_generation_reuse(tmp_path)
    cutover = tmp_path / "cutover.json"
    cutover.write_text(
        json.dumps(
            {
                "planned_current_writer_lanes": {"one": "bus/one-v2"},
                "historical_writer_lanes": {
                    "one": {"branch": "bus/one-v1", "head_sha": historical_head}
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(emitter, "request_oidc_token", lambda audience: "token")
    monkeypatch.setattr(
        emitter,
        "post_projection_batch",
        lambda endpoint, token, batch: {
            "ok": True,
            "conflicts": 0,
            "projected": 1,
            "results": [{"result": "INSERTED"}],
        },
    )

    rc = emitter.main(
        [
            "--repo-dir",
            str(repo),
            "--repository",
            "thebrazenbeard/chat-communication-bus",
            "--ref",
            CURRENT_REF,
            "--head",
            current_head,
            "--base",
            base,
            "--topology",
            str(topology),
            "--cutover",
            str(cutover),
        ]
    )

    captured = capsys.readouterr()
    assert rc == 1
    assert "DUPLICATE_NEW_MESSAGE_ID:one-0042" in captured.err
