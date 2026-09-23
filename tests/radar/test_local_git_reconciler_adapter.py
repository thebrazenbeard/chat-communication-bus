from __future__ import annotations

import subprocess

from radar.trusted_reconciler import LocalGitRepository, ReconcileError


def _git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def test_local_git_adapter_reads_ordered_ancestry_without_executing_branch_files(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "radar@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Radar Test"], check=True)

    (repo / "README.md").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
    base = _git(repo, "rev-parse", "HEAD")

    subprocess.run(["git", "-C", str(repo), "switch", "-qc", "bus/yin-v2"], check=True)
    (repo / "untrusted.py").write_text("raise RuntimeError('must never execute')\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "untrusted.py"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "message one"], check=True)
    first = _git(repo, "rev-parse", "HEAD")
    (repo / "data.txt").write_text("two\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "data.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "message two"], check=True)
    head = _git(repo, "rev-parse", "HEAD")

    adapter = LocalGitRepository(repo)
    assert adapter.branch_head("bus/yin-v2") == head
    assert adapter.is_ancestor(base, head) is True
    assert adapter.is_ancestor(head, base) is False
    assert adapter.commits_between(base, head) == (first, head)


def test_local_git_adapter_fails_closed_for_missing_branch(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)

    adapter = LocalGitRepository(repo)
    try:
        adapter.branch_head("bus/missing-v1")
    except ReconcileError as exc:
        assert str(exc) == "MISSING_WRITER_BRANCH"
    else:
        raise AssertionError("missing branch did not fail closed")
