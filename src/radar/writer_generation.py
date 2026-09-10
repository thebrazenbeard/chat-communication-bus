from __future__ import annotations

import re
from typing import Mapping, Iterable

_SHA40 = re.compile(r'^[0-9a-fA-F]{40}$')
_SHA256 = re.compile(r'^[0-9a-fA-F]{64}$')
_CURSOR_STATES = frozenset({'OBSERVED_PRESENT', 'OBSERVED_ABSENT'})


class WriterGenerationError(RuntimeError):
    pass


def _fail(code: str) -> None:
    raise WriterGenerationError(code)


def _sha(value, code: str) -> str:
    if not isinstance(value, str) or _SHA40.fullmatch(value) is None:
        _fail(code)
    return value.lower()


def _sha256(value, code: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        _fail(code)
    return value.lower()


def _workflow_map(value, code: str) -> dict[str, str]:
    if not isinstance(value, Mapping):
        _fail(code)
    out: dict[str, str] = {}
    for name, sha in value.items():
        if not isinstance(name, str) or not name or not isinstance(sha, str) or _SHA40.fullmatch(sha) is None:
            _fail(code)
        out[name] = sha.lower()
    return out


def _history_evidence(value, identity: str, expected_head: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        _fail(f'HISTORY_EVIDENCE_MISSING:{identity}')
    if value.get('state') != 'COMPLETE':
        _fail(f'HISTORY_INCOMPLETE:{identity}')
    observed_head = _sha(value.get('observed_head_sha'), f'HISTORY_HEAD_INVALID:{identity}')
    if observed_head != expected_head:
        _fail(f'HISTORY_HEAD_MISMATCH:{identity}')
    message_count = value.get('message_count')
    if not isinstance(message_count, int) or isinstance(message_count, bool) or message_count < 0:
        _fail(f'HISTORY_MESSAGE_COUNT_INVALID:{identity}')
    digest = _sha256(value.get('message_history_digest_sha256'), f'HISTORY_DIGEST_INVALID:{identity}')
    return {
        'state': 'COMPLETE',
        'observed_head_sha': observed_head,
        'message_count': message_count,
        'message_history_digest_sha256': digest,
    }


def _provider_cursor_evidence(value, identity: str, expected_branch: str) -> dict[str, object]:
    if not isinstance(value, Mapping):
        _fail(f'PROVIDER_CURSOR_EVIDENCE_MISSING:{identity}')
    state = value.get('observation_state')
    if state not in _CURSOR_STATES:
        _fail(f'PROVIDER_CURSOR_OBSERVATION_UNRESOLVED:{identity}')
    branch = value.get('branch')
    if branch != expected_branch:
        _fail(f'PROVIDER_CURSOR_BRANCH_MISMATCH:{identity}')
    projected = value.get('projected_head_sha')
    if state == 'OBSERVED_ABSENT':
        if projected is not None:
            _fail(f'PROVIDER_CURSOR_ABSENT_WITH_HEAD:{identity}')
        return {
            'observation_state': state,
            'branch': branch,
            'projected_head_sha': None,
        }
    projected_head = _sha(projected, f'PROVIDER_CURSOR_HEAD_INVALID:{identity}')
    return {
        'observation_state': state,
        'branch': branch,
        'projected_head_sha': projected_head,
    }


def build_generation_plan(
    *,
    contract: Mapping[str, object],
    topology: Mapping[str, object],
    current_inventory: Mapping[str, object],
    bootstrap_commit_sha: str,
    bootstrap_tree_sha: str,
    bootstrap_workflow_blobs: Mapping[str, str],
    existing_branches: Iterable[str],
) -> dict[str, object]:
    if contract.get('schema_version') != 1:
        _fail('CONTRACT_SCHEMA_INVALID')
    if contract.get('max_out_of_pocket_cost_usd') != 0:
        _fail('NONZERO_COST_FORBIDDEN')

    bootstrap_commit = _sha(bootstrap_commit_sha, 'BOOTSTRAP_COMMIT_INVALID')
    bootstrap_tree = _sha(bootstrap_tree_sha, 'BOOTSTRAP_TREE_INVALID')
    clean_expected = _workflow_map(contract.get('clean_bootstrap_workflow_blobs'), 'BOOTSTRAP_WORKFLOW_CONTRACT_INVALID')
    clean_observed = _workflow_map(bootstrap_workflow_blobs, 'BOOTSTRAP_WORKFLOW_INVENTORY_INVALID')
    if 'radar-bus-projection.yml' in clean_observed:
        _fail('BOOTSTRAP_LEGACY_PROJECTOR_PRESENT')
    if clean_observed != clean_expected:
        _fail('BOOTSTRAP_WORKFLOW_INVENTORY_MISMATCH')

    required = topology.get('required_writer_lanes')
    if not isinstance(required, Mapping):
        _fail('TOPOLOGY_INVALID')
    active = {
        identity: record
        for identity, record in required.items()
        if isinstance(record, Mapping) and record.get('lifecycle', 'ACTIVE') == 'ACTIVE'
    }
    active_ids = set(active)
    if not active_ids:
        _fail('ACTIVE_LANES_MISSING')

    successor_map = contract.get('successor_branches')
    if not isinstance(successor_map, Mapping) or set(successor_map) != active_ids:
        _fail('SUCCESSOR_MAP_MISMATCH')
    successors = list(successor_map.values())
    if any(not isinstance(branch, str) or not branch.startswith('bus/') for branch in successors):
        _fail('SUCCESSOR_BRANCH_INVALID')
    if len(set(successors)) != len(successors):
        _fail('SUCCESSOR_BRANCH_DUPLICATE')

    classes = contract.get('stale_generation_classes')
    if not isinstance(classes, Mapping):
        _fail('STALE_GENERATION_CLASSES_INVALID')
    expected_by_identity: dict[str, dict[str, str]] = {}
    for cls in classes.values():
        if not isinstance(cls, Mapping) or not isinstance(cls.get('identities'), list):
            _fail('STALE_GENERATION_CLASSES_INVALID')
        blobs = _workflow_map(cls.get('workflow_blobs'), 'STALE_GENERATION_CLASSES_INVALID')
        for identity in cls['identities']:
            if identity in expected_by_identity:
                _fail('STALE_GENERATION_IDENTITY_DUPLICATE')
            expected_by_identity[identity] = blobs
    if set(expected_by_identity) != active_ids:
        _fail('STALE_GENERATION_IDENTITY_MISMATCH')

    inv_lanes = current_inventory.get('lanes')
    if not isinstance(inv_lanes, Mapping) or set(inv_lanes) != active_ids:
        _fail('CURRENT_INVENTORY_IDENTITY_MISMATCH')

    existing = set(existing_branches)
    plan_lanes: list[dict[str, object]] = []
    for identity in sorted(active_ids):
        top = active[identity]
        inv = inv_lanes[identity]
        if not isinstance(inv, Mapping):
            _fail(f'CURRENT_INVENTORY_INVALID:{identity}')
        current_branch = top.get('branch')
        if not isinstance(current_branch, str) or inv.get('branch') != current_branch:
            _fail(f'CURRENT_BRANCH_MISMATCH:{identity}')
        head = _sha(inv.get('head_sha'), f'CURRENT_HEAD_INVALID:{identity}')
        observed_workflows = _workflow_map(inv.get('workflow_blobs'), f'CURRENT_WORKFLOW_INVENTORY_INVALID:{identity}')
        if observed_workflows != expected_by_identity[identity]:
            _fail(f'CURRENT_WORKFLOW_INVENTORY_MISMATCH:{identity}')

        history = _history_evidence(inv.get('history_evidence'), identity, head)
        cursor = _provider_cursor_evidence(inv.get('provider_cursor_evidence'), identity, current_branch)

        successor = successor_map[identity]
        if successor == current_branch:
            _fail(f'SUCCESSOR_EQUALS_CURRENT:{identity}')
        if successor in existing:
            _fail(f'SUCCESSOR_ALREADY_EXISTS:{identity}')

        plan_lanes.append({
            'identity': identity,
            'predecessor_branch': current_branch,
            'predecessor_head_sha': head,
            'history_evidence': history,
            'provider_cursor_evidence': cursor,
            'successor_branch': successor,
            'successor_state': 'PLANNED_INERT',
        })

    return {
        'schema': 'RADAR_WRITER_GENERATION_PLAN_V1',
        'repository': contract.get('repository'),
        'source_reference_commit': _sha(contract.get('source_reference_commit'), 'SOURCE_REFERENCE_COMMIT_INVALID'),
        'source_reference_tree': _sha(contract.get('source_reference_tree'), 'SOURCE_REFERENCE_TREE_INVALID'),
        'bootstrap_commit_sha': bootstrap_commit,
        'bootstrap_tree_sha': bootstrap_tree,
        'bootstrap_workflow_blobs': clean_observed,
        'lanes': plan_lanes,
        'activation_performed': False,
        'topology_mutated': False,
        'provider_cursor_mutated': False,
        'protected_effects_performed': False,
        'max_out_of_pocket_cost_usd': 0,
        'required_next_sequence': [
            'REVIEW_AND_REGISTER_PLANNED_SUCCESSORS',
            'CREATE_SUCCESSORS_FROM_EXACT_BOOTSTRAP',
            'VERIFY_SUCCESSOR_BOOTSTRAP',
            'EXPLICIT_TOPOLOGY_ACTIVATION',
            'FIRST_APPEND_EXACT_HEAD_VALIDATION',
            'RETIRE_PREDECESSOR_AFTER_ACTIVATION',
        ],
    }
