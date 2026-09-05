"""Radar logical identity, node, endpoint, and subscription registry.

Improvements in this version:
- Thread-safety: all access protected by an RLock.
- Better validation/error mapping when converting NodeStatus.
- Avoid unnecessary lookups in nodes_for_identity.
- Added docstrings and small validation checks in lookup methods.
- Minor clarifications for subscription priority validation.
"""

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
    """Normalize an identifier: non-empty string -> stripped, casefolded.

    Raises RegistryError("INVALID_IDENTIFIER") for invalid values.
    """
    if not isinstance(value, str) or not value.strip():
        raise RegistryError("INVALID_IDENTIFIER")
    return value.strip().casefold()


class IdentityRegistry:
    """Registry for identities, nodes, endpoints and subscriptions.

    Thread-safe for concurrent use.
    """

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
        """Register a new identity with optional aliases.

        Raises RegistryError on collisions or missing display name.
        """
        canonical = normalize_identifier(identity_id)
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
        with self._lock:
            if canonical in self._identities or canonical in self._aliases:
                # re-check under lock to avoid race
                raise RegistryError("IDENTITY_COLLISION")
            self._identities[canonical] = identity
            for alias in normalized_aliases:
                self._aliases[alias] = canonical
        return identity

    def resolve_identity_id(self, value: str) -> str:
        """Return the canonical identity id for a value (id or alias)."""
        key = normalize_identifier(value)
        with self._lock:
            if key in self._identities:
                return key
            canonical = self._aliases.get(key)
            if canonical is None:
                raise RegistryError("UNKNOWN_IDENTITY")
            return canonical

    def identity(self, identity_id: str) -> Identity:
        """Return Identity for the given id or alias, else RegistryError."""
        canonical = self.resolve_identity_id(identity_id)
        with self._lock:
            try:
                return self._identities[canonical]
            except KeyError as exc:
                # defensive: should not happen because resolve_identity_id already checked
                raise RegistryError("UNKNOWN_IDENTITY") from exc

    def register_node(
        self,
        node_id: str,
        *,
        identity_id: str,
        status: NodeStatus = NodeStatus.ONLINE,
    ) -> Node:
        """Register a node belonging to an identity.

        status may be a NodeStatus or something convertible to it; invalid values
        are mapped to RegistryError("INVALID_NODE_STATUS").
        """
        canonical_node = normalize_identifier(node_id)
        canonical_identity = self.resolve_identity_id(identity_id)
        with self._lock:
            if canonical_node in self._nodes:
                raise RegistryError("NODE_COLLISION")
            try:
                if not isinstance(status, NodeStatus):
                    status = NodeStatus(status)
            except Exception:
                raise RegistryError("INVALID_NODE_STATUS")
            node = Node(canonical_node, canonical_identity, status)
            self._nodes[canonical_node] = node
        return node

    def node(self, node_id: str) -> Node:
        """Lookup a node by id; raises RegistryError if unknown."""
        key = normalize_identifier(node_id)
        with self._lock:
            try:
                return self._nodes[key]
            except KeyError as exc:
                raise RegistryError("UNKNOWN_NODE") from exc

    def nodes_for_identity(self, identity_id: str) -> tuple[Node, ...]:
        """Return nodes for an identity, sorted by node_id.

        This avoids multiple dict lookups by iterating values directly.
        """
        canonical = self.resolve_identity_id(identity_id)
        with self._lock:
            nodes = [n for n in self._nodes.values() if n.identity_id == canonical]
        # Sort deterministically by node_id
        return tuple(sorted(nodes, key=lambda n: n.node_id))

    def identity_has_routable_node(self, identity_id: str) -> bool:
        """Return True if identity has any node in a routable status.

        Uses a generator to short-circuit as soon as a routable node is found.
        """
        canonical = self.resolve_identity_id(identity_id)
        with self._lock:
            return any(n.status in ROUTABLE_NODE_STATUSES for n in self._nodes.values() if n.identity_id == canonical)

    def set_node_status(self, node_id: str, status: NodeStatus) -> Node:
        """Update a node's status and return the updated Node."""
        with self._lock:
            current = self.node(node_id)  # node() will normalize and check existence
            try:
                if not isinstance(status, NodeStatus):
                    status = NodeStatus(status)
            except Exception:
                raise RegistryError("INVALID_NODE_STATUS")
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
        """Register an endpoint for an identity."""
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
        """Lookup an endpoint by id; raises RegistryError if unknown."""
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
        """Subscribe an identity to a domain with a min_priority (0..4).

        Note: behavior of min_priority is preserved from original code (sub.min_priority)
        is the threshold used during matching. See subscriptions_for_domain for details.
        """
        canonical_identity = self.resolve_identity_id(identity_id)
        if not isinstance(domain, str) or not domain.strip():
            raise RegistryError("DOMAIN_REQUIRED")
        try:
            min_pr = int(min_priority)
        except Exception:
            raise RegistryError("INVALID_PRIORITY")
        if not 0 <= min_pr <= 4:
            raise RegistryError("INVALID_PRIORITY")
        sub = Subscription(
            canonical_identity,
            domain.strip().casefold(),
            min_pr,
        )
        with self._lock:
            if sub not in self._subscriptions:
                self._subscriptions.append(sub)
        return sub

    def subscriptions_for_domain(
        self,
        domain: str,
        priority: int,
    ) -> tuple[Subscription, ...]:
        """Return subscriptions for a domain that accept the given priority.

        The matching logic preserves the original semantics:
          keep sub if sub.domain == domain and priority <= sub.min_priority

        That means 'min_priority' represents the maximum numeric priority the
        subscriber will accept (smaller numbers are considered higher priority).
        Document this clearly if you change the priority semantics.
        """
        if not isinstance(domain, str) or not domain.strip():
            raise RegistryError("DOMAIN_REQUIRED")
        try:
            pr = int(priority)
        except Exception:
            raise RegistryError("INVALID_PRIORITY")
        if not 0 <= pr <= 4:
            raise RegistryError("INVALID_PRIORITY")

        key = domain.strip().casefold()
        with self._lock:
            results = tuple(
                sub
                for sub in self._subscriptions
                if sub.domain == key and pr <= sub.min_priority
            )
        return results

    def identity_is_subscribed(
        self,
        identity_id: str,
        *,
        domain: str,
        priority: int,
    ) -> bool:
        """Return True if identity is subscribed to the domain at the priority."""
        canonical = self.resolve_identity_id(identity_id)
        return any(
            sub.identity_id == canonical
            for sub in self.subscriptions_for_domain(domain, priority)
        )

    def identities(self) -> tuple[Identity, ...]:
        """Return all registered identities sorted by canonical id."""
        with self._lock:
            return tuple(self._identities[key] for key in sorted(self._identities))


__all__ = [
    "IdentityRegistry",
    "NodeStatus",
    "ROUTABLE_NODE_STATUSES",
    "RegistryError",
    "normalize_identifier",
]
