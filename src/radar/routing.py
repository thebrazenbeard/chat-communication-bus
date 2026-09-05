"""Deterministic Radar routing, priority ordering, and deduplication."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
import heapq
import itertools
import threading

from .envelope import RadarEnvelope
from .registry import IdentityRegistry, RegistryError


@dataclass(frozen=True)
class RouteDecision:
    recipients: tuple[str, ...]
    priority: int
    authority_ref: str | None


class Router:
    """Resolve an envelope through subscriptions and current routable nodes."""

    def __init__(self, registry: IdentityRegistry) -> None:
        self.registry = registry

    def _authorized_and_routable(self, identity_id: str, envelope: RadarEnvelope) -> bool:
        return self.registry.identity_is_subscribed(
            identity_id,
            domain=envelope.domain,
            priority=envelope.priority,
        ) and self.registry.identity_has_routable_node(identity_id)

    def route(self, envelope: RadarEnvelope) -> RouteDecision:
        if envelope.audience:
            recipients: list[str] = []
            seen: set[str] = set()
            for audience in envelope.audience:
                try:
                    identity_id = self.registry.resolve_identity_id(audience)
                except RegistryError:
                    continue
                if identity_id in seen:
                    continue
                if self._authorized_and_routable(identity_id, envelope):
                    recipients.append(identity_id)
                    seen.add(identity_id)
        else:
            recipients = sorted(
                {
                    sub.identity_id
                    for sub in self.registry.subscriptions_for_domain(
                        envelope.domain,
                        envelope.priority,
                    )
                    if self.registry.identity_has_routable_node(sub.identity_id)
                }
            )
        return RouteDecision(tuple(recipients), envelope.priority, envelope.authority_ref)


class PriorityQueue:
    """Bounded deterministic queue; lower numeric priority executes first.

    ``push`` returns the envelope displaced by a priority-zero admission, if any,
    so the caller can account for the drop in durable telemetry rather than
    silently losing background work.
    """

    def __init__(self, max_size: int = 1024) -> None:
        if type(max_size) is not int or max_size <= 0:
            raise ValueError("max_size must be positive")
        self.max_size = max_size
        self._counter = itertools.count()
        self._heap: list[tuple[int, int, RadarEnvelope]] = []
        self._lock = threading.Lock()

    def push(self, envelope: RadarEnvelope) -> RadarEnvelope | None:
        with self._lock:
            # Admission sequence allocation belongs to the same critical section
            # as the heap mutation; otherwise the class is not truly thread-safe.
            counter = next(self._counter)
            evicted: RadarEnvelope | None = None
            if len(self._heap) >= self.max_size:
                if envelope.priority != 0:
                    raise OverflowError("RADAR_QUEUE_FULL")

                victim = max(self._heap, key=lambda item: (item[0], item[1]))
                if victim[0] == 0:
                    raise OverflowError("RADAR_QUEUE_FULL")
                self._heap.remove(victim)
                heapq.heapify(self._heap)
                evicted = victim[2]

            heapq.heappush(self._heap, (envelope.priority, counter, envelope))
            return evicted

    def pop(self) -> RadarEnvelope:
        with self._lock:
            if not self._heap:
                raise IndexError("RADAR_QUEUE_EMPTY")
            return heapq.heappop(self._heap)[2]

    def peek(self) -> RadarEnvelope:
        with self._lock:
            if not self._heap:
                raise IndexError("RADAR_QUEUE_EMPTY")
            return self._heap[0][2]

    def is_full(self) -> bool:
        with self._lock:
            return len(self._heap) >= self.max_size

    def clear(self) -> None:
        with self._lock:
            self._heap.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._heap)


class DedupeWindow:
    """Thread-safe 500 ms style duplicate suppression using a monotonic clock."""

    def __init__(self, *, window_ms: int = 500) -> None:
        if type(window_ms) is not int or window_ms < 0:
            raise ValueError("window_ms must be non-negative")
        self.window_ms = window_ms
        self._seen: OrderedDict[str, int] = OrderedDict()
        self._last_now_ms: int | None = None
        self._lock = threading.Lock()

    def accept(self, idempotency_key: str, now_ms: int) -> bool:
        if not isinstance(idempotency_key, str) or not idempotency_key:
            raise ValueError("INVALID_DEDUPE_KEY")
        if type(now_ms) is not int or now_ms < 0:
            raise ValueError("INVALID_DEDUPE_TIME")

        with self._lock:
            if self._last_now_ms is not None and now_ms < self._last_now_ms:
                raise ValueError("DEDUPE_CLOCK_REGRESSION")
            self._last_now_ms = now_ms

            previous = self._seen.get(idempotency_key)
            if previous is not None and now_ms - previous <= self.window_ms:
                return False

            self._seen[idempotency_key] = now_ms
            self._seen.move_to_end(idempotency_key)
            cutoff = now_ms - self.window_ms
            while self._seen:
                oldest_key, oldest_seen = next(iter(self._seen.items()))
                if oldest_seen >= cutoff:
                    break
                if oldest_key == idempotency_key:
                    break
                self._seen.popitem(last=False)
            return True

    def __len__(self) -> int:
        with self._lock:
            return len(self._seen)


__all__ = ["DedupeWindow", "PriorityQueue", "RouteDecision", "Router"]
