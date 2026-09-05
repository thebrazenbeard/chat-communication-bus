"""ChatGPT-facing operator projections for Radar.

This module provides small, stateless projection helpers for formatting operator
state for human or machine consumers. Methods are declared as staticmethods so
callers do not need to instantiate RadarOperator.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Protocol, Sequence, Tuple


BOOTSTRAP_ORDER: Tuple[str, ...] = (
    "contract",
    "github",
    "provider",
    "reconcile",
    "exceptions",
    "continue",
)


class Reconciler(Protocol):
    """Protocol describing the minimal interface required from a reconciler.

    The reconciler must implement a `compare(github_state, provider_state)`
    method that returns an iterable of findings/results.
    """

    def compare(self, github_state: Mapping[str, Any], provider_state: Mapping[str, Any]) -> Iterable[Any]:
        ...


class RadarOperator:
    """Projection helpers for formatting Radar operator state.

    These helpers are stateless and therefore defined as staticmethods so
    consumers can call them without creating an instance.
    """

    @staticmethod
    def status(
        *,
        identity_count: int,
        online_node_count: int,
        chat_session_active: bool,
        **extra: Any,
    ) -> Dict[str, Any]:
        """Return a summary status dictionary.

        Primary fields are coerced to primitive types for predictable JSON
        serialization. Extra keys can be provided via ``extra`` and will be
        merged into the resulting mapping.
        """
        status: Dict[str, Any] = {
            "identity_count": int(identity_count),
            "online_node_count": int(online_node_count),
            "chat_session_active": bool(chat_session_active),
        }
        status.update(extra)
        return status

    @staticmethod
    def health(*, findings: Sequence[Any] = ()) -> Dict[str, Any]:
        """Return a health projection.

        Findings are returned as a list to make JSON serialization explicit and
        predictable.
        """
        findings_list: List[Any] = list(findings)
        return {"finding_count": len(findings_list), "findings": findings_list}

    @staticmethod
    def dependencies(*, ready: Sequence[str] = (), waiting: Sequence[str] = ()) -> Dict[str, Any]:
        """Return dependency readiness information.

        Returns lists (not tuples) for clearer downstream consumption.
        """
        return {"ready": list(ready), "waiting": list(waiting)}

    @staticmethod
    def dlq(*, pending: int = 0) -> Dict[str, Any]:
        """Return dead-letter queue metrics."""
        return {"pending": int(pending)}

    @staticmethod
    def audit(*, findings: Sequence[Any] = ()) -> Dict[str, Any]:
        """Return an audit projection similar to :meth:`health`."""
        findings_list: List[Any] = list(findings)
        return {"finding_count": len(findings_list), "findings": findings_list}

    @staticmethod
    def reconcile(
        reconciler: Reconciler, github_state: Mapping[str, Any], provider_state: Mapping[str, Any]
    ) -> Tuple[Any, ...]:
        """Run ``reconciler.compare`` and return its results as a tuple.

        The reconciler must implement the :class:`Reconciler` protocol.
        """
        return tuple(reconciler.compare(github_state, provider_state))


__all__ = ["BOOTSTRAP_ORDER", "Reconciler", "RadarOperator"]
