#!/usr/bin/env python3
"""Emit a Git-evidenced Bus mailbox batch to Radar's Supabase projection.

The emitter transports tracked Git objects plus provenance to the trusted Edge
Function. Before transport it enforces one local append-only invariant: a newly
added message file may not reuse a message_id that already existed in its parent
mailbox (or another newly added file in the same commit). Historical collisions
remain readable/projectable and are not retroactively rejected.
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


DEFAULT_AUDIENCE = "chat-communication-bus-supabase"
DEFAULT_ENDPOINT = "https://klmbpaigzeguvnpccqzz.supabase.co/functions/v1/github-bus-ingest"
DEFAULT_MAX_FILE_BYTES = 512 * 1024
DEFAULT_MAX_TOTAL_BYTES = 5 * 1024 * 1024
_MESSAGE_ID_RE = re.compile(r"(?mi)^message_id\s*:\s*(?P<value>.+?)\s*$")


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


def _extract_message_id(content: bytes) -> str | None:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return None
    match = _MESSAGE_ID_RE.search(text)
    if not match:
        return None
    value = _unwrap_scalar(match.group("value"))
    return value or None


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
        message_id = _extract_message_id(_git_bytes(repo_dir, "show", f"{head}:{path}"))
        if not message_id:
            continue
        if message_id in prior_ids or message_id in added_ids:
            raise EmitterError(f"DUPLICATE_NEW_MESSAGE_ID:{message_id}:{path}")
        added_ids.add(message_id)


def collect_projection_batch(
    repo_dir: str | Path,
    *,
    repository: str,
    ref: str,
    branch_head: str,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
) -> dict[str, object]:
    repo = Path(repo_dir)
    if not repo.is_dir():
        raise EmitterError("REPO_DIR_MISSING")

    observed_head = _git(repo, "rev-parse", "HEAD")
    if observed_head != branch_head:
        raise EmitterError("BRANCH_HEAD_MISMATCH")

    _validate_new_message_ids(repo, branch_head)

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
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--audience", default=DEFAULT_AUDIENCE)
    args = parser.parse_args(argv)

    try:
        batch = collect_projection_batch(
            args.repo_dir,
            repository=args.repository,
            ref=args.ref,
            branch_head=args.head,
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
