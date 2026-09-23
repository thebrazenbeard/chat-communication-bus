from __future__ import annotations

import base64
import subprocess

from radar.central_projection import collect_projection_files


def _git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def test_collect_projection_files_reads_exact_added_commit_blob(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "radar@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Radar Test"], check=True)

    (repo / "README.md").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)

    messages = repo / "messages"
    messages.mkdir()
    content = b"message_id: yin-0001\nwriter: Yin\n\nhello\n"
    (messages / "yin-0001.md").write_bytes(content)
    subprocess.run(["git", "-C", str(repo), "add", "messages/yin-0001.md"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "message"], check=True)
    commit = _git(repo, "rev-parse", "HEAD")

    files = collect_projection_files(repo, (commit,))
    assert len(files) == 1
    item = files[0]
    assert item["path"] == "messages/yin-0001.md"
    assert item["source_commit"] == commit
    assert item["blob_sha"] == _git(repo, "rev-parse", f"{commit}:messages/yin-0001.md")
    assert base64.b64decode(item["content_base64"]) == content
    assert item["content_bytes"] == len(content)
