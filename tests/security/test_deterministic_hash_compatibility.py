import hashlib
import json

from radar.envelope import RadarEnvelope


def _build(*, sender: str, audience: list[str], domain: str, intent: str):
    payload = {"same": "payload", "nested": {"b": 2, "a": 1}}
    result = RadarEnvelope.from_mapping(
        {
            "schema_version": 1,
            "message_id": f"{sender}-hash-test",
            "created_at": "2026-09-04T22:00:00Z",
            "sender": sender,
            "audience": audience,
            "domain": domain,
            "intent": intent,
            "priority": 3,
            "idempotency_key": "caller-controlled-value",
            "payload": payload,
        }
    )
    assert result.envelope is not None
    return result.envelope, payload


def test_dedupe_key_matches_existing_middleware_payload_hash_contract():
    first, payload = _build(
        sender="radar",
        audience=["one"],
        domain="system",
        intent="event",
    )
    second, _ = _build(
        sender="vera",
        audience=["seven"],
        domain="coordination",
        intent="query",
    )

    expected = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    assert first.idempotency_key == expected
    assert second.idempotency_key == expected
    assert first.content_hash != second.content_hash
