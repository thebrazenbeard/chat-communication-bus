"""A dated provider readback is evidence, not deployment or delivery authority."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
CURRENT = ROOT / "architecture/contracts/RADAR_CURRENT.json"
OBSERVATION = ROOT / "architecture/contracts/RADAR_PROVIDER_OBSERVATION_20261103_V1.json"
CUSTODY = ROOT / "architecture/contracts/RADAR_SOURCE_CUSTODY_V1.json"
PROVIDER_DOC = ROOT / "architecture/contracts/RADAR_SUPABASE_V1.md"

SOURCE_MAIN_AT_OBSERVATION = "eb315a5612ae99aadddb397891ffcf3a2b0433a6"
DEPLOYED_EDGE_SOURCE_COMMIT = "b14175c992f93088b763822add6cc7baa7990a53"
EXPECTED_BUNDLE_SHA256 = "781265b5bf05f02a3420e2eb33fff5ce780a0e1fbb9499a8706e685142397f51"

EXPECTED_RADAR_MIGRATIONS = [
    "20260902120716_radar_control_plane_v1",
    "20260902120826_radar_realtime_v1",
    "20260902203610_radar_visual_identity_v1",
    "20260902204759_radar_live_message_projection_v1",
    "20260902231445_radar_live_message_collision_v1",
    "20260903000603_radar_receipt_plane_v1",
    "20260903001906_radar_assignment_plane_v1",
    "20260903113314_radar_operator_views_v1",
    "20260921202213_20260903214334_radar_thread_closure_v1",
    "20260921202217_20260905230823_radar_oidc_replay_guard_v1",
    "20260921202221_20260906133630_radar_node_routing_hardening_v1",
    "20260921202226_20260906154101_radar_projection_journal_v1",
    "20260921202232_20260906165117_radar_projection_journal_api_v1",
    "20260921202237_20260908010500_radar_projection_atomic_file_v1",
    "20260922171230_radar_oidc_replay_guard_rls_v1",
]

EXPECTED_BLOBS = {
    "index.ts": "2972c6915b0fec2b8b6082e6da9d7a3c87be929b",
    "handler.ts": "ce6c32be44d482a0216f4f397a8bf1a9ab8564f9",
    "provider_503_log.ts": "4dcb94eb42bc81e843fd5986cd96400222e0faba",
    "deno.json": "b717027d0dbca1ed7cf7f362f16a33cfc5c6da99",
}


def validate_public_safe_source_observation(data: dict) -> None:
    # This dated contract is intentionally closed-schema. These assertions are
    # consistency checks for one known fixture, not a general-purpose DLP or
    # credential scanner for arbitrary JSON/documents.
    assert set(data) == {
        "contract", "schema_version", "evidence_type", "observed_on_utc",
        "provider_alias", "project_id_included", "canonical_repository",
        "canonical_main_at_observation", "provider", "release_boundary",
    }
    assert data["contract"] == "RADAR_PROVIDER_OBSERVATION_V1"
    assert data["schema_version"] == 1
    assert data["evidence_type"] == "READ_ONLY_PROVIDER_OBSERVATION"
    assert data["observed_on_utc"] == "2026-11-03"
    assert data["provider_alias"] == "Vera Supabase"
    assert data["canonical_repository"] == "thebrazenbeard/chat-communication-bus"
    assert data["canonical_main_at_observation"] == SOURCE_MAIN_AT_OBSERVATION
    assert data["project_id_included"] is False

    # A source-only public contract may contain Git blob hashes, but neither
    # raw project references nor credentials, including inside free-form text.
    serialized = json.dumps(data, sort_keys=True)
    assert not re.search(r"\b[a-z]{20}\b", serialized)
    assert not any(
        field in serialized.lower()
        for field in ('"project_id"', '"project_ref"', '"service_role"', '"secret"')
    )

    provider = data["provider"]
    assert set(provider) == {
        "status", "migration_ledger_total", "radar_migration_ledger_count",
        "radar_migration_ledger_versions", "edge_function", "journal_row_counts",
    }
    assert provider["status"] == "ACTIVE_HEALTHY"
    edge = provider["edge_function"]
    assert set(edge) == {
        "slug", "status", "version", "verify_jwt", "bundle_sha256",
        "deployed_source_commit_match", "canonical_main_source_match",
        "source_file_git_blobs", "source_comparison", "oidc_runtime_execution_qualified",
    }
    assert edge["slug"] == "github-bus-ingest"
    assert edge["version"] == 7
    assert edge["bundle_sha256"] == EXPECTED_BUNDLE_SHA256
    assert edge["verify_jwt"] is False
    assert edge["status"] == "ACTIVE"
    assert edge["deployed_source_commit_match"] == DEPLOYED_EDGE_SOURCE_COMMIT
    assert edge["canonical_main_source_match"] is False
    assert edge["source_file_git_blobs"] == EXPECTED_BLOBS
    assert edge["source_comparison"] == "ALL_FOUR_DEPLOYED_FILE_BYTES_EQUAL_TO_COMMIT"
    assert edge["oidc_runtime_execution_qualified"] is False

    migrations = data["provider"]["radar_migration_ledger_versions"]
    assert data["provider"]["migration_ledger_total"] == 99
    assert data["provider"]["radar_migration_ledger_count"] == len(migrations) == 15
    assert migrations == EXPECTED_RADAR_MIGRATIONS
    assert len(set(migrations)) == len(migrations)
    assert all("radar_" in name for name in migrations)
    assert data["provider"]["journal_row_counts"] == {
        "projection_lane_state": 0,
        "projection_batches": 0,
        "projection_batch_files": 0,
    }

    boundary = data["release_boundary"]
    assert set(boundary) == {
        "source_only_observation", "migration_installation_claim",
        "canonical_main_deployment_claim", "trusted_projector_execution_claim",
        "batch_delivery_claim", "provider_recovery_complete_claim",
        "projection_delivery_status", "provider_configuration_attested",
        "runtime_success_attested", "effect_authority_granted",
    }
    assert boundary["source_only_observation"] is True
    for forbidden_claim in (
        "migration_installation_claim", "canonical_main_deployment_claim",
        "trusted_projector_execution_claim", "batch_delivery_claim",
        "provider_recovery_complete_claim", "provider_configuration_attested",
        "runtime_success_attested", "effect_authority_granted",
    ):
        assert boundary[forbidden_claim] is False
    assert boundary["projection_delivery_status"] == "NOT_ESTABLISHED_BY_THIS_OBSERVATION"


def assert_rejected(data: dict) -> None:
    try:
        validate_public_safe_source_observation(data)
    except AssertionError:
        return
    raise AssertionError("invalid observation was accepted")


def validate_schema_v5_provider_claims(data: dict) -> None:
    """Reject promotion of a historical Boolean or source observation into current provider state."""
    assert data["schema_version"] == 5
    assert "provider" not in data
    claims = data["provider_claims"]
    assert set(claims) == {
        "claim_role", "trusted_projector_deployment_status", "trusted_projector_execution_status",
        "github_oidc_delivery_status", "projection_cursor_custody_status", "latest_dated_observation",
        "runtime_effects_attested",
    }
    assert claims["claim_role"] == "SOURCE_CURRENTNESS_GATE_NOT_LIVE_PROVIDER_SNAPSHOT"
    for field in (
        "trusted_projector_deployment_status", "trusted_projector_execution_status",
        "github_oidc_delivery_status", "projection_cursor_custody_status",
    ):
        assert claims[field] == "UNKNOWN_UNQUALIFIED"
    assert claims["runtime_effects_attested"] is False
    assert claims["latest_dated_observation"] == OBSERVATION.relative_to(ROOT).as_posix()
    old = data["historical_provider_snapshot"]
    assert old["readback_role"] == "HISTORICAL_SNAPSHOT_NOT_CURRENT_PROVIDER_STATE"
    assert old["readback_at"] == "2026-09-09"


def assert_invalid_schema_v5_provider_claims(data: dict) -> None:
    try:
        validate_schema_v5_provider_claims(data)
    except (AssertionError, KeyError):
        return
    raise AssertionError("misleading provider-currentness contract was accepted")


def test_dated_source_observation_is_bound_but_does_not_supersede_release_authority() -> None:
    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    observation = json.loads(OBSERVATION.read_text(encoding="utf-8"))
    custody = json.loads(CUSTODY.read_text(encoding="utf-8"))
    path = OBSERVATION.relative_to(ROOT).as_posix()

    assert current["historical_provider_snapshot"]["readback_role"] == "HISTORICAL_SNAPSHOT_NOT_CURRENT_PROVIDER_STATE"
    assert current["historical_provider_snapshot"]["readback_at"] < observation["observed_on_utc"]
    assert current["latest_provider_observation_contract"] == path
    assert path in custody["paths"]
    assert path in PROVIDER_DOC.read_text(encoding="utf-8")
    assert current["projection_source"]["current_projection_anchor_e_deployment_eligible"] is True
    assert current["projection_source"]["successor_anchor_status"] == "FROZEN_QUALIFIED_SOURCE_ONLY"
    validate_public_safe_source_observation(observation)


def test_observation_rejects_false_deployment_or_delivery_claims() -> None:
    data = json.loads(OBSERVATION.read_text(encoding="utf-8"))
    for claim in ("canonical_main_deployment_claim", "batch_delivery_claim", "effect_authority_granted"):
        tampered = deepcopy(data)
        tampered["release_boundary"][claim] = True
        assert_rejected(tampered)


def test_observation_rejects_project_identifiers_and_fabricated_source_equality() -> None:
    data = json.loads(OBSERVATION.read_text(encoding="utf-8"))
    leaked = deepcopy(data)
    leaked["provider_alias"] = "abcdefghijklmnopqrst"
    assert_rejected(leaked)

    credential_shaped = deepcopy(data)
    credential_shaped["provider_alias"] = "service_role_token=NOT_A_REAL_TOKEN"
    assert_rejected(credential_shaped)

    unknown_field = deepcopy(data)
    unknown_field["unreviewed_note"] = "some external field"
    assert_rejected(unknown_field)

    forged_migration = deepcopy(data)
    forged_migration["provider"]["radar_migration_ledger_versions"][0] = (
        "20260902120716_radar_service_role_token_NOT_A_REAL_TOKEN"
    )
    assert_rejected(forged_migration)

    forged_digest = deepcopy(data)
    forged_digest["provider"]["edge_function"]["bundle_sha256"] = "service_role_token=NOT_A_REAL_TOKEN"
    assert_rejected(forged_digest)

    false_match = deepcopy(data)
    false_match["provider"]["edge_function"]["canonical_main_source_match"] = True
    assert_rejected(false_match)


def test_historical_drift_not_promoted_as_present_provider_state() -> None:
    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    observation = json.loads(OBSERVATION.read_text(encoding="utf-8"))
    historical_drift = {item["code"]: item for item in current["historical_provider_drift"]}
    current_drift = {item["code"]: item for item in current["known_provider_drift"]}
    historical = (
        "RADAR_SOURCE_MIGRATIONS_NOT_APPLIED",
        "GITHUB_BUS_INGEST_GATEWAY_JWT_MISMATCH",
        "PROJECTION_JOURNAL_NOT_INSTALLED_OR_SEEDED",
    )
    for code in historical:
        assert code not in current_drift
        assert historical_drift[code]["evidence_role"] == "HISTORICAL_SUPERSEDED_BY_2026-11-03_OBSERVATION"
        assert "September historical snapshot" in historical_drift[code]["detail"]
        assert "2026-11-03" in historical_drift[code]["detail"]

    assert current_drift["PROJECTION_ANCHOR_E_DEPLOYMENT_UNQUALIFIED"]["evidence_role"] == (
        "SOURCE_RELEASE_HOLD_NOT_A_PROVIDER_EXECUTION_FINDING"
    )
    assert current_drift["PROJECTION_ANCHOR_E_DEPLOYMENT_UNQUALIFIED"]["current_deployment_status"] == (
        "UNKNOWN_UNQUALIFIED"
    )
    assert current_drift["PROJECTION_ANCHOR_E_DEPLOYMENT_UNQUALIFIED"]["code_interpretation"] == (
        "CURRENT_RELEASE_HOLD_WITHOUT_VERIFIED_DEPLOYMENT_OR_NONDEPLOYMENT"
    )
    assert current["schema_version"] == 5
    assert current["projection_source"]["status"] == (
        "ANCHOR_E_FROZEN_QUALIFIED_SOURCE_ONLY_DEPLOYMENT_UNQUALIFIED"
    )
    assert current["projection_source"]["legacy_status_role"] == (
        "HISTORICAL_RELEASE_HOLD_LABEL_NOT_CURRENT_PROVIDER_READBACK"
    )
    assert current["legacy_release_hold_code_aliases"] == [
        {
            "legacy_code": "PROJECTION_ANCHOR_E_NOT_DEPLOYED",
            "current_code": "PROJECTION_ANCHOR_E_DEPLOYMENT_UNQUALIFIED",
            "alias_role": "HISTORICAL_RELEASE_HOLD_IDENTIFIER_NOT_CURRENT_PROVIDER_DRIFT",
            "compatibility_warning": current["legacy_release_hold_code_aliases"][0]["compatibility_warning"],
        }
    ]
    assert "cannot guarantee compatibility" in current["legacy_release_hold_code_aliases"][0][
        "compatibility_warning"
    ]
    date_conflict = current["historical_provider_readback_date_conflict"]
    assert date_conflict["current_json_readback_at"] == current["historical_provider_snapshot"]["readback_at"] == "2026-09-09"
    assert date_conflict["provider_contract_last_readback_at"] == "2026-09-06"
    assert date_conflict["resolution"] == "UNRESOLVED_HISTORICAL_METADATA_DATE_DISCREPANCY"
    assert date_conflict["currentness_evidence"] is False
    assert "2026-09-06" in PROVIDER_DOC.read_text(encoding="utf-8")
    assert observation["provider"]["radar_migration_ledger_count"] == 15
    assert observation["provider"]["edge_function"]["version"] == 7
    assert observation["provider"]["edge_function"]["verify_jwt"] is False
    assert observation["provider"]["journal_row_counts"]["projection_batches"] == 0


def test_unknown_current_provider_status_never_emits_definite_non_deployment_drift_code() -> None:
    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    validate_schema_v5_provider_claims(current)
    # This is a negative semantic test, not a claim of present provider state.
    # A dated observation of Edge source bytes is not a positive attestation that
    # the independent trusted projector was deployed OR was absent.
    assert "provider" not in current  # no overloaded field that exposes historical bool as current
    assert current["historical_provider_snapshot"]["readback_role"] == "HISTORICAL_SNAPSHOT_NOT_CURRENT_PROVIDER_STATE"
    assert current["historical_provider_snapshot"]["projection_anchor_e_deployed"] is False  # historical only
    assert current["historical_provider_snapshot"]["readback_at"] == "2026-09-09"
    assert current["provider_claims"]["trusted_projector_deployment_status"] == "UNKNOWN_UNQUALIFIED"
    assert current["latest_provider_observation_contract"] == OBSERVATION.relative_to(ROOT).as_posix()
    assert current["known_provider_drift"]
    for finding in current["known_provider_drift"]:
        if finding.get("current_deployment_status") == "UNKNOWN_UNQUALIFIED":
            assert "NOT_DEPLOYED" not in finding["code"]
            assert "DEPLOYED" not in finding["code"]
            assert finding["evidence_role"] == "SOURCE_RELEASE_HOLD_NOT_A_PROVIDER_EXECUTION_FINDING"
    legacy = current["legacy_release_hold_code_aliases"]
    assert all(item["legacy_code"] not in {d["code"] for d in current["known_provider_drift"]} for item in legacy)


def test_schema_v5_rejects_provider_boolean_promotion_or_fabricated_runtime_attestation() -> None:
    current = json.loads(CURRENT.read_text(encoding="utf-8"))
    validate_schema_v5_provider_claims(current)

    stale_alias = deepcopy(current)
    stale_alias["provider"] = {"projection_anchor_e_deployed": False}
    assert_invalid_schema_v5_provider_claims(stale_alias)

    for status in ("NOT_DEPLOYED", "DEPLOYED", "ACTIVE", True, False):
        fabricated = deepcopy(current)
        fabricated["provider_claims"]["trusted_projector_deployment_status"] = status
        assert_invalid_schema_v5_provider_claims(fabricated)

    fabricated_delivery = deepcopy(current)
    fabricated_delivery["provider_claims"]["github_oidc_delivery_status"] = "PASS"
    assert_invalid_schema_v5_provider_claims(fabricated_delivery)

    imported_legacy_boolean = deepcopy(current)
    imported_legacy_boolean["provider_claims"]["projection_anchor_e_deployed"] = False
    assert_invalid_schema_v5_provider_claims(imported_legacy_boolean)

    forged_effect = deepcopy(current)
    forged_effect["provider_claims"]["runtime_effects_attested"] = True
    assert_invalid_schema_v5_provider_claims(forged_effect)

    unscoped_snapshot = deepcopy(current)
    unscoped_snapshot["historical_provider_snapshot"]["readback_role"] = "CURRENT"
    assert_invalid_schema_v5_provider_claims(unscoped_snapshot)
