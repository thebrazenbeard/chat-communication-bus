"""Read-only GitHub Projects v2 queue adapter.

Project membership/status is queue metadata only. Repository issue/PR/branch/review/CI
state remains execution truth and must be read separately.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import subprocess
from typing import Callable, Sequence


class ProjectQueueError(RuntimeError):
    """Bounded, non-secret-bearing adapter failure."""


@dataclass(frozen=True)
class ProjectQueueSpec:
    owner: str
    project_number: int
    expected_title: str
    status_field: str
    allowed_statuses: tuple[str, ...]
    item_limit: int = 100


Runner = Callable[[Sequence[str]], str]
_CANONICAL_STATUSES = ("Backlog", "Ready", "In progress", "In review", "Done")


def _default_runner(argv: Sequence[str]) -> str:
    try:
        completed = subprocess.run(
            list(argv),
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
        )
    except FileNotFoundError as exc:
        raise ProjectQueueError("GH_CLI_UNAVAILABLE") from exc
    except subprocess.TimeoutExpired as exc:
        raise ProjectQueueError("GH_COMMAND_TIMEOUT") from exc
    except OSError as exc:
        raise ProjectQueueError("GH_COMMAND_UNAVAILABLE") from exc

    if completed.returncode != 0:
        command = " ".join(argv[:3])
        raise ProjectQueueError(
            f"GH_COMMAND_FAILED:{command}:exit={completed.returncode}"
        )
    return completed.stdout


def _decode_object(raw: str, label: str) -> dict[str, object]:
    try:
        value = json.loads(raw)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ProjectQueueError(f"INVALID_JSON:{label}") from exc
    if not isinstance(value, dict):
        raise ProjectQueueError(f"INVALID_JSON_OBJECT:{label}")
    return value


def _require_str(value: object, code: str) -> str:
    if not isinstance(value, str) or not value:
        raise ProjectQueueError(code)
    return value


def _require_list(value: object, code: str) -> list[object]:
    if not isinstance(value, list):
        raise ProjectQueueError(code)
    return value


def _validate_complete(payload: dict[str, object], key: str, code: str) -> list[object]:
    values = _require_list(payload.get(key), f"{code}_SHAPE")
    total = payload.get("totalCount")
    if not isinstance(total, int) or isinstance(total, bool) or total < 0:
        raise ProjectQueueError(f"{code}_TOTAL_COUNT_INVALID")
    if total != len(values):
        raise ProjectQueueError(f"INCOMPLETE_{code}")
    return values


def _content_kind(content: dict[str, object]) -> str:
    raw = content.get("type")
    if isinstance(raw, str) and raw:
        return raw
    if "number" in content:
        return "RepositoryItem"
    return "DraftIssue"


def _repository_name(value: object) -> str | None:
    if isinstance(value, str) and value:
        return value
    if isinstance(value, dict):
        for key in ("nameWithOwner", "name_with_owner"):
            candidate = value.get(key)
            if isinstance(candidate, str) and candidate:
                return candidate
    return None


class ProjectQueueReader:
    def __init__(self, spec: ProjectQueueSpec, *, runner: Runner | None = None) -> None:
        self.spec = spec
        self.runner = runner or _default_runner

    def _run(self, argv: Sequence[str], label: str) -> dict[str, object]:
        try:
            raw = self.runner(argv)
        except ProjectQueueError:
            raise
        except Exception as exc:
            raise ProjectQueueError(f"GH_COMMAND_FAILED:{label}") from exc
        return _decode_object(raw, label)

    def read(self) -> dict[str, object]:
        number = str(self.spec.project_number)
        owner = self.spec.owner

        view = self._run(
            ("gh", "project", "view", number, "--owner", owner, "--format", "json"),
            "view",
        )
        title = _require_str(view.get("title"), "PROJECT_TITLE_MISSING")
        project_id = _require_str(view.get("id"), "PROJECT_ID_MISSING")
        view_number = view.get("number", self.spec.project_number)
        if (
            title != self.spec.expected_title
            or not isinstance(view_number, int)
            or isinstance(view_number, bool)
            or view_number != self.spec.project_number
        ):
            raise ProjectQueueError("PROJECT_IDENTITY_MISMATCH")

        field_payload = self._run(
            (
                "gh", "project", "field-list", number, "--owner", owner,
                "--format", "json", "--limit", "100",
            ),
            "field-list",
        )
        fields = _validate_complete(field_payload, "fields", "FIELDS")
        status_matches = [
            item
            for item in fields
            if isinstance(item, dict) and item.get("name") == self.spec.status_field
        ]
        if len(status_matches) != 1:
            raise ProjectQueueError("STATUS_FIELD_MISSING")
        status_raw = status_matches[0]
        status_id = _require_str(status_raw.get("id"), "STATUS_FIELD_ID_MISSING")
        options_raw = _require_list(status_raw.get("options"), "STATUS_OPTIONS_MISSING")
        options: list[dict[str, str]] = []
        seen_option_names: set[str] = set()
        for raw in options_raw:
            if not isinstance(raw, dict):
                raise ProjectQueueError("STATUS_OPTION_INVALID")
            option_id = _require_str(raw.get("id"), "STATUS_OPTION_ID_MISSING")
            name = _require_str(raw.get("name"), "STATUS_OPTION_NAME_MISSING")
            if name in seen_option_names:
                raise ProjectQueueError("DUPLICATE_STATUS_OPTION")
            seen_option_names.add(name)
            options.append({"id": option_id, "name": name})
        if tuple(option["name"] for option in options) != self.spec.allowed_statuses:
            raise ProjectQueueError("STATUS_OPTIONS_MISMATCH")

        item_payload = self._run(
            (
                "gh", "project", "item-list", number, "--owner", owner,
                "--format", "json", "--limit", str(self.spec.item_limit),
                "--field", self.spec.status_field,
            ),
            "item-list",
        )
        raw_items = _validate_complete(item_payload, "items", "ITEMS")

        normalized: list[dict[str, object]] = []
        seen_item_ids: set[str] = set()
        seen_content_keys: set[str] = set()
        for raw in raw_items:
            if not isinstance(raw, dict):
                raise ProjectQueueError("PROJECT_ITEM_INVALID")
            item_id = _require_str(raw.get("id"), "PROJECT_ITEM_ID_MISSING")
            if item_id in seen_item_ids:
                raise ProjectQueueError("DUPLICATE_PROJECT_ITEM_ID")
            seen_item_ids.add(item_id)

            status = raw.get("status")
            if not isinstance(status, str) or status not in self.spec.allowed_statuses:
                raise ProjectQueueError("UNKNOWN_STATUS")

            content = raw.get("content")
            if not isinstance(content, dict):
                raise ProjectQueueError("PROJECT_ITEM_CONTENT_INVALID")
            kind = _content_kind(content)
            title = _require_str(content.get("title"), "PROJECT_ITEM_TITLE_MISSING")
            repository = _repository_name(content.get("repository"))
            number_value = content.get("number")
            url = content.get("url")
            if url is not None and not isinstance(url, str):
                raise ProjectQueueError("PROJECT_ITEM_URL_INVALID")

            if (
                repository is not None
                and isinstance(number_value, int)
                and not isinstance(number_value, bool)
            ):
                content_key = f"{repository}#{number_value}"
            else:
                content_key = f"draft:{item_id}"

            if content_key in seen_content_keys:
                raise ProjectQueueError("DUPLICATE_CONTENT_KEY")
            seen_content_keys.add(content_key)

            normalized.append(
                {
                    "item_id": item_id,
                    "status": status,
                    "content_kind": kind,
                    "content_key": content_key,
                    "repository": repository,
                    "number": number_value
                    if isinstance(number_value, int) and not isinstance(number_value, bool)
                    else None,
                    "title": title,
                    "url": url if isinstance(url, str) else None,
                }
            )

        normalized.sort(
            key=lambda item: (
                "" if item["repository"] is None else str(item["repository"]).casefold(),
                -1 if item["number"] is None else int(item["number"]),
                str(item["item_id"]),
            )
        )

        return {
            "schema": "radar-project-queue-snapshot-v1",
            "authority": "QUEUE_METADATA_ONLY",
            "mutation_supported": False,
            "browser_session_api_used": False,
            "max_out_of_pocket_cost_usd": 0,
            "project": {
                "id": project_id,
                "number": self.spec.project_number,
                "owner": self.spec.owner,
                "title": self.spec.expected_title,
            },
            "status_field": {
                "id": status_id,
                "name": self.spec.status_field,
                "options": options,
            },
            "total_count": len(normalized),
            "items": normalized,
        }


def load_project_queue_spec(path) -> ProjectQueueSpec:
    from pathlib import Path

    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProjectQueueError("PROJECT_QUEUE_CONTRACT_INVALID") from exc
    if not isinstance(raw, dict):
        raise ProjectQueueError("PROJECT_QUEUE_CONTRACT_INVALID")

    safe_envelope = (
        raw.get("schema_version") == 1
        and raw.get("authority") == "QUEUE_METADATA_ONLY"
        and raw.get("transport") == "GH_PROJECT_JSON"
        and raw.get("mutation_supported") is False
        and raw.get("browser_session_api_allowed") is False
        and raw.get("max_out_of_pocket_cost_usd") == 0
    )
    if not safe_envelope:
        raise ProjectQueueError("PROJECT_QUEUE_CONTRACT_UNSAFE")

    statuses = raw.get("allowed_statuses")
    if (
        not isinstance(statuses, list)
        or tuple(statuses) != _CANONICAL_STATUSES
        or len(set(statuses)) != len(statuses)
    ):
        raise ProjectQueueError("PROJECT_QUEUE_CONTRACT_INVALID")

    owner = raw.get("owner")
    project_number = raw.get("project_number")
    expected_title = raw.get("expected_title")
    status_field = raw.get("status_field")
    item_limit = raw.get("item_limit")
    if (
        not isinstance(owner, str)
        or not owner
        or not isinstance(project_number, int)
        or isinstance(project_number, bool)
        or project_number < 1
        or not isinstance(expected_title, str)
        or not expected_title
        or status_field != "Status"
        or not isinstance(item_limit, int)
        or isinstance(item_limit, bool)
        or item_limit < 1
        or item_limit > 1000
    ):
        raise ProjectQueueError("PROJECT_QUEUE_CONTRACT_INVALID")

    return ProjectQueueSpec(
        owner=owner,
        project_number=project_number,
        expected_title=expected_title,
        status_field=status_field,
        allowed_statuses=tuple(statuses),
        item_limit=item_limit,
    )


def render_snapshot_json(snapshot: dict[str, object]) -> str:
    return json.dumps(
        snapshot,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ) + "\n"


__all__ = [
    "ProjectQueueError",
    "ProjectQueueReader",
    "ProjectQueueSpec",
    "load_project_queue_spec",
    "render_snapshot_json",
]
