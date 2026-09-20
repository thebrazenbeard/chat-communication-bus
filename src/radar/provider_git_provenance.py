"""Authoritative read-only GitHub provenance verification for portable state.

The resolver verifies the immutable repository + commit + path -> blob relationship
against GitHub's API before provider materialization may treat a StateReference as
repository-backed provenance.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from .provider_portability import StateReference


_REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_GITHUB_API = "https://api.github.com"


def _validate_repository(repository: str) -> str:
    if type(repository) is not str or not _REPOSITORY_RE.fullmatch(repository):
        raise ValueError("repository must be exact GitHub owner/name")
    owner, name = repository.split("/", 1)
    if owner in (".", "..") or name in (".", ".."):
        raise ValueError("repository contains ambiguous path segment")
    return repository


def _validate_git_path(path: str) -> str:
    if type(path) is not str or not path:
        raise ValueError("path must be a non-empty exact Git path")
    if path.startswith("/") or "\\" in path:
        raise ValueError("path must be a relative POSIX Git path")
    parts = path.split("/")
    if any(part in ("", ".", "..") for part in parts):
        raise ValueError("path contains ambiguous Git path segment")
    return path


def _github_get_json(url: str, *, token: str | None, timeout: float) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "vera-provider-portability-v1",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise ValueError(
            f"GitHub provenance readback failed with HTTP {exc.code}"
        ) from None
    except URLError as exc:
        raise ValueError("GitHub provenance readback unavailable") from exc


@dataclass(frozen=True)
class GitHubProvenanceReceipt:
    repository: str
    repository_id: int
    commit_sha: str
    path: str
    git_blob: str
    resolver_claim: str = "GITHUB_API_COMMIT_PATH_BLOB_READBACK_V1"

    def __post_init__(self) -> None:
        _validate_repository(self.repository)
        if (
            type(self.repository_id) is not int
            or isinstance(self.repository_id, bool)
            or self.repository_id <= 0
        ):
            raise ValueError("repository_id must be a positive exact integer")
        _validate_git_path(self.path)
        for value, label in (
            (self.commit_sha, "commit_sha"),
            (self.git_blob, "git_blob"),
        ):
            if (
                type(value) is not str
                or len(value) != 40
                or any(ch not in "0123456789abcdef" for ch in value)
            ):
                raise ValueError(
                    f"{label} must be a lowercase Git SHA-1 object id"
                )
        if self.resolver_claim != "GITHUB_API_COMMIT_PATH_BLOB_READBACK_V1":
            raise ValueError("unsupported provenance resolver claim")


class GitHubCommitPathResolver:
    """Resolve immutable Git state against GitHub's repository object database."""

    __slots__ = ("_token", "_timeout")

    def __init__(self, *, token: str | None = None, timeout: float = 10.0) -> None:
        if token is not None and (type(token) is not str or not token):
            raise ValueError("token must be None or a non-empty exact string")
        if type(timeout) not in (int, float) or isinstance(timeout, bool) or timeout <= 0:
            raise ValueError("timeout must be positive")
        self._token = token
        self._timeout = float(timeout)

    def resolve(self, reference: StateReference) -> GitHubProvenanceReceipt:
        if type(reference) is not StateReference:
            raise ValueError("reference must be exact StateReference")

        repository = _validate_repository(reference.repository)
        path = _validate_git_path(reference.path)
        owner_repo = quote(repository, safe="/")
        repository_url = f"{_GITHUB_API}/repos/{owner_repo}"
        repository_readback = _github_get_json(
            repository_url, token=self._token, timeout=self._timeout
        )
        if type(repository_readback) is not dict:
            raise ValueError("GitHub repository readback was not an object")
        if repository_readback.get("full_name") != repository:
            raise ValueError("GitHub repository full-name readback mismatch")
        if repository_readback.get("id") != reference.repository_id:
            raise ValueError("GitHub repository id readback mismatch")

        commit_url = (
            f"{_GITHUB_API}/repos/{owner_repo}/git/commits/{reference.commit_sha}"
        )
        commit = _github_get_json(
            commit_url, token=self._token, timeout=self._timeout
        )
        if type(commit) is not dict or commit.get("sha") != reference.commit_sha:
            raise ValueError("GitHub commit readback did not match exact commit")

        encoded_path = quote(path, safe="/")
        content_url = (
            f"{_GITHUB_API}/repos/{owner_repo}/contents/{encoded_path}"
            f"?ref={reference.commit_sha}"
        )
        content = _github_get_json(
            content_url, token=self._token, timeout=self._timeout
        )
        if type(content) is not dict:
            raise ValueError("GitHub path readback was not a file object")
        if content.get("type") != "file":
            raise ValueError("GitHub path did not resolve to a file blob")
        if content.get("path") != path:
            raise ValueError("GitHub path readback mismatch")
        if content.get("sha") != reference.git_blob:
            raise ValueError("GitHub commit/path blob mismatch")

        return GitHubProvenanceReceipt(
            repository=repository,
            repository_id=reference.repository_id,
            commit_sha=reference.commit_sha,
            path=path,
            git_blob=reference.git_blob,
        )


__all__ = [
    "GitHubCommitPathResolver",
    "GitHubProvenanceReceipt",
]
