import pytest

from radar.message_grammar import MessageGrammarError, parse_bus_document


def test_invalid_boolean_is_rejected_by_canonical_grammar() -> None:
    content = b"message_id: radar-9999\nwriter: Radar\nrequires_reply: maybe\n\nBody\n"
    with pytest.raises(MessageGrammarError, match="INVALID_REQUIRES_REPLY"):
        parse_bus_document(content, path="messages/radar-9999.md")


def test_timezone_less_datetime_is_rejected_but_date_only_is_canonicalized() -> None:
    with pytest.raises(MessageGrammarError, match="INVALID_CREATED_AT"):
        parse_bus_document(
            b"message_id: radar-9999\nwriter: Radar\ncreated_at: 2026-09-06T09:00:00\n\nBody\n"
        )

    parsed = parse_bus_document(
        b"message_id: radar-9999\nwriter: Radar\ncreated_at: 2026-09-06\n\nBody\n"
    )
    assert parsed.created_at == "2026-09-06T00:00:00Z"


def test_frontmatter_scalars_hashes_and_endthread_are_shared_evidence() -> None:
    content = (
        b"---\n"
        b"message_id: `radar-9999`\n"
        b"writer: 'Radar'\n"
        b"requires_reply: yes\n"
        b"intended_recipient: Vera, One\n"
        b"ignored_list:\n"
        b"  - provenance-only\n"
        b"---\n\n"
        b"Body\n#ENDTHREAD\n"
    )
    parsed = parse_bus_document(content)
    assert parsed.message_id == "radar-9999"
    assert parsed.writer == "Radar"
    assert parsed.requires_reply is True
    assert parsed.requires_ack is False
    assert parsed.conversation_closed_by_sender is True
    assert len(parsed.full_sha256) == 64
    assert len(parsed.body_sha256) == 64
    assert parsed.body_length == len(b"Body\n#ENDTHREAD\n")
