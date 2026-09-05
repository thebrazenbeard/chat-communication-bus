"""Deterministic Radar routing, priority ordering, and deduplication."""

from __future__ import annotations

from dataclasses import dataclass
from collections import OrderedDict
import heapq
import itertools
import threading
from typing import Optional, Tuple, List

from .envelope import RadarEnvelope
from .registry import IdentityRegistry, RegistryError


@dataclass(frozen=True)
class RouteDecision:
    """Decision produced by Router: recipients (identity ids), priority, authority_ref."""
    recipients: tuple[str, ...]
    priority: int
    authority_ref: Optional[str]


class Router:
    """Resolve an envelope to recipients using an IdentityRegistry."""

    def __init__(self, registry: IdentityRegistry) -> None:
        self.registry = registry

    def _authorized_and_routable(self, identity_id: str, envelope: RadarEnvelope) -> bool:
        return self.registry.identity_is_subscribed(
            identity_id,
            domain=envelope.domain,
            priority=envelope.priority,
        ) and self.registry.identity_has_routable_node(identity_id)

    def route(self, envelope: RadarEnvelope) -> RouteDecision:
        """
        Determine the recipients for an envelope.

        - If envelope.audience is set, preserve the audience order but deduplicate
          duplicate resolved identity IDs (first occurrence wins).
        - Otherwise include all subscribers for the envelope domain/priority that
          have a routable node; results are sorted for deterministic ordering.
        """
        if envelope.audience:
            recipients_list: List[str] = []
            seen: set[str] = set()
            for audience in envelope.audience:
                try:
                    identity_id = self.registry.resolve_identity_id(audience)
                except RegistryError:
                    continue
                if identity_id in seen:
                    continue
                if self._authorized_and_routable(identity_id, envelope):
                    recipients_list.append(identity_id)
                    seen.add(identity_id)
            recipients = tuple(recipients_list)
        else:
            recipients = tuple(
                sorted(
                    {
                        sub.identity_id
                        for sub in self.registry.subscriptions_for_domain(
                            envelope.domain,
                            envelope.priority,
                        )
                        if self.registry.identity_has_routable_node(sub.identity_id)
                    }
                )
            )
        return RouteDecision(recipients, envelope.priority, envelope.authority_ref)


class PriorityQueue:
    """Small deterministic in-process queue. Lower numeric priority runs first.

    Thread-safe for concurrent push/pop. Lower numeric value is higher urgency
    (i.e. runs first). Priority zero is reserved for halt/security-class dispatch
    and may evict less urgent queued items when the queue is full.
    """

    def __init__(self, max_size: int = 1024) -> None:
        if max_size <= 0:
            raise ValueError("max_size must be positive")
        self.max_size = max_size
        self._counter = itertools.count()
        # heap items are tuples: (priority, admission_counter, envelope)
        self._heap: list[tuple[int, int, RadarEnvelope]] = []
        self._lock = threading.Lock()

    def push(self, envelope: RadarEnvelope) -> None:
        """Push an envelope. May evict a non-zero-priority victim when inserting a priority 0."""
        counter = next(self._counter)
        with self._lock:
            if len(self._heap) >= self.max_size:
                # non-zero priorities cannot be admitted when full
                if envelope.priority != 0:
                    raise OverflowError("RADAR_QUEUE_FULL")

                # Priority zero may displace the deterministic victim:
                # - victim chosen as the largest (priority, counter) so highest numeric priority
                #   (least urgent) and, among ties, the newest admission.
                victim = max(self._heap, key=lambda item: (item[0], item[1]))
                # never evict existing priority-zero entries
                if victim[0] == 0:
                    raise OverflowError("RADAR_QUEUE_FULL")
                # remove victim and re-heapify
                self._heap.remove(victim)
                heapq.heapify(self._heap)

            heapq.heappush(self._heap, (envelope.priority, counter, envelope))

    def pop(self) -> RadarEnvelope:
        """Pop the next envelope (raises IndexError if empty)."""
        with self._lock:
            if not self._heap:
                raise IndexError("RADAR_QUEUE_EMPTY")
            return heapq.heappop(self._heap)[2]

    def peek(self) -> RadarEnvelope:
        """Return the next envelope without removing it (raises IndexError if empty)."""
        with self._lock:
            if not self._heap:
                raise IndexError("RADAR_QUEUE_EMPTY")
            return self._heap[0][2]

    def is_full(self) -> bool:
        """Return True when the queue is at capacity."""
        with self._lock:
            return len(self._heap) >= self.max_size

    def clear(self) -> None:
        """Remove all queued items."""
        with self._lock:
            self._heap.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._heap)


class DedupeWindow:
    """Time-windowed idempotency/deduplication.

    Accepts idempotency keys with a timestamp in milliseconds (now_ms). Returns True
    if the key is accepted (not seen within window_ms), and False if it's a duplicate
    within the configured window.

    Performance:
    - Uses an OrderedDict to keep insertion order and prune stale entries efficiently.
    - Expects now_ms to be a monotonically increasing millisecond timestamp (e.g., from
      time.monotonic_ns() // 1_000_000 or a monotonic ms clock).
    """

    def __init__(self, *, window_ms: int = 500) -> None:
        if window_ms < 0:
            raise ValueError("window_ms must be non-negative")
        self.window_ms = window_ms
        self._seen: "OrderedDict[str, int]" = OrderedDict()
        self._lock = threading.Lock()

    def accept(self, idempotency_key: str, now_ms: int) -> bool:
        """
        Return True if we should accept this key (not seen within the window),
        otherwise False.

        The method will also prune stale entries older than now_ms - window_ms.
        """
        cutoff = now_ms - self.window_ms
        with self._lock:
            previous = self._seen.get(idempotency_key)
            if previous is not None and now_ms - previous <= self.window_ms:
                return False

            # record/refresh the key and make it the newest item
            self._seen[idempotency_key] = now_ms
            self._seen.move_to_end(idempotency_key)

            # prune oldest entries while they're older than cutoff
            # because we moved current key to the end, we won't accidentally drop it
            while self._seen:
                oldest_key, oldest_seen = next(iter(self._seen.items()))
                if oldest_seen < cutoff:
                    # don't remove the key we just set (should be at the end)
                    if oldest_key == idempotency_key:
                        break
                    self._seen.popitem(last=False)
                else:
                    break

            return True

    def __len__(self) -> int:
        with self._lock:
            return len(self._seen)


__all__ = ["DedupeWindow", "PriorityQueue", "RouteDecision", "Router"]
