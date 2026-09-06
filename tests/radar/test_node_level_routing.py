from __future__ import annotations

import pytest

from radar.envelope import RadarEnvelope
from radar.model import NodeStatus
from radar.registry import IdentityRegistry, RegistryError
from radar.routing import Router


def _env(*, audience=("yin",), intent="event", priority=2):
    result = RadarEnvelope.from_mapping(
        {
            "schema_version": 1,
            "message_id": f"radar-node-route-{intent}-{priority}",
            "created_at": "2026-09-06T13:23:00Z",
            "sender": "radar",
            "audience": list(audience),
            "domain": "database",
            "intent": intent,
            "priority": priority,
            "payload": {"intent": intent},
        }
    )
    assert result.envelope is not None
    return result.envelope


def _register_node(
    registry: IdentityRegistry,
    node_id: str,
    *,
    status=NodeStatus.ONLINE,
    last_heartbeat_ms=1_000,
    lease_expires_ms=2_000,
):
    return registry.register_node(
        node_id,
        identity_id="yin",
        status=status,
        last_heartbeat_ms=last_heartbeat_ms,
        lease_expires_ms=lease_expires_ms,
    )


def test_routes_only_exact_live_node_matching_domain_and_intent():
    registry = IdentityRegistry()
    registry.register_identity("yin", display_name="Yin")
    _register_node(registry, "yin-event")
    _register_node(registry, "yin-command")
    registry.subscribe("yin-event", domain="database", intent="event", min_priority=4)
    registry.subscribe("yin-command", domain="database", intent="command", min_priority=4)

    decision = Router(registry).route(_env(intent="event"), now_ms=1_500)

    assert decision.recipients == ("yin-event",)


def test_missing_or_null_lease_is_not_routable():
    registry = IdentityRegistry()
    registry.register_identity("yin", display_name="Yin")
    _register_node(
        registry,
        "yin-no-lease",
        last_heartbeat_ms=None,
        lease_expires_ms=None,
    )
    registry.subscribe("yin-no-lease", domain="database", intent="event", min_priority=4)

    assert Router(registry).route(_env(), now_ms=1_500).recipients == ()


def test_expired_lease_is_not_routable():
    registry = IdentityRegistry()
    registry.register_identity("yin", display_name="Yin")
    _register_node(registry, "yin-expired", lease_expires_ms=1_499)
    registry.subscribe("yin-expired", domain="database", intent="event", min_priority=4)

    assert Router(registry).route(_env(), now_ms=1_500).recipients == ()


def test_paused_and_offline_nodes_are_not_routable_even_with_live_lease():
    registry = IdentityRegistry()
    registry.register_identity("yin", display_name="Yin")
    _register_node(registry, "yin-paused", status=NodeStatus.PAUSED)
    _register_node(registry, "yin-offline", status=NodeStatus.OFFLINE)
    registry.subscribe("yin-paused", domain="database", intent="event", min_priority=4)
    registry.subscribe("yin-offline", domain="database", intent="event", min_priority=4)

    assert Router(registry).route(_env(), now_ms=1_500).recipients == ()


def test_wildcard_intent_subscription_matches_any_intent_on_that_node_only():
    registry = IdentityRegistry()
    registry.register_identity("yin", display_name="Yin")
    _register_node(registry, "yin-any")
    _register_node(registry, "yin-event")
    registry.subscribe("yin-any", domain="database", intent=None, min_priority=4)
    registry.subscribe("yin-event", domain="database", intent="event", min_priority=4)

    decision = Router(registry).route(_env(intent="command"), now_ms=1_500)

    assert decision.recipients == ("yin-any",)


def test_identity_named_subscription_is_only_compatibly_bound_when_unambiguous():
    registry = IdentityRegistry()
    registry.register_identity("yin", display_name="Yin")
    _register_node(registry, "yin-one")
    sub = registry.subscribe("yin", domain="database", intent="event", min_priority=4)
    assert sub.node_id == "yin-one"

    _register_node(registry, "yin-two")
    with pytest.raises(RegistryError, match="AMBIGUOUS_SUBSCRIPTION_TARGET"):
        registry.subscribe("yin", domain="database", intent="command", min_priority=4)


def test_invalid_node_lease_times_fail_closed():
    registry = IdentityRegistry()
    registry.register_identity("yin", display_name="Yin")

    with pytest.raises(RegistryError, match="INVALID_NODE_LEASE_TIME"):
        _register_node(registry, "yin-bool-heartbeat", last_heartbeat_ms=True)
    with pytest.raises(RegistryError, match="INVALID_NODE_LEASE_TIME"):
        _register_node(
            registry,
            "yin-backwards-lease",
            last_heartbeat_ms=1_000,
            lease_expires_ms=999,
        )


def test_route_time_rejects_boolean_int_coercion():
    registry = IdentityRegistry()
    registry.register_identity("yin", display_name="Yin")
    _register_node(registry, "yin-event")
    registry.subscribe("yin-event", domain="database", intent="event", min_priority=4)

    with pytest.raises(ValueError, match="INVALID_ROUTE_TIME"):
        Router(registry).route(_env(), now_ms=True)
