import json
from pathlib import Path

import pytest

from radar.writer_generation import WriterGenerationError, build_generation_plan

SHA = lambda c: c * 40
BRANCH = 'bus/four-v2'
REQUIRED_MIGRATION = '20260906154101_radar_projection_journal_v1'
PROVIDER_CEILING = '20260903113314_radar_operator_views_v1'
CLEAN = {'ci.yml': 'e' * 40}
STALE = {'ci.yml': 'a' * 40}


def contract():
    return {
        'schema_version': 1,
        'repository': 'thebrazenbeard/chat-communication-bus',
        'source_reference_commit': SHA('3'),
        'source_reference_tree': SHA('4'),
        'planning_evidence_requirements': {
            'provider_cursor_required_migration': REQUIRED_MIGRATION,
        },
        'clean_bootstrap_workflow_blobs': CLEAN,
        'stale_generation_classes': {
            'A': {'identities': ['four'], 'workflow_blobs': STALE},
        },
        'successor_branches': {'four': 'bus/four-v3'},
        'max_out_of_pocket_cost_usd': 0,
    }


def inventory(cursor):
    return {
        'lanes': {
            'four': {
                'branch': BRANCH,
                'head_sha': SHA('7'),
                'workflow_blobs': STALE,
                'history_evidence': {
                    'state': 'COMPLETE',
                    'observed_head_sha': SHA('7'),
                    'message_count': 1,
                    'message_history_digest_sha256': '8' * 64,
                },
                'provider_cursor_evidence': cursor,
            },
        },
    }


def build(cursor):
    return build_generation_plan(
        contract=contract(),
        topology={
            'required_writer_lanes': {
                'four': {'branch': BRANCH, 'lifecycle': 'ACTIVE'},
            },
        },
        current_inventory=inventory(cursor),
        bootstrap_commit_sha=SHA('5'),
        bootstrap_tree_sha=SHA('6'),
        bootstrap_workflow_blobs=CLEAN,
        existing_branches={BRANCH},
    )


def facility(**overrides):
    value = {
        'observation_state': 'CURSOR_FACILITY_NOT_INSTALLED',
        'branch': BRANCH,
        'projected_head_sha': None,
        'provider_migration_ceiling': PROVIDER_CEILING,
        'required_cursor_migration': REQUIRED_MIGRATION,
        'cursor_relation_observation': 'RELATION_NOT_INSTALLED_42P01',
    }
    value.update(overrides)
    return value


def test_facility_not_installed_is_preserved_and_forces_reconciliation():
    plan = build(facility())
    evidence = plan['lanes'][0]['provider_cursor_evidence']
    assert evidence == facility()
    assert plan['provider_cursor_reconciliation_required'] is True
    assert (
        'PROVIDER_CURSOR_RECONCILIATION_REQUIRED_BEFORE_ACTIVATION_OR_CURRENT_ROUTE_CLAIM'
        in plan['required_next_sequence']
    )


def test_facility_not_installed_blocks_successor_creation_until_reconciliation():
    plan = build(facility())
    sequence = plan['required_next_sequence']
    assert sequence[:4] == [
        'REVIEW_AND_REGISTER_PLANNED_SUCCESSORS',
        'PROVIDER_CURSOR_RECONCILIATION_REQUIRED_BEFORE_ACTIVATION_OR_CURRENT_ROUTE_CLAIM',
        'CREATE_SUCCESSORS_FROM_EXACT_BOOTSTRAP',
        'VERIFY_SUCCESSOR_BOOTSTRAP',
    ]


def test_facility_not_installed_rejects_missing_ceiling():
    value = facility()
    value.pop('provider_migration_ceiling')
    with pytest.raises(WriterGenerationError, match='PROVIDER_CURSOR_MIGRATION_CEILING_INVALID:four'):
        build(value)


def test_facility_not_installed_rejects_wrong_required_migration():
    with pytest.raises(WriterGenerationError, match='PROVIDER_CURSOR_REQUIRED_MIGRATION_MISMATCH:four'):
        build(facility(required_cursor_migration='20260908000000_wrong'))


def test_facility_not_installed_rejects_non_null_head():
    with pytest.raises(WriterGenerationError, match='PROVIDER_CURSOR_FACILITY_NOT_INSTALLED_WITH_HEAD:four'):
        build(facility(projected_head_sha='9' * 40))


def test_facility_not_installed_requires_relation_observation():
    value = facility()
    value.pop('cursor_relation_observation')
    with pytest.raises(WriterGenerationError, match='PROVIDER_CURSOR_RELATION_OBSERVATION_INVALID:four'):
        build(value)


@pytest.mark.parametrize(
    'ceiling',
    [
        REQUIRED_MIGRATION,
        '20260906154101_aaa',
        '20260907000000_later',
    ],
)
def test_facility_not_installed_rejects_ceiling_not_strictly_before_required_version(ceiling):
    with pytest.raises(WriterGenerationError, match='PROVIDER_CURSOR_FACILITY_STATE_CONTRADICTED:four'):
        build(facility(provider_migration_ceiling=ceiling))


def test_observed_absent_remains_distinct_and_does_not_force_reconciliation():
    plan = build({
        'observation_state': 'OBSERVED_ABSENT',
        'branch': BRANCH,
        'projected_head_sha': None,
    })
    assert plan['lanes'][0]['provider_cursor_evidence']['observation_state'] == 'OBSERVED_ABSENT'
    assert plan['provider_cursor_reconciliation_required'] is False
    assert (
        'PROVIDER_CURSOR_RECONCILIATION_REQUIRED_BEFORE_ACTIVATION_OR_CURRENT_ROUTE_CLAIM'
        not in plan['required_next_sequence']
    )


def test_repository_contract_records_facility_not_installed_semantics():
    path = Path(__file__).parents[2] / 'architecture/contracts/RADAR_WRITER_GENERATION_V1.json'
    requirements = json.loads(path.read_text())['planning_evidence_requirements']
    assert requirements['provider_cursor_facility_state'] == 'CURSOR_FACILITY_NOT_INSTALLED'
    assert requirements['provider_cursor_required_migration'] == REQUIRED_MIGRATION
    assert requirements['provider_cursor_facility_relation_observation'] == 'RELATION_NOT_INSTALLED_42P01'
