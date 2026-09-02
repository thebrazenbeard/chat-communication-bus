"""Radar workflow readiness and proportionate effect-scope rules."""

from __future__ import annotations

from dataclasses import dataclass


class WorkflowError(ValueError):
    pass


@dataclass(frozen=True)
class EffectScope:
    isolated_branch: bool = False
    merge: bool = False
    deploy: bool = False

    def allows(self, action: str) -> bool:
        if action in {"create_branch", "write_isolated"}:
            return self.isolated_branch
        if action == "merge":
            return self.merge
        if action == "deploy":
            return self.deploy
        return False


def classify_lane_requirement(*, required: bool, exists: bool) -> str:
    if required and not exists:
        return "ACTION_REQUIRED:CREATE_LANE"
    if required and exists:
        return "SATISFIED"
    return "NOT_REQUIRED"


def resolve_effect_scope(*, older: dict[str, object], newer: dict[str, object]) -> EffectScope:
    """Apply a newer narrow instruction without broadening unrelated ceilings."""

    isolated = bool(newer.get("create_isolated_branch", False))
    if not isolated:
        isolated = not bool(older.get("local_only", False)) and bool(older.get("isolated_branch", False))
    merge = bool(newer.get("merge", older.get("merge", False)))
    deploy = bool(newer.get("deploy", older.get("deploy", False)))
    return EffectScope(isolated_branch=isolated, merge=merge, deploy=deploy)


def execution_decision(
    *,
    action: str,
    explicitly_assigned: bool,
    reversible: bool,
    protected: bool,
    ambiguous: bool,
) -> str:
    if ambiguous:
        return "REQUIRE_CLARIFICATION"
    if protected:
        return "REQUIRE_EXACT_AUTHORITY"
    if explicitly_assigned and reversible:
        return "DO_VERIFY_REPORT"
    if not explicitly_assigned:
        return "REQUIRE_ASSIGNMENT"
    return "REQUIRE_EXACT_AUTHORITY"


class DependencyGraph:
    def __init__(self) -> None:
        self._assignments: set[str] = set()
        self._complete: set[str] = set()
        self._predecessors: dict[str, set[str]] = {}
        self._protected_authority: set[str] = set()

    def add_assignment(self, assignment_id: str, *, protected_authority: bool = False) -> None:
        if not assignment_id:
            raise WorkflowError("ASSIGNMENT_ID_REQUIRED")
        self._assignments.add(assignment_id)
        self._predecessors.setdefault(assignment_id, set())
        if protected_authority:
            self._protected_authority.add(assignment_id)

    def add_edge(self, predecessor: str, successor: str) -> None:
        self._require(predecessor)
        self._require(successor)
        if predecessor == successor or self._reachable(successor, predecessor):
            raise WorkflowError("DEPENDENCY_CYCLE")
        self._predecessors[successor].add(predecessor)

    def complete(self, assignment_id: str) -> None:
        self._require(assignment_id)
        self._complete.add(assignment_id)

    def ready(self, assignment_id: str) -> bool:
        self._require(assignment_id)
        predecessors = self._predecessors[assignment_id]
        return predecessors.issubset(self._complete)

    def protected_authority(self, assignment_id: str) -> bool:
        self._require(assignment_id)
        return assignment_id in self._protected_authority

    def _require(self, assignment_id: str) -> None:
        if assignment_id not in self._assignments:
            raise WorkflowError("UNKNOWN_ASSIGNMENT")

    def _reachable(self, start: str, target: str) -> bool:
        stack = [start]
        seen: set[str] = set()
        reverse: dict[str, set[str]] = {a: set() for a in self._assignments}
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
