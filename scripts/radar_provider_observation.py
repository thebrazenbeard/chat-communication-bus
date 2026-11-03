#!/usr/bin/env python3
"""Compare current Radar's historical provider snapshot with fresh metadata.

This is an inert diagnostic. An observation JSON is untrusted input, not an
authenticated provider receipt. Matching fields never qualify deployment,
delivery, a projection cursor, or a Bus acknowledgement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


def _object(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("INVALID_PROVIDER_OBSERVATION: expected object")
    return value


def _field(value: object, field: str, expected: type) -> object:
    if expected is int and (not isinstance(value, int) or isinstance(value, bool)):
        raise ValueError(f"INVALID_PROVIDER_OBSERVATION: {field}")
    if expected is bool and type(value) is not bool:
        raise ValueError(f"INVALID_PROVIDER_OBSERVATION: {field}")
    if expected is str and (not isinstance(value, str) or not value):
        raise ValueError(f"INVALID_PROVIDER_OBSERVATION: {field}")
    return value


def compare_provider_observation(
    current: dict[str, object], observation: dict[str, object]
) -> dict[str, object]:
    """Return discrepancy signals only; never return a delivery PASS."""
    provider = _object(_object(current).get("provider"))
    expected = _object(provider.get("edge_function"))
    observed = _object(_object(observation).get("edge_function"))
    _field(observation.get("source_kind"), "source_kind", str)
    if observation["source_kind"] != "SUPABASE_EDGE_METADATA":
        raise ValueError("INVALID_PROVIDER_OBSERVATION: source_kind")
    _field(observation.get("observed_at"), "observed_at", str)

    comparisons = (("slug", "slug", str), ("version", "live_version", int),
                   ("status", "live_status", str), ("verify_jwt", "verify_jwt", bool))
    changed: list[str] = []
    for observed_key, expected_key, kind in comparisons:
        actual = _field(observed.get(observed_key), observed_key, kind)
        baseline = _field(expected.get(expected_key), expected_key, kind)
        if actual != baseline:
            changed.append(observed_key)

    # Supabase may re-version an applied migration while preserving the exact
    # historical source version in its name. Compare the declared source stems,
    # not just the provider's newly allocated timestamp.
    migrations = observation.get("migrations")
    migration_unobserved = migrations is None
    if migrations is not None:
        if not isinstance(migrations, list):
            raise ValueError("INVALID_PROVIDER_OBSERVATION: migrations")
        observed_names: set[str] = set()
        for item in migrations:
            record = _object(item)
            name = _field(record.get("name"), "migration.name", str)
            _field(record.get("version"), "migration.version", str)
            if name in observed_names:
                raise ValueError("INVALID_PROVIDER_OBSERVATION: duplicate migration.name")
            observed_names.add(name)
        missing_before = provider.get("unapplied_source_migrations", [])
        if not isinstance(missing_before, list) or any(not isinstance(x, str) for x in missing_before):
            raise ValueError("INVALID_PROVIDER_OBSERVATION: unapplied_source_migrations")
        if any(Path(path).stem in observed_names for path in missing_before):
            changed.append("unapplied_source_migrations")

    reasons = ["PROVIDER_SNAPSHOT_DRIFT"] if changed else []
    if migration_unobserved:
        reasons.append("MIGRATIONS_UNOBSERVED")
    source_state = _object(current.get("projection_source", {})).get("status", "")
    if isinstance(source_state, str) and "SOURCE_ONLY" in source_state:
        reasons.append("SOURCE_CUTOVER_HOLD")
    reasons.append("DELIVERY_UNVERIFIED")
    return {
        "status": "HOLD",
        "snapshot_drift": bool(changed),
        "changed_fields": changed,
        "reasons": reasons,
        "evidence_class": "UNTRUSTED_METADATA_COMPARISON",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("current", type=Path, help="local RADAR_CURRENT.json")
    parser.add_argument("observation", type=Path, help="operator-supplied provider metadata JSON")
    parser.add_argument("--fail-on-drift", action="store_true", help="exit 1 when historical snapshot differs")
    args = parser.parse_args(argv)
    try:
        current = _object(json.loads(args.current.read_text(encoding="utf-8")))
        observation = _object(json.loads(args.observation.read_text(encoding="utf-8")))
        result = compare_provider_observation(current, observation)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "ERROR", "error": "INVALID_PROVIDER_OBSERVATION", "detail": str(exc)}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 1 if args.fail_on_drift and result["snapshot_drift"] else 0


if __name__ == "__main__":
    sys.exit(main())
