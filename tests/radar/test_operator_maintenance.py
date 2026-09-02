import importlib
import pytest


def _mods():
    try:
        return importlib.import_module("radar.operator"), importlib.import_module("radar.maintenance")
    except Exception as exc:
        pytest.fail(f"Radar operator implementation missing: {exc}")


def test_operator_bootstrap_order_is_explicit():
    op, _ = _mods()
    assert op.BOOTSTRAP_ORDER == ("contract", "github", "provider", "reconcile", "exceptions", "continue")


def test_operator_status_does_not_claim_chat_session_is_identity_liveness():
    op, _ = _mods()
    status = op.RadarOperator().status(identity_count=3, online_node_count=1, chat_session_active=True)
    assert status["identity_count"] == 3
    assert status["online_node_count"] == 1
    assert status["chat_session_active"] is True
    assert "identity_alive" not in status


def test_maintenance_is_exception_oriented():
    _, m = _mods()
    findings = m.audit({"required_lanes": {"yin", "seven"}, "observed_lanes": {"yin"}, "dlq_pending": 2, "stale_endpoints": 0})
    codes = {x.code for x in findings}
    assert codes == {"MISSING_LANE", "DLQ_PENDING"}


def test_maintenance_surfaces_malformed_lane_separately_from_missing_lane():
    _, m = _mods()
    findings = m.audit(
        {
            "required_lanes": {"hephaestus"},
            "observed_lanes": set(),
            "malformed_lanes": {"bus/hephaestus-v1"},
        }
    )
    pairs = {(x.code, x.detail) for x in findings}
    assert ("MISSING_LANE", "hephaestus") in pairs
    assert ("MALFORMED_LANE", "bus/hephaestus-v1") in pairs
