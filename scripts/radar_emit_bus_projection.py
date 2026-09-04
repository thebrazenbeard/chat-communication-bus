#!/usr/bin/env python3
"""Emit a Git-evidenced Bus mailbox batch to Radar's Supabase projection.

The emitter transports tracked Git objects plus provenance to the trusted Edge
Function. Before transport it enforces local append-only invariants:

* the source ref must be the topology-registered current lane for exactly one
  logical identity and every commit in the observed push range may only add
  message files;
* a newly added message file may not reuse a message_id that already existed in
  its parent mailbox (or another newly added file in the same commit);
* recovery checkpoints are continuity artifacts, not Bus messages, and may not
  consume the ordinary message_id namespace.

Historical collisions remain readable/projectable and are not retroactively
rejected.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen


# Existing v1 writer-lane workflows execute this script directly from a separate
# `control/` checkout without installing the package. Prefer the sibling source
# tree so post-merge control code remains executable during the zero-gap cutover.
_CONTROL_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _CONTROL_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from radar.writer_lanes import WriterLaneError, validate_writer_lane_commit


DEFAULT_AUDIENCE = "chat-communication-bus-supabase"
DEFAULT_ENDPOINT = "https://klmbpaigzeguvnpccqzz.supabase.co/functions/v1/github-bus-ingest"
DEFAULT_MAX_FILE_BYTES = 512 * 1024
DEFAULT_MAX_TOTAL_BYTES = 5 * 1024 * 1024
DEFAULT_TOPOLOGY = _CONTROL_ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json"
_ZERO_SHA = "0" * 40
_SHA_RE = re.compile(r"^[0-9a-fA-F]{40}$")
_MESSAGE_ID_RE = re.compile(r"(?mi)^message_id\s*:\s*(?P<value>.+?)\s*$")
_STATUS_RE = re.compile(r"(?mi)^status\s*:\s*(?P<value>.+?)\s*$")


class EmitterError(RuntimeError):
    pass


def _git(repo_dir: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo_dir), *args],
            text=True,
            stderr=subprocess.PIPE,
        ).strip()
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() if exc.stderr else str(exc)
        raise EmitterError(f"GIT_COMMAND_FAILED:{detail}") from exc


def _git_bytes(repo_dir: Path, *args: str) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo_dir), *args],
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.decode("utf-8", errors="replace").strip() if exc.stderr else str(exc)
        raise EmitterError(f"GIT_COMMAND_FAILED:{detail}") from exc


def build_oidc_url(base_url: str, audience: str = DEFAULT_AUDIENCE) -> str:
    parts = urlsplit(base_url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query["audience"] = audience
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def resolve_base_commit(
    explicit_base: str | None,
    event_path: str | Path | None = None,
) -> str | None:
    """Resolve the pushed range base, preferring explicit successor-workflow input.

    Historical v1 workflows do not pass ``--base``. On GitHub Actions, recover
    the same authoritative push ``before`` SHA from ``GITHUB_EVENT_PATH`` so
    those lanes receive full-range validation during the staged migration.
    """
    if explicit_base:
        return explicit_base

    raw_path = event_path if event_path is not None else os.environ.get("GITHUB_EVENT_PATH")
    if not raw_path:
        return None

    try:
        payload = json.loads(Path(raw_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EmitterError("GITHUB_EVENT_INVALID") from exc

    before = payload.get("before") if isinstance(payload, dict) else None
    if before is None:
        return None
    if not isinstance(before, str) or not _SHA_RE.fullmatch(before):
        raise EmitterError("GITHUB_EVENT_BEFORE_INVALID")
    return before


def _tracked_message_paths(repo_dir: Path) -> list[str]:
    raw = subprocess.check_output(
        ["git", "-C", str(repo_dir), "ls-files", "-z", "--", "messages/*.md"],
        stderr=subprocess.PIPE,
    )
    return sorted(path.decode("utf-8") for path in raw.split(b"\0") if path)


def _unwrap_scalar(value: str) -> str:
    text = value.strip()
    for left, right in (("`", "`"), ('"', '"'), ("'", "'")):
        if len(text) >= 2 and text.startswith(left) and text.endswith(right):
            return text[1:-1].strip()
    return text


def _extract_scalar(content: bytes, pattern: re.Pattern[str]) -> str | None:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return None
    match = pattern.search(text)
    if not match:
        return None
    value = _unwrap_scalar(match.group("value"))
    return value or None


def _extract_message_id(content: bytes) -> str | None:
    return _extract_scalar(content, _MESSAGE_ID_RE)


def _extract_status(content: bytes) -> str | None:
    return _extract_scalar(content, _STATUS_RE)


def _paths_at_ref(repo_dir: Path, ref: str) -> list[str]:
    raw = _git_bytes(repo_dir, "ls-tree", "-r", "-z", "--name-only", ref, "--", "messages")
    return sorted(path.decode("utf-8") for path in raw.split(b"\0") if path.endswith(b".md"))


def _added_message_paths(repo_dir: Path, parent: str, head: str) -> list[str]:
    raw = _git_bytes(
        repo_dir,
        "diff-tree",
        "--no-commit-id",
        "--name-only",
        "--diff-filter=A",
        "-r",
        "-z",
        parent,
        head,
        "--",
        "messages",
    )
    return sorted(path.decode("utf-8") for path in raw.split(b"\0") if path.endswith(b".md"))


def _validate_new_message_ids(repo_dir: Path, head: str) -> None:
    try:
        parent = _git(repo_dir, "rev-parse", f"{head}^")
    except EmitterError:
        return

    added_paths = _added_message_paths(repo_dir, parent, head)
    if not added_paths:
        return

    prior_ids: set[str] = set()
    for path in _paths_at_ref(repo_dir, parent):
        message_id = _extract_message_id(_git_bytes(repo_dir, "show", f"{parent}:{path}"))
        if message_id:
            prior_ids.add(message_id)

    added_ids: set[str] = set()
    for path in added_paths:
        content = _git_bytes(repo_dir, "show", f"{head}:{path}")
        message_id = _extract_message_id(content)
        status = (_extract_status(content) or "").strip().lower()

        if status == "recovery-checkpoint" and message_id:
            raise EmitterError(f"RECOVERY_CHECKPOINT_MESSAGE_NAMESPACE:{path}")

        if not message_id:
            continue
        if message_id in prior_ids or message_id in added_ids:
            raise EmitterError(f"DUPLICATE_NEW_MESSAGE_ID:{message_id}:{path}")
        added_ids.add(message_id)


def _push_commits(repo_dir: Path, head: str, base: str | None) -> list[str]:
    if not base or base == _ZERO_SHA:
        return [head]
    return [line for line in _git(repo_dir, "rev-list", "--reverse", f"{base}..{head}").splitlines() if line]


def collect_projection_batch(
    repo_dir: str | Path,
    *,
    repository: str,
    ref: str,
    branch_head: str,
    base_commit: str | None = None,
    topology_path: str | Path = DEFAULT_TOPOLOGY,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
) -> dict[str, object]:
    repo = Path(repo_dir)
    if not repo.is_dir():
        raise EmitterError("REPO_DIR_MISSING")

    try:
        lane_identity = validate_writer_lane_commit(
            repo,
            ref,
            branch_head,
            topology_path,
            base=base_commit,
        )
    except WriterLaneError as exc:
        raise EmitterError(str(exc)) from exc

    for commit in _push_commits(repo, branch_head, base_commit):
        _validate_new_message_ids(repo, commit)

    files: list[dict[str, object]] = []
    total = 0
    for path in _tracked_message_paths(repo):
        file_path = repo / path
        content = file_path.read_bytes()
        if len(content) > max_file_bytes:
            raise EmitterError(f"MESSAGE_FILE_TOO_LARGE:{path}")
        total += len(content)
        if total > max_total_bytes:
            raise EmitterError("BATCH_TOO_LARGE")

        source_commit = _git(repo, "log", "-1", "--format=%H", "--", path)
        source_committed_at = _git(repo, "log", "-1", "--format=%cI", "--", path)
        if not source_commit or not source_committed_at:
            raise EmitterError(f"MESSAGE_SOURCE_COMMIT_MISSING:{path}")
        blob_sha = _git(repo, "rev-parse", f"{branch_head}:{path}")

        files.append(
            {
                "path": path,
                "source_commit": source_commit,
                "source_committed_at": source_committed_at,
                "blob_sha": blob_sha,
                "content_base64": base64.b64encode(content).decode("ascii"),
            }
        )

    return {
        "projection_version": 1,
        "repository": repository,
        "ref": ref,
        "branch_head": branch_head,
        "lane_identity": lane_identity,
        "files": files,
    }


def request_oidc_token(audience: str = DEFAULT_AUDIENCE) -> str:
    request_url = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL", "")
    request_token = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "")
    if not request_url or not request_token:
        raise EmitterError("GITHUB_OIDC_ENV_MISSING")

    req = Request(
        build_oidc_url(request_url, audience),
        headers={"Authorization": f"Bearer {request_token}", "Accept": "application/json"},
    )
    with urlopen(req, timeout=20) as response:
        data = json.loads(response.read().decode("utf-8"))
    token = data.get("value")
    if not isinstance(token, str) or not token:
        raise EmitterError("GITHUB_OIDC_TOKEN_MISSING")
    return token


def post_projection_batch(endpoint: str, oidc_token: str, batch: dict[str, object]) -> dict[str, object]:
    body = json.dumps(batch, sort_keys=True, separators=(",", ":")).encode("utf-8")
    req = Request(
        endpoint,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {oidc_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "radar-bus-projection-v1",
        },
    )
    try:
        with urlopen(req, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise EmitterError(f"PROJECTION_POST_FAILED:{exc}") from exc
    if not isinstance(result, dict):
        raise EmitterError("PROJECTION_RESPONSE_INVALID")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-dir", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--base")
    parser.add_argument("--topology", default=str(DEFAULT_TOPOLOGY))
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--audience", default=DEFAULT_AUDIENCE)
    args = parser.parse_args(argv)

    try:
        base_commit = resolve_base_commit(args.base)
        batch = collect_projection_batch(
            args.repo_dir,
            repository=args.repository,
            ref=args.ref,
            branch_head=args.head,
            base_commit=base_commit,
            topology_path=args.topology,
        )
        token = request_oidc_token(args.audience)
        result = post_projection_batch(args.endpoint, token, batch)
    except EmitterError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, sort_keys=True))
    conflicts = result.get("conflicts", 0)
    return 1 if isinstance(conflicts, int) and conflicts > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
