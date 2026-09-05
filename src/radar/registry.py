"""Radar logical identity, node, endpoint, and subscription registry."""

from __future__ import annotations

from dataclasses import replace
import threading

from .model import Endpoint, Identity, Node, NodeStatus, Subscription


ROUTABLE_NODE_STATUSES = frozenset(
    {
        NodeStatus.ONLINE,
        NodeStatus.IDLE,
        NodeStatus.WORKING,
        NodeStatus.WAITING_DEPENDENCY,
        NodeStatus.DEGRADED,
    }
)


class RegistryError(ValueError):
    """Errors raised by the registry use short string codes as messages."""


def normalize_identifier(value: str) -> str:
    """Normalize an identifier to stripped, casefolded text."""
    if not isinstance(value, str) or not value.strip():
        raise RegistryError("INVALID_IDENTIFIER")
    return value.strip().casefold()


def _priority_value(value: object) -> int:
    """Parse priority without accepting Python booleans as integers."""
    if isinstance(value, bool):
        raise RegistryError("INVALID_PRIORITY")
    try:
        priority = int(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise RegistryError("INVALID_PRIORITY") from exc
    if not 0 <= priority <= 4:
        raise RegistryError("INVALID_PRIORITY")
    return priority


class IdentityRegistry:
    """Thread-safe registry for identities, nodes, endpoints and subscriptions."""

    def __init__(self) -> None:
        self._identities: dict[str, Identity] = {}
        self._aliases: dict[str, str] = {}
        self._nodes: dict[str, Node] = {}
        self._endpoints: dict[str, Endpoint] = {}
        self._subscriptions: list[Subscription] = []
        self._lock = threading.RLock()

    def register_identity(
        self,
        identity_id: str,
        *,
        display_name: str,
        aliases: tuple[str, ...] = (),
    ) -> Identity:
        """Register an identity while making alias ownership atomic."""
        canonical = normalize_identifier(identity_id)
        if not isinstance(display_name, str) or not display_name.strip():
            raise RegistryError("DISPLAY_NAME_REQUIRED")

        normalized_aliases: list[str] = []
        for alias in aliases:
            normalized = normalize_identifier(alias)
            # Input-local collisions can be rejected before taking the lock.
            if normalized == canonical or normalized in normalized_aliases:
                raise RegistryError("ALIAS_COLLISION")
            normalized_aliases.append(normalized)

        identity = Identity(canonical, display_name.strip(), tuple(normalized_aliases))
        with self._lock:
            # Registry-dependent checks must happen under the same lock as the
            # writes. Otherwise two registrations can both preflight the same
            # free alias and the later writer silently steals it.
            if canonical in self._identities or canonical in self._aliases:
                raise RegistryError("IDENTITY_COLLISION")
            for alias in normalized_aliases:
                if alias in self._identities or alias in self._aliases:
                    raise RegistryError("ALIAS_COLLISION")

            self._identities[canonical] = identity
            for alias in normalized_aliases:
                self._aliases[alias] = canonical
        return identity

    def resolve_identity_id(self, value: str) -> str:
        key = normalize_identifier(value)
        with self._lock:
            if key in self._identities:
                return key
            canonical = self._aliases.get(key)
            if canonical is None:
                raise RegistryError("UNKNOWN_IDENTITY")
            return canonical

    def identity(self, identity_id: str) -> Identity:
        canonical = self.resolve_identity_id(identity_id)
        with self._lock:
            try:
                return self._identities[canonical]
            except KeyError as exc:
                raise RegistryError("UNKNOWN_IDENTITY") from exc

    def register_node(
        self,
        node_id: str,
        *,
        identity_id: str,
        status: NodeStatus = NodeStatus.ONLINE,
    ) -> Node:
        canonical_node = normalize_identifier(node_id)
        canonical_identity = self.resolve_identity_id(identity_id)
        with self._lock:
            if canonical_node in self._nodes:
                raise RegistryError("NODE_COLLISION")
            try:
                if not isinstance(status, NodeStatus):
                    status = NodeStatus(status)
            except Exception as exc:
                raise RegistryError("INVALID_NODE_STATUS") from exc
            node = Node(canonical_node, canonical_identity, status)
            self._nodes[canonical_node] = node
        return node

    def node(self, node_id: str) -> Node:
        key = normalize_identifier(node_id)
        with self._lock:
            try:
                return self._nodes[key]
            except KeyError as exc:
                raise RegistryError("UNKNOWN_NODE") from exc

    def nodes_for_identity(self, identity_id: str) -> tuple[Node, ...]:
        canonical = self.resolve_identity_id(identity_id)
        with self._lock:
            nodes = [n for n in self._nodes.values() if n.identity_id == canonical]
        return tuple(sorted(nodes, key=lambda n: n.node_id))

    def identity_has_routable_node(self, identity_id: str) -> bool:
        canonical = self.resolve_identity_id(identity_id)
        with self._lock:
            return any(
                n.status in ROUTABLE_NODE_STATUSES
                for n in self._nodes.values()
                if n.identity_id == canonical
            )

    def set_node_status(self, node_id: str, status: NodeStatus) -> Node:
        with self._lock:
            current = self.node(node_id)
            try:
                if not isinstance(status, NodeStatus):
                    status = NodeStatus(status)
            except Exception as exc:
                raise RegistryError("INVALID_NODE_STATUS") from exc
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
        with self._lock:
            if canonical_endpoint in self._endpoints:
                raise RegistryError("ENDPOINT_COLLISION")
            self._endpoints[canonical_endpoint] = endpoint
        return endpoint

    def endpoint(self, endpoint_id: str) -> Endpoint:
        key = normalize_identifier(endpoint_id)
        with self._lock:
            try:
                return self._endpoints[key]
            except KeyError as exc:
                raise RegistryError("UNKNOWN_ENDPOINT") from exc

    def subscribe(
        self,
        identity_id: str,
        *,
        domain: str,
        min_priority: int = 3,
    ) -> Subscription:
        canonical_identity = self.resolve_identity_id(identity_id)
        if not isinstance(domain, str) or not domain.strip():
            raise RegistryError("DOMAIN_REQUIRED")
        min_pr = _priority_value(min_priority)
        sub = Subscription(canonical_identity, domain.strip().casefold(), min_pr)
        with self._lock:
            if sub not in self._subscriptions:
                self._subscriptions.append(sub)
        return sub

    def subscriptions_for_domain(
        self,
        domain: str,
        priority: int,
    ) -> tuple[Subscription, ...]:
        """Return subscriptions accepting the numeric priority.

        Lower numeric values are more urgent. A subscription with min_priority
        3 therefore accepts priorities 0 through 3.
        """
        if not isinstance(domain, str) or not domain.strip():
            raise RegistryError("DOMAIN_REQUIRED")
        pr = _priority_value(priority)
        key = domain.strip().casefold()
        with self._lock:
            return tuple(
                sub
                for sub in self._subscriptions
                if sub.domain == key and pr <= sub.min_priority
            )

    def identity_is_subscribed(
        self,
        identity_id: str,
        *,
        domain: str,
        priority: int,
    ) -> bool:
        canonical = self.resolve_identity_id(identity_id)
        return any(
            sub.identity_id == canonical
            for sub in self.subscriptions_for_domain(domain, priority)
        )

    def identities(self) -> tuple[Identity, ...]:
        with self._lock:
            return tuple(self._identities[key] for key in sorted(self._identities))


__all__ = [
    "IdentityRegistry",
    "NodeStatus",
    "ROUTABLE_NODE_STATUSES",
    "RegistryError",
    "normalize_identifier",
]
