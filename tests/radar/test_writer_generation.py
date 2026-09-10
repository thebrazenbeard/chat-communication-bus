import pytest

from radar.writer_generation import WriterGenerationError, build_generation_plan

SHA = lambda c: c * 40

ACTIVE = [
    'brigit','eight','five-five','five','fng','four','hephaestus','masa','mune','nine',
    'one','radar','seven','six','thirteen','three','two','vera','yang','yin'
]

CURRENT = {
    'brigit':'bus/bridget-v1','eight':'bus/eight-v2','five-five':'bus/five-five-v2',
    'five':'bus/five-v2','fng':'bus/fng-v2','four':'bus/four-v2','hephaestus':'bus/hephaestus-v3',
    'masa':'bus/masa-v2','mune':'bus/mune-v2','nine':'bus/nine-v2','one':'bus/one-v2',
    'radar':'bus/radar-v2','seven':'bus/seven-v2','six':'bus/six-v2','thirteen':'bus/thirteen-v2',
    'three':'bus/three-v2','two':'bus/two-v2','vera':'bus/vera-v2','yang':'bus/yang-v2','yin':'bus/yin-v2'
}
NEXT = {k: f"bus/{k}-v3" for k in ACTIVE}
NEXT['hephaestus'] = 'bus/hephaestus-v4'

STALE_A = {'ci.yml':'a'*40,'radar-bus-projection.yml':'b'*40,'writer-lane-guard.yml':'c'*40}
STALE_B = {'radar-bus-projection.yml':'d'*40}
CLEAN = {'ci.yml':'e'*40,'radar-central-dispatcher.yml':'f'*40,'radar-trusted-projector.yml':'1'*40,'writer-lane-guard.yml':'2'*40}


def contract():
    return {
        'schema_version': 1,
        'repository': 'thebrazenbeard/chat-communication-bus',
        'source_reference_commit': SHA('3'),
        'source_reference_tree': SHA('4'),
        'clean_bootstrap_workflow_blobs': CLEAN,
        'stale_generation_classes': {
            'A': {'identities':[x for x in ACTIVE if x != 'brigit'], 'workflow_blobs': STALE_A},
            'B': {'identities':['brigit'], 'workflow_blobs': STALE_B},
        },
        'successor_branches': dict(NEXT),
        'max_out_of_pocket_cost_usd': 0,
    }


def topology():
    lanes = {k:{'writer':k.title(),'branch':v,'lifecycle':'ACTIVE'} for k,v in CURRENT.items()}
    lanes['parallax'] = {'writer':'Parallax','branch':'bus/parallax-v1','lifecycle':'REGISTERED_INERT'}
    return {'required_writer_lanes': lanes}


def inventory():
    lanes = {}
    for idx, identity in enumerate(ACTIVE):
        head = f"{idx+10:040x}"[-40:]
        lanes[identity] = {
            'branch': CURRENT[identity],
            'head_sha': head,
            'workflow_blobs': STALE_B if identity == 'brigit' else STALE_A,
            'history_evidence': {
                'state': 'COMPLETE',
                'observed_head_sha': head,
                'message_count': idx + 1,
                'message_history_digest_sha256': f"{idx+1:064x}"[-64:],
            },
            'provider_cursor_evidence': {
                'observation_state': 'OBSERVED_ABSENT',
                'branch': CURRENT[identity],
                'projected_head_sha': None,
            },
        }
    return {'lanes': lanes}


def build(**overrides):
    args = dict(
        contract=contract(), topology=topology(), current_inventory=inventory(),
        bootstrap_commit_sha=SHA('5'), bootstrap_tree_sha=SHA('6'),
        bootstrap_workflow_blobs=CLEAN, existing_branches=set(CURRENT.values()) | {'bus/brigit-v2','bus/parallax-v1'},
    )
    args.update(overrides)
    return build_generation_plan(**args)


def test_builds_inert_plan_for_active_identities_only():
    plan = build()
    assert plan['schema'] == 'RADAR_WRITER_GENERATION_PLAN_V1'
    assert plan['activation_performed'] is False
    assert plan['provider_cursor_mutated'] is False
    assert plan['protected_effects_performed'] is False
    assert [x['identity'] for x in plan['lanes']] == sorted(ACTIVE)
    assert 'parallax' not in {x['identity'] for x in plan['lanes']}
    heph = next(x for x in plan['lanes'] if x['identity'] == 'hephaestus')
    assert heph['predecessor_branch'] == 'bus/hephaestus-v3'
    assert heph['successor_branch'] == 'bus/hephaestus-v4'
    assert heph['successor_state'] == 'PLANNED_INERT'
    assert heph['history_evidence']['state'] == 'COMPLETE'
    assert heph['history_evidence']['observed_head_sha'] == heph['predecessor_head_sha']
    assert heph['provider_cursor_evidence'] == {
        'observation_state': 'OBSERVED_ABSENT',
        'branch': 'bus/hephaestus-v3',
        'projected_head_sha': None,
    }


def test_rejects_inventory_branch_that_disagrees_with_topology():
    inv = inventory(); inv['lanes']['four']['branch'] = 'main'
    with pytest.raises(WriterGenerationError, match='CURRENT_BRANCH_MISMATCH:four'):
        build(current_inventory=inv)


def test_rejects_current_workflow_inventory_drift():
    inv = inventory(); inv['lanes']['four']['workflow_blobs'] = dict(STALE_A, surprise='9'*40)
    with pytest.raises(WriterGenerationError, match='CURRENT_WORKFLOW_INVENTORY_MISMATCH:four'):
        build(current_inventory=inv)


def test_rejects_bootstrap_with_legacy_projector():
    dirty = dict(CLEAN, **{'radar-bus-projection.yml':'9'*40})
    with pytest.raises(WriterGenerationError, match='BOOTSTRAP_LEGACY_PROJECTOR_PRESENT'):
        build(bootstrap_workflow_blobs=dirty)


def test_rejects_bootstrap_workflow_byte_drift():
    drift = dict(CLEAN); drift['writer-lane-guard.yml'] = '9'*40
    with pytest.raises(WriterGenerationError, match='BOOTSTRAP_WORKFLOW_INVENTORY_MISMATCH'):
        build(bootstrap_workflow_blobs=drift)


def test_rejects_existing_successor_branch_instead_of_overwriting():
    with pytest.raises(WriterGenerationError, match='SUCCESSOR_ALREADY_EXISTS:four'):
        build(existing_branches=set(CURRENT.values()) | {'bus/four-v3'})


def test_rejects_missing_successor_for_active_identity():
    c = contract(); del c['successor_branches']['yin']
    with pytest.raises(WriterGenerationError, match='SUCCESSOR_MAP_MISMATCH'):
        build(contract=c)


def test_rejects_successor_aliasing_current_or_another_successor():
    c = contract(); c['successor_branches']['four'] = CURRENT['four']
    with pytest.raises(WriterGenerationError, match='SUCCESSOR_EQUALS_CURRENT:four'):
        build(contract=c)
    c = contract(); c['successor_branches']['four'] = c['successor_branches']['five']
    with pytest.raises(WriterGenerationError, match='SUCCESSOR_BRANCH_DUPLICATE'):
        build(contract=c)


def test_rejects_nonzero_cost_contract():
    c = contract(); c['max_out_of_pocket_cost_usd'] = 1
    with pytest.raises(WriterGenerationError, match='NONZERO_COST_FORBIDDEN'):
        build(contract=c)


def test_requires_exact_sha_inputs():
    with pytest.raises(WriterGenerationError, match='BOOTSTRAP_COMMIT_INVALID'):
        build(bootstrap_commit_sha='main')
    with pytest.raises(WriterGenerationError, match='BOOTSTRAP_TREE_INVALID'):
        build(bootstrap_tree_sha='tree')


def test_accepts_observed_present_provider_cursor_and_preserves_exact_sha():
    inv = inventory()
    inv['lanes']['four']['provider_cursor_evidence'] = {
        'observation_state': 'OBSERVED_PRESENT',
        'branch': CURRENT['four'],
        'projected_head_sha': '9' * 40,
    }
    plan = build(current_inventory=inv)
    four = next(x for x in plan['lanes'] if x['identity'] == 'four')
    assert four['provider_cursor_evidence']['projected_head_sha'] == '9' * 40


@pytest.mark.parametrize(
    ('mutator', 'code'),
    [
        (lambda inv: inv['lanes']['four'].pop('history_evidence'), 'HISTORY_EVIDENCE_MISSING:four'),
        (lambda inv: inv['lanes']['four']['history_evidence'].__setitem__('state', 'INCOMPLETE'), 'HISTORY_INCOMPLETE:four'),
        (lambda inv: inv['lanes']['four']['history_evidence'].__setitem__('observed_head_sha', '9'*40), 'HISTORY_HEAD_MISMATCH:four'),
        (lambda inv: inv['lanes']['four']['history_evidence'].__setitem__('message_count', -1), 'HISTORY_MESSAGE_COUNT_INVALID:four'),
        (lambda inv: inv['lanes']['four']['history_evidence'].__setitem__('message_history_digest_sha256', 'bad'), 'HISTORY_DIGEST_INVALID:four'),
        (lambda inv: inv['lanes']['four'].pop('provider_cursor_evidence'), 'PROVIDER_CURSOR_EVIDENCE_MISSING:four'),
        (lambda inv: inv['lanes']['four']['provider_cursor_evidence'].__setitem__('observation_state', 'UNKNOWN'), 'PROVIDER_CURSOR_OBSERVATION_UNRESOLVED:four'),
        (lambda inv: inv['lanes']['four']['provider_cursor_evidence'].__setitem__('branch', 'bus/other'), 'PROVIDER_CURSOR_BRANCH_MISMATCH:four'),
        (lambda inv: inv['lanes']['four']['provider_cursor_evidence'].__setitem__('projected_head_sha', '9'*40), 'PROVIDER_CURSOR_ABSENT_WITH_HEAD:four'),
    ],
)
def test_rejects_incomplete_or_unobserved_history_and_cursor_evidence(mutator, code):
    inv = inventory(); mutator(inv)
    with pytest.raises(WriterGenerationError, match=code):
        build(current_inventory=inv)


def test_repository_contract_pins_observed_generations_and_clean_anchor_e_bytes():
    import json
    from pathlib import Path
    path = Path(__file__).parents[2] / 'architecture/contracts/RADAR_WRITER_GENERATION_V1.json'
    c = json.loads(path.read_text())
    assert c['source_reference_commit'] == 'ded270af1dbd51537bec92904e283da8d4183ff8'
    assert c['source_reference_tree'] == 'ecf31c90eadf43d6c7d838f1f4cb5c5f50ee7e97'
    assert 'radar-bus-projection.yml' not in c['clean_bootstrap_workflow_blobs']
    assert c['clean_bootstrap_workflow_blobs']['writer-lane-guard.yml'] == '460403230d93ff33d73204be9c7e900a3510155f'
    assert len(c['stale_generation_classes']['A']['identities']) == 19
    assert c['stale_generation_classes']['B']['identities'] == ['brigit']
    assert c['successor_branches']['brigit'] == 'bus/brigit-v3'
    assert c['successor_branches']['hephaestus'] == 'bus/hephaestus-v4'
    assert c['planning_evidence_requirements']['history_state'] == 'COMPLETE'
    assert c['planning_evidence_requirements']['provider_cursor_observation_states'] == ['OBSERVED_PRESENT', 'OBSERVED_ABSENT']
    assert c['max_out_of_pocket_cost_usd'] == 0
