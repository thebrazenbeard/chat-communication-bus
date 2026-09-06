from __future__ import annotations

import subprocess

from radar.trusted_reconciler import LocalGitRepository


def _git(repo, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def test_remote_tracking_writer_ref_is_read_without_local_branch_materialization(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "radar@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Radar Test"], check=True)

    (repo / "README.md").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
    head = _git(repo, "rev-parse", "HEAD")

    subprocess.run(
        ["git", "-C", str(repo), "update-ref", "refs/remotes/origin/bus/yin-v2", head],
        check=True,
    )

    adapter = LocalGitRepository(repo, use_remote_tracking_refs=True)
    assert adapter.branch_head("bus/yin-v2") == head
    assert subprocess.run(
        ["git", "-C", str(repo), "show-ref", "--verify", "--quiet", "refs/heads/bus/yin-v2"],
        check=False,
    ).returncode != 0
