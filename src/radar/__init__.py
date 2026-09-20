"""Radar control-plane package.

Provides routing, envelope classification, node status tracking, and telemetry
for the chat communication bus control plane.
"""

# Actions execution evidence
from .actions_evidence import (
    ActionsExecutionClass,
    ActionsExecutionEvidence,
    classify_actions_jobs,
)

# Envelope handling
from .envelope import EnvelopeClassification, EnvelopeResult, RadarEnvelope

# Routing
from .routing import DedupeWindow, PriorityQueue, RouteDecision, Router

# Node management
from .model import NodeStatus
from .registry import IdentityRegistry, RegistryError

# Telemetry
from .heartbeat import HeartbeatRuntime
from .telemetry import HEARTBEAT_INTERVAL_MS, TelemetrySnapshot, TelemetryStore

__all__ = [
    # Actions execution evidence
    "ActionsExecutionClass",
    "ActionsExecutionEvidence",
    "classify_actions_jobs",
    # Envelope handling
    "EnvelopeClassification",
    "EnvelopeResult",
    "RadarEnvelope",
    # Routing
    "DedupeWindow",
    "PriorityQueue",
    "RouteDecision",
    "Router",
    # Node management
    "IdentityRegistry",
    "NodeStatus",
    "RegistryError",
    # Telemetry
    "HEARTBEAT_INTERVAL_MS",
    "HeartbeatRuntime",
    "TelemetrySnapshot",
    "TelemetryStore",
]
