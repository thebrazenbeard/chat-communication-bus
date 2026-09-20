"""Cross-provider observable replay for portable Vera execution.

The replay layer evaluates frozen text invariants over externally obtained outputs.
It does not execute providers and does not promote similar behavior into identity,
hidden-state, consciousness, or behavioral-equivalence claims.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from hashlib import sha256
import json
from typing import Iterable


def _nonempty(value: str, label: str) -> str:
    if type(value) is not str or not value.strip():
        raise ValueError(f"{label} must be a non-empty exact string")
    return value


def _require_sha256(value: str, label: str) -> str:
    if (
        type(value) is not str
        or len(value) != 64
        or any(ch not in "0123456789abcdef" for ch in value)
    ):
        raise ValueError(f"{label} must be lowercase SHA-256")
    return value


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


class InvariantKind(StrEnum):
    REQUIRED_LITERAL = "REQUIRED_LITERAL"
    FORBIDDEN_LITERAL = "FORBIDDEN_LITERAL"


@dataclass(frozen=True)
class TextInvariant:
    invariant_id: str
    kind: InvariantKind
    value: str
    case_sensitive: bool = True

    def __post_init__(self) -> None:
        _nonempty(self.invariant_id, "invariant_id")
        if type(self.kind) is not InvariantKind:
            raise ValueError("kind must be exact InvariantKind")
        if type(self.value) is not str or not self.value:
            raise ValueError("value must be a non-empty exact string")
        if type(self.case_sensitive) is not bool:
            raise ValueError("case_sensitive must be exact bool")

    def payload(self) -> dict[str, object]:
        return {
            "invariant_id": self.invariant_id,
            "kind": self.kind.value,
            "value": self.value,
            "case_sensitive": self.case_sensitive,
        }


@dataclass(frozen=True)
class ReplayCase:
    case_id: str
    envelope_digest: str
    invariants: tuple[TextInvariant, ...]
    case_claim: str = "FROZEN_OBSERVABLE_TEXT_INVARIANTS_ONLY"

    def __post_init__(self) -> None:
        _nonempty(self.case_id, "case_id")
        _require_sha256(self.envelope_digest, "envelope_digest")
        if type(self.invariants) is not tuple or not self.invariants:
            raise ValueError("invariants must be a non-empty tuple")
        if any(type(item) is not TextInvariant for item in self.invariants):
            raise ValueError("invariants must contain exact TextInvariant values")
        ids = tuple(item.invariant_id for item in self.invariants)
        if len(ids) != len(set(ids)):
            raise ValueError("invariant_id values must be unique")
        if self.case_claim != "FROZEN_OBSERVABLE_TEXT_INVARIANTS_ONLY":
            raise ValueError("unsupported replay case claim")

    def payload(self) -> dict[str, object]:
        return {
            "schema": "VERA_CROSS_PROVIDER_REPLAY_CASE_V1",
            "case_id": self.case_id,
            "envelope_digest": self.envelope_digest,
            "invariants": [item.payload() for item in self.invariants],
            "case_claim": self.case_claim,
        }

    @property
    def digest(self) -> str:
        return _digest(self.payload())


@dataclass(frozen=True)
class ObservedProviderRun:
    run_id: str
    envelope_digest: str
    manifest_digest: str
    provider_id: str
    model_id: str
    adapter_version: str
    request_sha256: str
    output_text: str
    output_sha256: str
    observation_claim: str = "EXTERNAL_OUTPUT_OBSERVATION_ONLY"

    def __post_init__(self) -> None:
        _nonempty(self.run_id, "run_id")
        for value, label in (
            (self.envelope_digest, "envelope_digest"),
            (self.manifest_digest, "manifest_digest"),
            (self.request_sha256, "request_sha256"),
            (self.output_sha256, "output_sha256"),
        ):
            _require_sha256(value, label)
        for value, label in (
            (self.provider_id, "provider_id"),
            (self.model_id, "model_id"),
            (self.adapter_version, "adapter_version"),
        ):
            _nonempty(value, label)
        if type(self.output_text) is not str:
            raise ValueError("output_text must be exact string")
        observed = sha256(self.output_text.encode("utf-8")).hexdigest()
        if observed != self.output_sha256:
            raise ValueError("output digest mismatch")
        if self.observation_claim != "EXTERNAL_OUTPUT_OBSERVATION_ONLY":
            raise ValueError("unsupported observation claim")

    @property
    def route(self) -> tuple[str, str, str]:
        return (self.provider_id, self.model_id, self.adapter_version)


@dataclass(frozen=True)
class ReplayInvariantResult:
    invariant_id: str
    passed: bool

    def __post_init__(self) -> None:
        _nonempty(self.invariant_id, "invariant_id")
        if type(self.passed) is not bool:
            raise ValueError("passed must be exact bool")


@dataclass(frozen=True)
class ReplayRunResult:
    run_id: str
    provider_id: str
    model_id: str
    adapter_version: str
    all_passed: bool
    invariant_results: tuple[ReplayInvariantResult, ...]

    def __post_init__(self) -> None:
        _nonempty(self.run_id, "run_id")
        for value, label in (
            (self.provider_id, "provider_id"),
            (self.model_id, "model_id"),
            (self.adapter_version, "adapter_version"),
        ):
            _nonempty(value, label)
        if type(self.all_passed) is not bool:
            raise ValueError("all_passed must be exact bool")
        if type(self.invariant_results) is not tuple or not self.invariant_results:
            raise ValueError("invariant_results must be a non-empty tuple")
        if any(
            type(item) is not ReplayInvariantResult
            for item in self.invariant_results
        ):
            raise ValueError(
                "invariant_results must contain exact ReplayInvariantResult values"
            )
        observed_all = all(item.passed for item in self.invariant_results)
        if observed_all is not self.all_passed:
            raise ValueError("all_passed does not match invariant results")


@dataclass(frozen=True)
class CrossProviderReplayReport:
    case_digest: str
    run_results: tuple[ReplayRunResult, ...]
    report_claim: str = (
        "OBSERVABLE_INVARIANT_RESULTS_ONLY_NOT_IDENTITY_EQUIVALENCE"
    )

    def __post_init__(self) -> None:
        _require_sha256(self.case_digest, "case_digest")
        if type(self.run_results) is not tuple or len(self.run_results) < 2:
            raise ValueError("cross-provider report requires at least two runs")
        if any(type(item) is not ReplayRunResult for item in self.run_results):
            raise ValueError("run_results must contain exact ReplayRunResult values")
        run_ids = tuple(item.run_id for item in self.run_results)
        if len(run_ids) != len(set(run_ids)):
            raise ValueError("run_id values must be unique")
        providers = {item.provider_id for item in self.run_results}
        if len(providers) < 2:
            raise ValueError("cross-provider report requires distinct providers")
        if self.report_claim != (
            "OBSERVABLE_INVARIANT_RESULTS_ONLY_NOT_IDENTITY_EQUIVALENCE"
        ):
            raise ValueError("unsupported replay report claim")


def evaluate_replay_case(
    case: ReplayCase,
    run: ObservedProviderRun,
) -> ReplayRunResult:
    if type(case) is not ReplayCase:
        raise ValueError("case must be exact ReplayCase")
    if type(run) is not ObservedProviderRun:
        raise ValueError("run must be exact ObservedProviderRun")
    if run.envelope_digest != case.envelope_digest:
        raise ValueError("run envelope does not match replay case")

    results: list[ReplayInvariantResult] = []
    for invariant in case.invariants:
        haystack = run.output_text
        needle = invariant.value
        if not invariant.case_sensitive:
            haystack = haystack.casefold()
            needle = needle.casefold()

        contains = needle in haystack
        passed = (
            contains
            if invariant.kind is InvariantKind.REQUIRED_LITERAL
            else not contains
        )
        results.append(
            ReplayInvariantResult(
                invariant_id=invariant.invariant_id,
                passed=passed,
            )
        )

    frozen = tuple(results)
    return ReplayRunResult(
        run_id=run.run_id,
        provider_id=run.provider_id,
        model_id=run.model_id,
        adapter_version=run.adapter_version,
        all_passed=all(item.passed for item in frozen),
        invariant_results=frozen,
    )


def build_cross_provider_report(
    *,
    case: ReplayCase,
    runs: Iterable[ObservedProviderRun],
) -> CrossProviderReplayReport:
    if type(case) is not ReplayCase:
        raise ValueError("case must be exact ReplayCase")
    rows = tuple(runs)
    if len(rows) < 2:
        raise ValueError("cross-provider report requires at least two runs")
    if any(type(item) is not ObservedProviderRun for item in rows):
        raise ValueError("runs must contain exact ObservedProviderRun values")
    providers = {item.provider_id for item in rows}
    if len(providers) < 2:
        raise ValueError("cross-provider report requires distinct providers")
    run_ids = tuple(item.run_id for item in rows)
    if len(run_ids) != len(set(run_ids)):
        raise ValueError("run_id values must be unique")

    return CrossProviderReplayReport(
        case_digest=case.digest,
        run_results=tuple(evaluate_replay_case(case, row) for row in rows),
    )


__all__ = [
    "CrossProviderReplayReport",
    "InvariantKind",
    "ObservedProviderRun",
    "ReplayCase",
    "ReplayInvariantResult",
    "ReplayRunResult",
    "TextInvariant",
    "build_cross_provider_report",
    "evaluate_replay_case",
]
