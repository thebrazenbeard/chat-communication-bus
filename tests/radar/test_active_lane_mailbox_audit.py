"""A current ACTIVE topology claim requires observed Git mailbox structure."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess

import pytest

from radar.active_lane_mailboxes import ActiveMailboxAuditError, audit_active_lane_mailboxes


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def local_remote(tmp_path: Path, *, with_mailbox: bool) -> tuple[Path, Path]:
    remote = tmp_path / "remote.git"
    source = tmp_path / "source"
    subprocess.check_call(["git", "init", "--bare", "-q", str(remote)])
    subprocess.check_call(["git", "init", "-q", "-b", "main", str(source)])
    git(source, "config", "user.email", "audit@example.test")
    git(source, "config", "user.name", "Audit")
    (source / "README.md").write_text("branch inherited source\n", encoding="utf-8")
    git(source, "add", ".")
    git(source, "commit", "-qm", "initial")
    git(source, "branch", "bus/vera-v2")
    if with_mailbox:
        git(source, "checkout", "-q", "bus/vera-v2")
        mailbox = source / "messages"
        mailbox.mkdir()
        (mailbox / ".gitkeep").write_text("\n", encoding="utf-8")
        git(source, "add", "messages/.gitkeep")
        git(source, "commit", "-qm", "mailbox structure")
    git(source, "remote", "add", "origin", str(remote))
    git(source, "push", "-q", "origin", "bus/vera-v2")
    git(source, "checkout", "-q", "main")
    return source, remote


def topology(tmp_path: Path) -> Path:
    path = tmp_path / "topology.json"
    path.write_text(
        json.dumps({
            "required_writer_lanes": {
                "vera": {"writer": "Vera", "branch": "bus/vera-v2", "lifecycle": "ACTIVE"},
                "parallax": {"writer": "Parallax", "branch": "bus/parallax-v1", "lifecycle": "REGISTERED_INERT"},
            }
        }),
        encoding="utf-8",
    )
    return path


def test_active_named_branch_without_mailbox_fails_with_exact_head(tmp_path):
    repo, _remote = local_remote(tmp_path, with_mailbox=False)
    expected = git(repo, "rev-parse", "refs/heads/bus/vera-v2")
    with pytest.raises(ActiveMailboxAuditError, match=f"ACTIVE_MAILBOX_MISSING:vera:bus/vera-v2:{expected}"):
        audit_active_lane_mailboxes(repo, topology(tmp_path), remote="origin", identity="vera")


def test_real_git_mailbox_structure_passes_without_checkout_or_branch_update(tmp_path):
    repo, _remote = local_remote(tmp_path, with_mailbox=True)
    before = git(repo, "rev-parse", "HEAD")
    found = audit_active_lane_mailboxes(repo, topology(tmp_path), remote="origin", identity="vera")
    assert found == {"vera": git(repo, "rev-parse", "refs/heads/bus/vera-v2")}
    assert git(repo, "rev-parse", "HEAD") == before


def test_inert_registration_is_not_implicitly_audited_or_activated(tmp_path):
    repo, _remote = local_remote(tmp_path, with_mailbox=True)
    assert set(audit_active_lane_mailboxes(repo, topology(tmp_path), remote="origin")) == {"vera"}
    with pytest.raises(ActiveMailboxAuditError, match="ACTIVE_LANE_NOT_REGISTERED:parallax"):
        audit_active_lane_mailboxes(repo, topology(tmp_path), remote="origin", identity="parallax")


def test_missing_remote_active_lane_fails_closed(tmp_path):
    repo, _remote = local_remote(tmp_path, with_mailbox=False)
    git(repo, "push", "-q", "origin", ":bus/vera-v2")
    with pytest.raises(ActiveMailboxAuditError, match="ACTIVE_BRANCH_MISSING:vera:bus/vera-v2"):
        audit_active_lane_mailboxes(repo, topology(tmp_path), remote="origin", identity="vera")
