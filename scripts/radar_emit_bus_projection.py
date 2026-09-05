#!/usr/bin/env python3
"""Emit Git-evidenced Bus message deltas to Radar's provider projection.

The emitter transports immutable Git objects plus provenance. It validates the
observed writer-lane push before transport, projects exact added-message deltas
when a push base is available, and splits oversized deltas into deterministic
provider-safe chunks instead of truncating or replaying an entire mailbox.
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


_CONTROL_ROOT = Path(__file__).resolve().parents[1]
_SRC_ROOT = _CONTROL_ROOT / "src"
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from radar.writer_lanes import (
    WriterLaneError,
    planned_successor_bootstrap_identity,
    validate_writer_lane_commit,
)


DEFAULT_AUDIENCE = "chat-communication-bus-supabase"
DEFAULT_ENDPOINT = "https://klmbpaigzeguvnpccqzz.supabase.co/functions/v1/github-bus-ingest"
DEFAULT_MAX_FILES = 500
DEFAULT_MAX_FILE_BYTES = 512 * 1024
DEFAULT_MAX_TOTAL_BYTES = 5 * 1024 * 1024
DEFAULT_TOPOLOGY = _CONTROL_ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json"
DEFAULT_CUTOVER = _CONTROL_ROOT / "architecture" / "contracts" / "RADAR_WRITER_LANE_V2_CUTOVER.json"
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
    """Resolve the observed push base, preferring explicit workflow input."""
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


def _added_message_paths_for_commits(repo_dir: Path, commits: list[str]) -> list[str]:
    paths: set[str] = set()
    for commit in commits:
        try:
            parent = _git(repo_dir, "rev-parse", f"{commit}^")
        except EmitterError:
            continue
        paths.update(_added_message_paths(repo_dir, parent, commit))
    return sorted(paths)


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
    return [
        line
        for line in _git(repo_dir, "rev-list", "--reverse", f"{base}..{head}").splitlines()
        if line
    ]


def _validate_limits(max_files: int, max_file_bytes: int, max_total_bytes: int) -> None:
    if type(max_files) is not int or max_files <= 0:
        raise EmitterError("INVALID_MAX_FILES")
    if type(max_file_bytes) is not int or max_file_bytes <= 0:
        raise EmitterError("INVALID_MAX_FILE_BYTES")
    if type(max_total_bytes) is not int or max_total_bytes <= 0:
        raise EmitterError("INVALID_MAX_TOTAL_BYTES")


def _collect_projection_source(
    repo_dir: str | Path,
    *,
    repository: str,
    ref: str,
    branch_head: str,
    base_commit: str | None,
    topology_path: str | Path,
    max_file_bytes: int,
) -> tuple[dict[str, object], list[tuple[dict[str, object], int]]]:
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

    push_commits = _push_commits(repo, branch_head, base_commit)
    for commit in push_commits:
        _validate_new_message_ids(repo, commit)

    if base_commit and base_commit != _ZERO_SHA:
        projection_paths = _added_message_paths_for_commits(repo, push_commits)
        projection_mode = "DELTA"
    else:
        projection_paths = _paths_at_ref(repo, branch_head)
        projection_mode = "FULL_COMPAT"

    files: list[tuple[dict[str, object], int]] = []
    for path in projection_paths:
        # Read the exact Git object, not a mutable working-tree copy.
        content = _git_bytes(repo, "show", f"{branch_head}:{path}")
        if len(content) > max_file_bytes:
            raise EmitterError(f"MESSAGE_FILE_TOO_LARGE:{path}")

        source_commit = _git(repo, "log", "-1", "--format=%H", branch_head, "--", path)
        source_committed_at = _git(repo, "log", "-1", "--format=%cI", branch_head, "--", path)
        if not source_commit or not source_committed_at:
            raise EmitterError(f"MESSAGE_SOURCE_COMMIT_MISSING:{path}")
        blob_sha = _git(repo, "rev-parse", f"{branch_head}:{path}")

        files.append(
            (
                {
                    "path": path,
                    "source_commit": source_commit,
                    "source_committed_at": source_committed_at,
                    "blob_sha": blob_sha,
                    "content_base64": base64.b64encode(content).decode("ascii"),
                },
                len(content),
            )
        )

    common = {
        "projection_version": 1,
        "repository": repository,
        "ref": ref,
        "branch_head": branch_head,
        "lane_identity": lane_identity,
        "projection_mode": projection_mode,
    }
    return common, files


def collect_projection_batch(
    repo_dir: str | Path,
    *,
    repository: str,
    ref: str,
    branch_head: str,
    base_commit: str | None = None,
    topology_path: str | Path = DEFAULT_TOPOLOGY,
    max_files: int = DEFAULT_MAX_FILES,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
) -> dict[str, object]:
    """Collect one provider-safe batch, failing rather than dropping overflow."""
    _validate_limits(max_files, max_file_bytes, max_total_bytes)
    common, files_with_sizes = _collect_projection_source(
        repo_dir,
        repository=repository,
        ref=ref,
        branch_head=branch_head,
        base_commit=base_commit,
        topology_path=topology_path,
        max_file_bytes=max_file_bytes,
    )
    if len(files_with_sizes) > max_files:
        raise EmitterError("BATCH_TOO_MANY_FILES")
    if sum(size for _, size in files_with_sizes) > max_total_bytes:
        raise EmitterError("BATCH_TOO_LARGE")
    return {**common, "files": [item for item, _ in files_with_sizes]}


def collect_projection_batches(
    repo_dir: str | Path,
    *,
    repository: str,
    ref: str,
    branch_head: str,
    base_commit: str | None = None,
    topology_path: str | Path = DEFAULT_TOPOLOGY,
    max_files: int = DEFAULT_MAX_FILES,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
) -> tuple[dict[str, object], ...]:
    """Collect every source file exactly once in deterministic bounded chunks."""
    _validate_limits(max_files, max_file_bytes, max_total_bytes)

    # Preserve the long-standing single-batch API path for ordinary traffic and
    # test doubles. Only overflow pays for the second source traversal.
    try:
        single = collect_projection_batch(
            repo_dir,
            repository=repository,
            ref=ref,
            branch_head=branch_head,
            base_commit=base_commit,
            topology_path=topology_path,
            max_files=max_files,
            max_file_bytes=max_file_bytes,
            max_total_bytes=max_total_bytes,
        )
    except EmitterError as exc:
        if str(exc) not in {"BATCH_TOO_MANY_FILES", "BATCH_TOO_LARGE"}:
            raise
    else:
        return (
            {
                **single,
                "projection_chunk_index": 1,
                "projection_chunk_count": 1,
            },
        )

    common, files_with_sizes = _collect_projection_source(
        repo_dir,
        repository=repository,
        ref=ref,
        branch_head=branch_head,
        base_commit=base_commit,
        topology_path=topology_path,
        max_file_bytes=max_file_bytes,
    )

    chunks: list[list[dict[str, object]]] = []
    current: list[dict[str, object]] = []
    current_bytes = 0
    for item, size in files_with_sizes:
        if size > max_total_bytes:
            raise EmitterError(f"MESSAGE_FILE_EXCEEDS_BATCH_LIMIT:{item['path']}")
        would_overflow = current and (
            len(current) >= max_files or current_bytes + size > max_total_bytes
        )
        if would_overflow:
            chunks.append(current)
            current = []
            current_bytes = 0
        current.append(item)
        current_bytes += size
    if current or not chunks:
        chunks.append(current)

    chunk_count = len(chunks)
    return tuple(
        {
            **common,
            "projection_chunk_index": index,
            "projection_chunk_count": chunk_count,
            "files": chunk,
        }
        for index, chunk in enumerate(chunks, start=1)
    )


def request_oidc_token(audience: str = DEFAULT_AUDIENCE) -> str:
    request_url = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_URL", "")
    request_token = os.environ.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "")
    if not request_url or not request_token:
        raise EmitterError("GITHUB_OIDC_ENV_MISSING")

    req = Request(
        build_oidc_url(request_url, audience),
        headers={"Authorization": f"Bearer {request_token}", "Accept": "application/json"},
    )
    try:
        with urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise EmitterError(f"GITHUB_OIDC_REQUEST_FAILED:{exc}") from exc
    token = data.get("value") if isinstance(data, dict) else None
    if not isinstance(token, str) or not token:
        raise EmitterError("GITHUB_OIDC_TOKEN_MISSING")
    return token


def post_projection_batch(
    endpoint: str,
    oidc_token: str,
    batch: dict[str, object],
) -> dict[str, object]:
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


def projection_result_failed(result: dict[str, object]) -> bool:
    if result.get("ok") is not True:
        return True

    conflicts = result.get("conflicts", 0)
    if isinstance(conflicts, int) and conflicts > 0:
        return True

    rows = result.get("results")
    if not isinstance(rows, list):
        return True
    for row in rows:
        if not isinstance(row, dict):
            return True
        status = row.get("result")
        if not isinstance(status, str) or status.casefold() in {"conflict", "failed", "error"}:
            return True
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-dir", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--base")
    parser.add_argument("--topology", default=str(DEFAULT_TOPOLOGY))
    parser.add_argument("--cutover", default=str(DEFAULT_CUTOVER))
    parser.add_argument("--bootstrap-main")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--audience", default=DEFAULT_AUDIENCE)
    args = parser.parse_args(argv)

    try:
        base_commit = resolve_base_commit(args.base)
        try:
            bootstrap_identity = planned_successor_bootstrap_identity(
                args.ref,
                args.head,
                args.topology,
                base=base_commit,
                cutover_path=args.cutover,
                bootstrap_main=args.bootstrap_main,
            )
        except WriterLaneError as exc:
            raise EmitterError(str(exc)) from exc

        if bootstrap_identity is not None:
            print(
                json.dumps(
                    {
                        "status": "PLANNED_SUCCESSOR_BOOTSTRAP_SKIPPED",
                        "lane_identity": bootstrap_identity,
                        "branch_head": args.head,
                    },
                    sort_keys=True,
                )
            )
            return 0

        batches = collect_projection_batches(
            args.repo_dir,
            repository=args.repository,
            ref=args.ref,
            branch_head=args.head,
            base_commit=base_commit,
            topology_path=args.topology,
        )
        token = request_oidc_token(args.audience)

        all_results: list[dict[str, object]] = []
        total_projected = 0
        for batch in batches:
            result = post_projection_batch(args.endpoint, token, batch)
            if projection_result_failed(result):
                print(
                    json.dumps(
                        {
                            "ok": False,
                            "failed_chunk": batch.get("projection_chunk_index"),
                            "chunk_count": len(batches),
                            "provider_result": result,
                        },
                        sort_keys=True,
                    )
                )
                return 1
            rows = result["results"]
            assert isinstance(rows, list)  # established by projection_result_failed
            all_results.extend(row for row in rows if isinstance(row, dict))
            projected = result.get("projected")
            total_projected += projected if isinstance(projected, int) else len(rows)
    except EmitterError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "chunks": len(batches),
                "projected": total_projected,
                "results": all_results,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
