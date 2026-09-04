import json
from pathlib import Path

from radar.github_projection import LaneEvidence, project_branches


ROOT = Path(__file__).resolve().parents[2]


def _topology():
    return json.loads(
        (ROOT / "architecture" / "contracts" / "RADAR_TOPOLOGY_V1.json").read_text(encoding="utf-8")
    )


def test_topology_has_unique_required_identities_and_radar_lane():
    data = _topology()
    lanes = data["required_writer_lanes"]
    assert len(lanes) == len(set(lanes))
    assert lanes["radar"]["branch"] == "bus/radar-v2"
    assert lanes["radar"]["historical_branch"] == "bus/radar-v1"
    assert lanes["radar"]["writer"] == "Radar"
    assert data["excluded_branches"]["bus/bridget-v1-tempcheck"] == "temporary_diagnostic"


def test_topology_preserves_brigit_legacy_branch_without_second_identity():
    data = _topology()
    brigit = data["required_writer_lanes"]["brigit"]
    assert brigit["branch"] == "bus/brigit-v2"
    assert brigit["legacy_spelling"] is False
    assert brigit["historical_branch"] == "bus/bridget-v1"
    assert brigit["historical_legacy_spelling"] is True
    assert "bridget" not in data["required_writer_lanes"]


def test_expected_topology_projects_without_missing_lanes():
    data = _topology()
    lanes = data["required_writer_lanes"]
    observed = [entry["branch"] for entry in lanes.values()]
    projection = project_branches(observed, required_identities=set(lanes))
    assert projection.missing_required == ()
    assert projection.identity_lanes["brigit"] == "bus/brigit-v2"
    assert projection.identity_lanes["vera"] == "bus/vera-v2"


def test_evidence_backed_projection_rejects_named_branch_without_mailbox():
    projection = project_branches(
        ["bus/hephaestus-v1"],
        required_identities={"hephaestus"},
        lane_evidence={
            "bus/hephaestus-v1": LaneEvidence(
                has_messages_dir=False,
                declared_writer=None,
                message_writers=(),
            )
        },
    )
    assert "hephaestus" not in projection.identity_lanes
    assert projection.missing_required == ("hephaestus",)
    assert projection.malformed_lanes == ("bus/hephaestus-v1",)


def test_evidence_backed_projection_accepts_empty_mailbox_with_matching_declared_writer():
    projection = project_branches(
        ["bus/hephaestus-v2"],
        required_identities={"hephaestus"},
        lane_evidence={
            "bus/hephaestus-v2": LaneEvidence(
                has_messages_dir=True,
                declared_writer="Hephaestus",
                message_writers=(),
            )
        },
    )
    assert projection.identity_lanes["hephaestus"] == "bus/hephaestus-v2"
    assert projection.missing_required == ()
    assert projection.malformed_lanes == ()


def test_evidence_writer_aliases_resolve_to_logical_identity():
    projection = project_branches(
        ["bus/bridget-v1", "bus/vera-sol-v1"],
        required_identities={"brigit", "vera"},
        lane_evidence={
            "bus/bridget-v1": LaneEvidence(True, "Brigit", ()),
            "bus/vera-sol-v1": LaneEvidence(True, None, ("Vera-Sol",)),
        },
    )
    assert projection.identity_lanes["brigit"] == "bus/bridget-v1"
    assert projection.identity_lanes["vera"] == "bus/vera-sol-v1"
    assert projection.malformed_lanes == ()


def test_hephaestus_current_lane_advances_to_v3_and_preserves_both_predecessors():
    data = _topology()
    hephaestus = data["required_writer_lanes"]["hephaestus"]
    assert hephaestus["branch"] == "bus/hephaestus-v3"
    assert hephaestus["historical_branch"] == "bus/hephaestus-v2"
    assert data["excluded_branches"]["bus/hephaestus-v1"] == "malformed_historical_non_mailbox"


def test_lane_projection_seed_uses_logical_vera_identity_not_runtime_route_identity():
    seed = (ROOT / "supabase" / "seed" / "radar_bus_lanes_20260902.sql").read_text(encoding="utf-8")
    assert "('vera', 'Vera', 'bus/vera-sol-v1')" in seed
    assert "('vera-sol', 'Vera / Sol', 'bus/vera-sol-v1')" not in seed
    assert "case when identity_id = 'vera' then array['vera-sol']::text[]" in seed


def test_lane_projection_seed_uses_hephaestus_v2_not_malformed_v1():
    seed = (ROOT / "supabase" / "seed" / "radar_bus_lanes_20260902.sql").read_text(encoding="utf-8")
    assert "('hephaestus', 'Hephaestus', 'bus/hephaestus-v2')" in seed
    assert "('hephaestus', 'Hephaestus', 'bus/hephaestus-v1')" not in seed


def test_vera_projection_repair_preserves_legacy_provenance_without_delete():
    repair = (ROOT / "supabase" / "repairs" / "20260902_normalize_vera_identity.sql").read_text(encoding="utf-8").lower()
    assert "delete from radar.identities" not in repair
    assert "delete from radar.endpoints" not in repair
    assert "'vera'" in repair
    assert "array['vera-sol']" in repair
    assert "'lane-vera'" in repair
    assert "'lane-vera-sol'" in repair
    assert "'archived'" in repair
    assert "'superseded_by', 'vera'" in repair
