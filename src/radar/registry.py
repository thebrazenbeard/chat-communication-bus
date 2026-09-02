"""Radar logical identity, node, endpoint, and subscription registry."""

from __future__ import annotations

from dataclasses import replace

from .model import Endpoint, Identity, Node, NodeStatus, Subscription


class RegistryError(ValueError):
    pass


def normalize_identifier(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RegistryError("INVALID_IDENTIFIER")
    return value.strip().casefold()


class IdentityRegistry:
    def __init__(self) -> None:
        self._identities: dict[str, Identity] = {}
        self._aliases: dict[str, str] = {}
        self._nodes: dict[str, Node] = {}
        self._endpoints: dict[str, Endpoint] = {}
        self._subscriptions: list[Subscription] = []

    def register_identity(
        self,
        identity_id: str,
        *,
        display_name: str,
        aliases: tuple[str, ...] = (),
    ) -> Identity:
        canonical = normalize_identifier(identity_id)
        if canonical in self._identities or canonical in self._aliases:
            raise RegistryError("IDENTITY_COLLISION")
        if not isinstance(display_name, str) or not display_name.strip():
            raise RegistryError("DISPLAY_NAME_REQUIRED")

        normalized_aliases: list[str] = []
        for alias in aliases:
            normalized = normalize_identifier(alias)
            if (
                normalized == canonical
                or normalized in self._identities
                or normalized in self._aliases
                or normalized in normalized_aliases
            ):
                raise RegistryError("ALIAS_COLLISION")
            normalized_aliases.append(normalized)

        identity = Identity(canonical, display_name.strip(), tuple(normalized_aliases))
        self._identities[canonical] = identity
        for alias in normalized_aliases:
            self._aliases[alias] = canonical
        return identity

    def resolve_identity_id(self, value: str) -> str:
        key = normalize_identifier(value)
        if key in self._identities:
            return key
        canonical = self._aliases.get(key)
        if canonical is None:
            raise RegistryError("UNKNOWN_IDENTITY")
        return canonical

    def identity(self, identity_id: str) -> Identity:
        return self._identities[self.resolve_identity_id(identity_id)]

    def register_node(
        self,
        node_id: str,
        *,
        identity_id: str,
        status: NodeStatus = NodeStatus.ONLINE,
    ) -> Node:
        canonical_node = normalize_identifier(node_id)
        canonical_identity = self.resolve_identity_id(identity_id)
        if canonical_node in self._nodes:
            raise RegistryError("NODE_COLLISION")
        if not isinstance(status, NodeStatus):
            status = NodeStatus(status)
        node = Node(canonical_node, canonical_identity, status)
        self._nodes[canonical_node] = node
        return node

    def node(self, node_id: str) -> Node:
        key = normalize_identifier(node_id)
        try:
            return self._nodes[key]
        except KeyError as exc:
            raise RegistryError("UNKNOWN_NODE") from exc

    def set_node_status(self, node_id: str, status: NodeStatus) -> Node:
        current = self.node(node_id)
        if not isinstance(status, NodeStatus):
            status = NodeStatus(status)
        updated = replace(current, status=status)
        self._nodes[current.node_id] = updated
        return updated

    def register_endpoint(
        self,
        endpoint_id: str,
        *,
        identity_id: str,
        transport: str,
        address: str,
    ) -> Endpoint:
        canonical_endpoint = normalize_identifier(endpoint_id)
        canonical_identity = self.resolve_identity_id(identity_id)
        if canonical_endpoint in self._endpoints:
            raise RegistryError("ENDPOINT_COLLISION")
        if not isinstance(transport, str) or not transport.strip():
            raise RegistryError("TRANSPORT_REQUIRED")
        if not isinstance(address, str) or not address.strip():
            raise RegistryError("ADDRESS_REQUIRED")
        endpoint = Endpoint(
            canonical_endpoint,
            canonical_identity,
            transport.strip().casefold(),
            address.strip(),
        )
        self._endpoints[canonical_endpoint] = endpoint
        return endpoint

    def endpoint(self, endpoint_id: str) -> Endpoint:
        key = normalize_identifier(endpoint_id)
        try:
            return self._endpoints[key]
        except KeyError as exc:
            raise RegistryError("UNKNOWN_ENDPOINT") from exc

    def subscribe(self, identity_id: str, *, domain: str, min_priority: int = 3) -> Subscription:
        canonical_identity = self.resolve_identity_id(identity_id)
        if not isinstance(domain, str) or not domain.strip():
            raise RegistryError("DOMAIN_REQUIRED")
        if not 0 <= int(min_priority) <= 4:
            raise RegistryError("INVALID_PRIORITY")
        sub = Subscription(canonical_identity, domain.strip().casefold(), int(min_priority))
        if sub not in self._subscriptions:
            self._subscriptions.append(sub)
        return sub

    def subscriptions_for_domain(self, domain: str, priority: int) -> tuple[Subscription, ...]:
        key = domain.strip().casefold()
        return tuple(
            sub
            for sub in self._subscriptions
            if sub.domain == key and priority <= sub.min_priority
        )

    def identities(self) -> tuple[Identity, ...]:
        return tuple(self._identities[key] for key in sorted(self._identities))


__all__ = ["IdentityRegistry", "NodeStatus", "RegistryError", "normalize_identifier"]
