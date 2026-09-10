from __future__ import annotations

import json

import pytest

from radar.project_queue import (
    ProjectQueueError,
    ProjectQueueReader,
    ProjectQueueSpec,
    load_project_queue_spec,
    render_snapshot_json,
)


class FakeRunner:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def __call__(self, argv):
        self.calls.append(tuple(argv))
        key = tuple(argv)
        if key not in self.responses:
            raise AssertionError(f"unexpected command: {argv!r}")
        return self.responses[key]


SPEC = ProjectQueueSpec(
    owner="thebrazenbeard",
    project_number=10,
    expected_title="Radar's Chat Bus Fix",
    status_field="Status",
    allowed_statuses=("Backlog", "Ready", "In progress", "In review", "Done"),
    item_limit=100,
)


def commands():
    return {
        (
            "gh", "project", "view", "10", "--owner", "thebrazenbeard", "--format", "json"
        ): json.dumps({
            "id": "PVT_kwHOExample",
            "number": 10,
            "title": "Radar's Chat Bus Fix",
        }),
        (
            "gh", "project", "field-list", "10", "--owner", "thebrazenbeard",
            "--format", "json", "--limit", "100"
        ): json.dumps({
            "totalCount": 3,
            "fields": [
                {"id": "PVTF_title", "name": "Title", "type": "ProjectV2Field"},
                {
                    "id": "PVTSSF_status",
                    "name": "Status",
                    "type": "ProjectV2SingleSelectField",
                    "options": [
                        {"id": "f75ad846", "name": "Backlog"},
                        {"id": "e18bf179", "name": "Ready"},
                        {"id": "47fc9ee4", "name": "In progress"},
                        {"id": "aba860b9", "name": "In review"},
                        {"id": "98236657", "name": "Done"},
                    ],
                },
                {"id": "PVTF_repo", "name": "Repository", "type": "ProjectV2Field"},
            ],
        }),
        (
            "gh", "project", "item-list", "10", "--owner", "thebrazenbeard",
            "--format", "json", "--limit", "100", "--field", "Status"
        ): json.dumps({
            "totalCount": 3,
            "items": [
                {
                    "id": "PVTI_73",
                    "status": "Backlog",
                    "content": {
                        "type": "Issue",
                        "number": 73,
                        "title": "Retire stale actions",
                        "repository": "thebrazenbeard/chat-communication-bus",
                        "url": "https://github.com/thebrazenbeard/chat-communication-bus/issues/73",
                    },
                },
                {
                    "id": "PVTI_72",
                    "status": "In review",
                    "content": {
                        "type": "PullRequest",
                        "number": 72,
                        "title": "Zero-cost source CI",
                        "repository": "thebrazenbeard/chat-communication-bus",
                        "url": "https://github.com/thebrazenbeard/chat-communication-bus/pull/72",
                    },
                },
                {
                    "id": "PVTI_DRAFT",
                    "status": "Ready",
                    "content": {"type": "DraftIssue", "title": "Investigate something"},
                },
            ],
        }),
    }


def test_read_normalizes_project_metadata_and_sorts_items_deterministically():
    runner = FakeRunner(commands())
    snapshot = ProjectQueueReader(SPEC, runner=runner).read()

    assert snapshot["schema"] == "radar-project-queue-snapshot-v1"
    assert snapshot["authority"] == "QUEUE_METADATA_ONLY"
    assert snapshot["mutation_supported"] is False
    assert snapshot["browser_session_api_used"] is False
    assert snapshot["project"] == {
        "id": "PVT_kwHOExample",
        "number": 10,
        "owner": "thebrazenbeard",
        "title": "Radar's Chat Bus Fix",
    }
    assert [item["item_id"] for item in snapshot["items"]] == [
        "PVTI_DRAFT", "PVTI_72", "PVTI_73"
    ]
    assert snapshot["items"][1]["content_key"] == "thebrazenbeard/chat-communication-bus#72"
    assert "execution_truth" not in snapshot["items"][2]
    rendered = render_snapshot_json(snapshot)
    assert rendered.endswith("\n")
    assert rendered == render_snapshot_json(snapshot)
    assert json.loads(rendered) == snapshot


def test_read_uses_only_official_read_only_gh_project_commands():
    runner = FakeRunner(commands())
    ProjectQueueReader(SPEC, runner=runner).read()
    assert runner.calls == [
        ("gh", "project", "view", "10", "--owner", "thebrazenbeard", "--format", "json"),
        ("gh", "project", "field-list", "10", "--owner", "thebrazenbeard", "--format", "json", "--limit", "100"),
        ("gh", "project", "item-list", "10", "--owner", "thebrazenbeard", "--format", "json", "--limit", "100", "--field", "Status"),
    ]
    assert all("item-edit" not in call for call in runner.calls)
    assert all("api" not in call for call in runner.calls)
    assert all("memex" not in " ".join(call).lower() for call in runner.calls)


@pytest.mark.parametrize("payload_key", ["fields", "items"])
def test_incomplete_cli_result_fails_closed(payload_key):
    responses = commands()
    command_name = "field-list" if payload_key == "fields" else "item-list"
    command = next(key for key in responses if command_name in key)
    payload = json.loads(responses[command])
    payload["totalCount"] = len(payload[payload_key]) + 1
    responses[command] = json.dumps(payload)
    with pytest.raises(ProjectQueueError, match="INCOMPLETE_"):
        ProjectQueueReader(SPEC, runner=FakeRunner(responses)).read()


def test_unknown_status_fails_closed():
    responses = commands()
    command = next(key for key in responses if "item-list" in key)
    payload = json.loads(responses[command])
    payload["items"][0]["status"] = "Mystery"
    responses[command] = json.dumps(payload)
    with pytest.raises(ProjectQueueError, match="UNKNOWN_STATUS"):
        ProjectQueueReader(SPEC, runner=FakeRunner(responses)).read()


def test_duplicate_repo_content_key_fails_closed():
    responses = commands()
    command = next(key for key in responses if "item-list" in key)
    payload = json.loads(responses[command])
    duplicate = dict(payload["items"][0])
    duplicate["id"] = "PVTI_DUP"
    payload["items"].append(duplicate)
    payload["totalCount"] += 1
    responses[command] = json.dumps(payload)
    with pytest.raises(ProjectQueueError, match="DUPLICATE_CONTENT_KEY"):
        ProjectQueueReader(SPEC, runner=FakeRunner(responses)).read()


def test_duplicate_project_item_id_fails_closed():
    responses = commands()
    command = next(key for key in responses if "item-list" in key)
    payload = json.loads(responses[command])
    payload["items"][1]["id"] = payload["items"][0]["id"]
    responses[command] = json.dumps(payload)
    with pytest.raises(ProjectQueueError, match="DUPLICATE_PROJECT_ITEM_ID"):
        ProjectQueueReader(SPEC, runner=FakeRunner(responses)).read()


def test_project_identity_and_status_field_must_match_contract():
    responses = commands()
    view_cmd = next(key for key in responses if "view" in key)
    payload = json.loads(responses[view_cmd])
    payload["title"] = "Wrong Project"
    responses[view_cmd] = json.dumps(payload)
    with pytest.raises(ProjectQueueError, match="PROJECT_IDENTITY_MISMATCH"):
        ProjectQueueReader(SPEC, runner=FakeRunner(responses)).read()

    responses = commands()
    field_cmd = next(key for key in responses if "field-list" in key)
    payload = json.loads(responses[field_cmd])
    payload["fields"] = [field for field in payload["fields"] if field["name"] != "Status"]
    payload["totalCount"] -= 1
    responses[field_cmd] = json.dumps(payload)
    with pytest.raises(ProjectQueueError, match="STATUS_FIELD_MISSING"):
        ProjectQueueReader(SPEC, runner=FakeRunner(responses)).read()


def test_gh_failure_is_bounded_and_does_not_echo_secret_stderr():
    class FailingRunner:
        def __call__(self, argv):
            raise ProjectQueueError("GH_COMMAND_FAILED:item-list")

    with pytest.raises(ProjectQueueError) as exc:
        ProjectQueueReader(SPEC, runner=FailingRunner()).read()
    assert "token" not in str(exc.value).lower()


def _contract():
    return {
        "schema_version": 1,
        "owner": "thebrazenbeard",
        "project_number": 10,
        "expected_title": "Radar's Chat Bus Fix",
        "status_field": "Status",
        "allowed_statuses": ["Backlog", "Ready", "In progress", "In review", "Done"],
        "item_limit": 100,
        "authority": "QUEUE_METADATA_ONLY",
        "transport": "GH_PROJECT_JSON",
        "mutation_supported": False,
        "browser_session_api_allowed": False,
        "max_out_of_pocket_cost_usd": 0,
    }


def test_contract_loader_is_strict_and_read_only(tmp_path):
    path = tmp_path / "contract.json"
    path.write_text(json.dumps(_contract()), encoding="utf-8")
    assert load_project_queue_spec(path) == SPEC

    raw = _contract()
    raw["mutation_supported"] = True
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ProjectQueueError, match="PROJECT_QUEUE_CONTRACT_UNSAFE"):
        load_project_queue_spec(path)


def test_contract_loader_rejects_duplicate_or_unknown_statuses(tmp_path):
    path = tmp_path / "contract.json"
    for statuses in (
        ["Backlog", "Ready", "Ready", "In review", "Done"],
        ["Backlog", "Ready", "In progress", "In review", "Done", "Mystery"],
    ):
        raw = _contract()
        raw["allowed_statuses"] = statuses
        path.write_text(json.dumps(raw), encoding="utf-8")
        with pytest.raises(ProjectQueueError, match="PROJECT_QUEUE_CONTRACT_INVALID"):
            load_project_queue_spec(path)
