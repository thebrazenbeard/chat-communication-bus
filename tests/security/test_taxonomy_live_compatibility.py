import pytest

from radar.envelope import EnvelopeClassification, RadarEnvelope


@pytest.mark.parametrize(
    ("domain", "intent"),
    [
        ("chat_bus", "bus_message"),
        ("protocol", "event"),
        ("repository", "event"),
        ("coordination", "event"),
        ("database", "event"),
        ("security", "verification"),
        ("system", "telemetry"),
    ],
)
def test_source_and_provider_backed_taxonomy_values_remain_admissible(domain, intent):
    result = RadarEnvelope.from_mapping(
        {
            "schema_version": 1,
            "sender": "radar",
            "domain": domain,
            "intent": intent,
            "payload": {},
        }
    )

    assert result.classification in {
        EnvelopeClassification.VALID,
        EnvelopeClassification.NORMALIZED,
    }
    assert result.envelope is not None
