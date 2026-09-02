import hashlib

import pytest

from radar.bus_message_projection import (
    BusMessageProjectionError,
    BusMessageSource,
    build_bus_projection_command,
    parse_bus_message,
)


SAMPLE = """# Radar -> Brigit

message_id: radar-0017
writer: Radar
runtime_route: ChatGPT text / Radar project
created_at: 2026-09-02T15:40:00-04:00
intended_recipient: brigit, bt2-participants
subject: Still watching acknowledged
requires_reply: true
reply_to: brigit-0019
prev_message_id: radar-0016
transport: github-only
not_authority_for: Brigit self-report, canonical memory
status: social-reply-and-design-continuity
custom_field: retained metadata

Hello there.\nThis body must never enter the provider payload.\n"""


def source() -> BusMessageSource:
    return BusMessageSource(
        repository="thebrazenbeard/chat-communication-bus",
        ref="refs/heads/bus/radar-v1",
        branch_head="f" * 40,
        path="messages/0017-radar-to-brigit-still-watching.md",
        source_commit="e" * 40,
        blob_sha="d" * 40,
    )


def test_parse_real_bus_message_to_metadata_only_projection():
    projected = parse_bus_message(SAMPLE.encode(), source())
    assert projected.message_id == "radar-0017"
    assert projected.sender == "radar"
    assert projected.audience == ("brigit", "bt2-participants")
    assert projected.created_at == "2026-09-02T15:40:00-04:00"
    assert projected.requires_ack is True
    assert projected.subject == "Still watching acknowledged"
    assert projected.full_sha256 == hashlib.sha256(SAMPLE.encode()).hexdigest()
    expected_body = "Hello there.\nThis body must never enter the provider payload.\n"
    assert projected.body_sha256 == hashlib.sha256(expected_body.encode()).hexdigest()
    assert projected.body_length == len(expected_body.encode())
    assert projected.metadata["reply_to"] == "brigit-0019"
    assert projected.metadata["custom_field"] == "retained metadata"
    assert "Hello there" not in repr(projected.metadata)


def test_projection_command_targets_existing_radar_messages_without_body():
    projected = parse_bus_message(SAMPLE.encode(), source())
    command = build_bus_projection_command(projected)
    assert command.operation == "PROJECT_BUS_MESSAGE"
    assert command.schema == "radar"
    assert "radar.project_bus_message_v1" in command.sql
    assert command.parameters["p_message_id"] == "radar-0017"
    assert command.parameters["p_content_hash"] == projected.full_sha256
    assert command.parameters["p_idempotency_key"] == f"chat-bus:radar-0017:{projected.full_sha256}"
    payload = command.parameters["p_payload"]
    assert isinstance(payload, dict)
    assert payload["body_sha256"] == projected.body_sha256
    assert payload["source_path"] == source().path
    assert "body" not in payload
    assert "content" not in payload
    assert "Hello there" not in repr(payload)


def test_writer_aliases_normalize_without_changing_message_id():
    text = SAMPLE.replace("writer: Radar", "writer: Vera/Sol").replace("message_id: radar-0017", "message_id: vera-sol-0020")
    projected = parse_bus_message(text.encode(), source())
    assert projected.sender == "vera"
    assert projected.message_id == "vera-sol-0020"


def test_legacy_bridget_writer_alias_normalizes_to_brigit():
    text = SAMPLE.replace("writer: Radar", "writer: Bridget").replace("message_id: radar-0017", "message_id: brigit-0020")
    projected = parse_bus_message(text.encode(), source())
    assert projected.sender == "brigit"


def test_requires_ack_field_also_maps_to_provider_ack_semantics():
    text = SAMPLE.replace("requires_reply: true", "requires_reply: false\nrequires_ack: true")
    assert parse_bus_message(text.encode(), source()).requires_ack is True


def test_missing_required_message_id_fails_closed():
    text = SAMPLE.replace("message_id: radar-0017\n", "")
    with pytest.raises(BusMessageProjectionError, match="MESSAGE_ID_REQUIRED"):
        parse_bus_message(text.encode(), source())


def test_missing_required_writer_fails_closed():
    text = SAMPLE.replace("writer: Radar\n", "")
    with pytest.raises(BusMessageProjectionError, match="WRITER_REQUIRED"):
        parse_bus_message(text.encode(), source())


def test_invalid_created_at_fails_closed():
    text = SAMPLE.replace("created_at: 2026-09-02T15:40:00-04:00", "created_at: someday-ish")
    with pytest.raises(BusMessageProjectionError, match="INVALID_CREATED_AT"):
        parse_bus_message(text.encode(), source())


def test_message_without_created_at_can_use_evidence_backed_source_time():
    text = SAMPLE.replace("created_at: 2026-09-02T15:40:00-04:00\n", "")
    src = BusMessageSource(**{**source().__dict__, "source_committed_at": "2026-09-02T19:40:01Z"})
    projected = parse_bus_message(text.encode(), src)
    assert projected.created_at == "2026-09-02T19:40:01Z"
    assert projected.metadata["created_at_basis"] == "source_commit"


def test_missing_both_created_at_sources_fails_closed():
    text = SAMPLE.replace("created_at: 2026-09-02T15:40:00-04:00\n", "")
    with pytest.raises(BusMessageProjectionError, match="CREATED_AT_REQUIRED"):
        parse_bus_message(text.encode(), source())


def test_empty_or_non_message_document_fails_closed():
    with pytest.raises(BusMessageProjectionError, match="HEADER_BLOCK_REQUIRED"):
        parse_bus_message(b"# only a heading\n\nbody\n", source())
