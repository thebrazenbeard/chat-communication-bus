"""Radar workflow readiness and proportionate effect-scope rules.

Improvements:
- Added type hints (Mapping, Any).
- Introduced constants for decision/lane strings to avoid typos.
- Unified action/key names around "create_isolated_branch".
- Added docstrings for public functions and classes.
- Improved error messages.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping, Set


# Workflow-specific error
class WorkflowError(ValueError):
    pass


# Stable string constants for return values (keeps API non-breaking)
LANE_ACTION_REQUIRED_CREATE_LANE = "ACTION_REQUIRED:CREATE_LANE"
LANE_SATISFIED = "SATISFIED"
LANE_NOT_REQUIRED = "NOT_REQUIRED"

DECISION_REQUIRE_CLARIFICATION = "REQUIRE_CLARIFICATION"
DECISION_REQUIRE_EXACT_AUTHORITY = "REQUIRE_EXACT_AUTHORITY"
DECISION_DO_VERIFY_REPORT = "DO_VERIFY_REPORT"
DECISION_REQUIRE_ASSIGNMENT = "REQUIRE_ASSIGNMENT"


@dataclass(frozen=True)
class EffectScope:
    """Represents allowed side-effect categories for a workflow step.

    Attributes:
        isolated_branch: whether creating or writing to an isolated branch is allowed.
        merge: whether merges are allowed.
        deploy: whether deployments are allowed.
    """

    isolated_branch: bool = False
    merge: bool = False
    deploy: bool = False

    def allows(self, action: str) -> bool:
        """Return True if this scope allows a named action.

        Canonical action names:
          - "create_isolated_branch" (preferred)
          - "create_branch" (alias)
          - "write_isolated" (legacy alias)
          - "merge"
          - "deploy"
        """
        if action in {"create_isolated_branch", "create_branch", "write_isolated"}:
            return self.isolated_branch
        if action == "merge":
            return self.merge
        if action == "deploy":
            return self.deploy
        return False


def classify_lane_requirement(*, required: bool, exists: bool) -> str:
    """Classify whether a lane must be created.

    Returns one of the stable string constants:
      - ACTION_REQUIRED:CREATE_LANE
      - SATISFIED
      - NOT_REQUIRED
    """
    if required and not exists:
        return LANE_ACTION_REQUIRED_CREATE_LANE
    if required and exists:
        return LANE_SATISFIED
    return LANE_NOT_REQUIRED


def resolve_effect_scope(*, older: Mapping[str, Any], newer: Mapping[str, Any]) -> EffectScope:
    """Resolve an effect scope by applying the 'newer' narrower instructions without
    broadening unrelated ceilings from 'older'.

    Both `older` and `newer` are mappings representing the previous and desired
    constraints. The function recognizes the following keys (booleans):
      - "create_isolated_branch" (preferred)
      - "create_branch" (alias)
      - "isolated_branch" (legacy)
      - "local_only" (if True, prevents inheriting isolated permissions)
      - "merge"
      - "deploy"
    """
    # Helper to get a boolean with aliases
    def _get_bool(map_obj: Mapping[str, Any], *keys: str, default: bool = False) -> bool:
        for k in keys:
            if k in map_obj:
                return bool(map_obj[k])
        return default

    # Prefer canonical "create_isolated_branch"; accept aliases for compatibility.
    isolated = _get_bool(newer, "create_isolated_branch", "create_branch", "write_isolated", default=False)
    if not isolated:
        # inherit isolated_branch from older unless local_only was set on older
        local_only = _get_bool(older, "local_only", default=False)
        isolated = (not local_only) and _get_bool(older, "isolated_branch", "create_isolated_branch", default=False)

    merge = _get_bool(newer, "merge", default=_get_bool(older, "merge", default=False))
    deploy = _get_bool(newer, "deploy", default=_get_bool(older, "deploy", default=False))

    return EffectScope(isolated_branch=isolated, merge=merge, deploy=deploy)


def execution_decision(
    *,
    action: str,
    explicitly_assigned: bool,
    reversible: bool,
    protected: bool,
    ambiguous: bool,
) -> str:
    """Return an execution decision string for a requested action.

    The returned string is one of the DECISION_* constants defined above.
    """
    if ambiguous:
        return DECISION_REQUIRE_CLARIFICATION
    if protected:
        return DECISION_REQUIRE_EXACT_AUTHORITY
    if explicitly_assigned and reversible:
        return DECISION_DO_VERIFY_REPORT
    if not explicitly_assigned:
        return DECISION_REQUIRE_ASSIGNMENT
    # Fallback: require exact authority for any non-reversible explicit assignment
    return DECISION_REQUIRE_EXACT_AUTHORITY


class DependencyGraph:
    """Simple dependency graph for assignment readiness and protected authority."""

    def __init__(self) -> None:
        self._assignments: Set[str] = set()
        self._complete: Set[str] = set()
        self._predecessors: Dict[str, Set[str]] = {}
        self._protected_authority: Set[str] = set()

    def add_assignment(self, assignment_id: str, *, protected_authority: bool = False) -> None:
        """Register a new assignment ID.

        Raises:
            WorkflowError: if assignment_id is falsy.
        """
        if not assignment_id:
            raise WorkflowError("ASSIGNMENT_ID_REQUIRED")
        self._assignments.add(assignment_id)
        self._predecessors.setdefault(assignment_id, set())
        if protected_authority:
            self._protected_authority.add(assignment_id)

    def add_edge(self, predecessor: str, successor: str) -> None:
        """Add a dependency edge predecessor -> successor.

        Raises:
            WorkflowError: if either assignment is unknown or the edge would create a cycle.
        """
        self._require(predecessor)
        self._require(successor)
        if predecessor == successor or self._reachable(successor, predecessor):
            raise WorkflowError(f"DEPENDENCY_CYCLE: {predecessor} -> {successor}")
        self._predecessors[successor].add(predecessor)

    def complete(self, assignment_id: str) -> None:
        """Mark an assignment as complete."""
        self._require(assignment_id)
        self._complete.add(assignment_id)

    def ready(self, assignment_id: str) -> bool:
        """Return True when all predecessors of assignment_id are complete."""
        self._require(assignment_id)
        predecessors = self._predecessors.get(assignment_id, set())
        return predecessors.issubset(self._complete)

    def protected_authority(self, assignment_id: str) -> bool:
        """Return True if the assignment carries protected authority."""
        self._require(assignment_id)
        return assignment_id in self._protected_authority

    def _require(self, assignment_id: str) -> None:
        if assignment_id not in self._assignments:
            raise WorkflowError(f"UNKNOWN_ASSIGNMENT: {assignment_id}")

    def _reachable(self, start: str, target: str) -> bool:
        """Detect whether `target` is reachable from `start` (graph traversal on successor edges)."""
        stack = [start]
        seen: Set[str] = set()
        # Build reverse map (predecessor -> successors) for traversal
        reverse: Dict[str, Set[str]] = {a: set() for a in self._assignments}
        for successor, predecessors in self._predecessors.items():
            for predecessor in predecessors:
                reverse.setdefault(predecessor, set()).add(successor)

        while stack:
            current = stack.pop()
            if current == target:
                return True
            if current in seen:
                continue
            seen.add(current)
            stack.extend(reverse.get(current, ()))
        return False


__all__ = [
    "DependencyGraph",
    "EffectScope",
    "WorkflowError",
    "classify_lane_requirement",
    "execution_decision",
    "resolve_effect_scope",
]
