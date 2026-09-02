"""Deterministic Radar routing, priority ordering, and deduplication."""

from __future__ import annotations

from dataclasses import dataclass
import heapq
import itertools

from .envelope import RadarEnvelope
from .registry import IdentityRegistry, RegistryError


@dataclass(frozen=True)
class RouteDecision:
    recipients: tuple[str, ...]
    priority: int
    authority_ref: str | None


class Router:
    def __init__(self, registry: IdentityRegistry) -> None:
        self.registry = registry

    def route(self, envelope: RadarEnvelope) -> RouteDecision:
        if envelope.audience:
            recipients: list[str] = []
            for audience in envelope.audience:
                try:
                    identity_id = self.registry.resolve_identity_id(audience)
                except RegistryError:
                    continue
                if identity_id not in recipients:
                    recipients.append(identity_id)
        else:
            recipients = sorted(
                {
                    sub.identity_id
                    for sub in self.registry.subscriptions_for_domain(
                        envelope.domain, envelope.priority
                    )
                }
            )
        return RouteDecision(tuple(recipients), envelope.priority, envelope.authority_ref)


class PriorityQueue:
    """Small deterministic in-process queue. Lower numeric priority runs first."""

    def __init__(self, max_size: int = 1024) -> None:
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        self.max_size = max_size
        self._counter = itertools.count()
        self._heap: list[tuple[int, int, RadarEnvelope]] = []

    def push(self, envelope: RadarEnvelope) -> None:
        if len(self._heap) >= self.max_size:
            raise OverflowError("RADAR_QUEUE_FULL")
        heapq.heappush(self._heap, (envelope.priority, next(self._counter), envelope))

    def pop(self) -> RadarEnvelope:
        if not self._heap:
            raise IndexError("RADAR_QUEUE_EMPTY")
        return heapq.heappop(self._heap)[2]

    def __len__(self) -> int:
        return len(self._heap)


class DedupeWindow:
    def __init__(self, *, window_ms: int = 500) -> None:
        if window_ms < 0:
            raise ValueError("window_ms must be non-negative")
        self.window_ms = window_ms
        self._seen: dict[str, int] = {}

    def accept(self, idempotency_key: str, now_ms: int) -> bool:
        previous = self._seen.get(idempotency_key)
        if previous is not None and now_ms - previous <= self.window_ms:
            return False
        self._seen[idempotency_key] = now_ms
        cutoff = now_ms - self.window_ms
        stale = [key for key, seen_at in self._seen.items() if seen_at < cutoff]
        for key in stale:
            if key != idempotency_key:
                self._seen.pop(key, None)
        return True


__all__ = ["DedupeWindow", "PriorityQueue", "RouteDecision", "Router"]
