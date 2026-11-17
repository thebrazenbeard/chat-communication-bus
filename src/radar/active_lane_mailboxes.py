"""Object-only currentness check for ACTIVE Bus writer-lane mailbox claims.

This is an audit, not writer-lane authorization or a mailbox reader. It never
checks out writer branches or opens message bodies; it only inspects Git paths.
"""

from __future__ import annotations

from pathlib import Path
import re
import subprocess

from .writer_lanes import load_writer_lanes


_SHA40 = re.compile(r"^[0-9a-f]{40}$")


class ActiveMailboxAuditError(ValueError):
    """A current ACTIVE topology claim was not structurally supported."""


def _git(repo: Path, *args: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=45,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ActiveMailboxAuditError("ACTIVE_LANE_GIT_UNAVAILABLE") from exc
    if result.returncode:
        # Keep remote diagnostic stderr private: it may contain an authenticated URL.
        raise ActiveMailboxAuditError("ACTIVE_LANE_GIT_FAILED")
    return result.stdout


def audit_active_lane_mailboxes(
    repo_dir: str | Path,
    topology_path: str | Path,
    *,
    remote: str = "origin",
    identity: str | None = None,
) -> dict[str, str]:
    """Require current remote Git tree paths under `messages/` for ACTIVE lanes.

    For each lane, confirm the advertised branch's exact remote SHA, fetch only
    its Git objects into FETCH_HEAD, and compare the resulting commit before
    inspecting paths. Never treat a matching branch name as a functioning
    mailbox or a grant of delivery/reader/effect authority.
    """
    repo = Path(repo_dir)
    lanes = load_writer_lanes(topology_path)
    if identity is not None:
        if identity not in lanes:
            raise ActiveMailboxAuditError(f"ACTIVE_LANE_NOT_REGISTERED:{identity}")
        lanes = {identity: lanes[identity]}

    passed: dict[str, str] = {}
    for name, lane in sorted(lanes.items()):
        ref = f"refs/heads/{lane.branch}"
        if not re.fullmatch(r"refs/heads/bus/[a-z0-9][a-z0-9_-]*-v[0-9]+", ref):
            raise ActiveMailboxAuditError(f"ACTIVE_LANE_REF_INVALID:{name}")
        lines = _git(repo, "ls-remote", "--heads", remote, ref).decode("utf-8", "strict").splitlines()
        exact = [line.split("\t", 1)[0] for line in lines if line.endswith(f"\t{ref}")]
        if len(exact) != 1 or not _SHA40.fullmatch(exact[0]):
            raise ActiveMailboxAuditError(f"ACTIVE_BRANCH_MISSING:{name}:{lane.branch}")
        expected_sha = exact[0]

        # Explicit source ref only: object fetch updates local FETCH_HEAD, not
        # the writer branch or any public/private remote ref.
        _git(repo, "fetch", "--quiet", "--no-tags", "--depth=1", remote, ref)
        fetched_sha = _git(repo, "rev-parse", "FETCH_HEAD").decode("ascii", "strict").strip()
        if fetched_sha != expected_sha:
            raise ActiveMailboxAuditError(f"ACTIVE_BRANCH_HEAD_MOVED:{name}:{lane.branch}")
        paths = _git(repo, "ls-tree", "-r", "-z", "--name-only", fetched_sha, "--", "messages")
        if not any(path.startswith(b"messages/") for path in paths.split(b"\0")):
            raise ActiveMailboxAuditError(f"ACTIVE_MAILBOX_MISSING:{name}:{lane.branch}:{fetched_sha}")
        passed[name] = fetched_sha
    return passed


__all__ = ["ActiveMailboxAuditError", "audit_active_lane_mailboxes"]
