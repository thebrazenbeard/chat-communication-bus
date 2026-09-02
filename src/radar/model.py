"""Core immutable models shared by Radar subsystems."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EnvelopeClassification(str, Enum):
    VALID = "VALID"
    NORMALIZED = "NORMALIZED"
    REJECTED = "REJECTED"
    DLQ = "DLQ"


class NodeStatus(str, Enum):
    ONLINE = "ONLINE"
    IDLE = "IDLE"
    WORKING = "WORKING"
    WAITING_DEPENDENCY = "WAITING_DEPENDENCY"
    DEGRADED = "DEGRADED"
    OFFLINE = "OFFLINE"
    PAUSED = "PAUSED"
    ARCHIVED = "ARCHIVED"


@dataclass(frozen=True)
class Identity:
    identity_id: str
    display_name: str
    aliases: tuple[str, ...] = ()


@dataclass(frozen=True)
class Node:
    node_id: str
    identity_id: str
    status: NodeStatus


@dataclass(frozen=True)
class Endpoint:
    endpoint_id: str
    identity_id: str
    transport: str
    address: str


@dataclass(frozen=True)
class Subscription:
    identity_id: str
    domain: str
    min_priority: int = 3
