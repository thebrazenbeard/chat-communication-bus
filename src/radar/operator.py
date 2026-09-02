"""ChatGPT-facing operator projections for Radar."""

from __future__ import annotations


BOOTSTRAP_ORDER = ("contract", "github", "provider", "reconcile", "exceptions", "continue")


class RadarOperator:
    def status(
        self,
        *,
        identity_count: int,
        online_node_count: int,
        chat_session_active: bool,
        **extra: object,
    ) -> dict[str, object]:
        status: dict[str, object] = {
            "identity_count": int(identity_count),
            "online_node_count": int(online_node_count),
            "chat_session_active": bool(chat_session_active),
        }
        status.update(extra)
        return status

    def health(self, *, findings: tuple[object, ...] = ()) -> dict[str, object]:
        return {"finding_count": len(findings), "findings": findings}

    def dependencies(self, *, ready: tuple[str, ...] = (), waiting: tuple[str, ...] = ()) -> dict[str, object]:
        return {"ready": ready, "waiting": waiting}

    def dlq(self, *, pending: int = 0) -> dict[str, object]:
        return {"pending": int(pending)}

    def audit(self, *, findings: tuple[object, ...] = ()) -> dict[str, object]:
        return {"finding_count": len(findings), "findings": findings}

    def reconcile(self, reconciler: object, github_state: dict[str, object], provider_state: dict[str, object]) -> tuple[object, ...]:
        return tuple(reconciler.compare(github_state, provider_state))


__all__ = ["BOOTSTRAP_ORDER", "RadarOperator"]
