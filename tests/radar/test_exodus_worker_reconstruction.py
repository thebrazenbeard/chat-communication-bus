import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_exodus_worker_reconstruction_contract_has_only_three_persistent_interfaces():
    data = json.loads(
        (ROOT / 'architecture/contracts/WORKER_RUNTIME_RECONSTRUCTION_V1.json')
        .read_text(encoding='utf-8')
    )
    assert data['persistent_human_interfaces'] == [
        'Vera',
        'Vera Control Plane Coordinator',
        'BT2 Coordinator',
    ]
    assert data['terminal_rule']['execution_environments_are_terminals'] is True
    assert data['terminal_rule']['terminal_is_durable_identity'] is False
    assert 'named_permanent_worker_chat' in data['forbidden_recovery_dependencies']


def test_chat_local_lane_labels_do_not_become_independent_identities():
    data = json.loads(
        (ROOT / 'architecture/contracts/WORKER_RUNTIME_RECONSTRUCTION_V1.json')
        .read_text(encoding='utf-8')
    )
    labels = data['execution_label_classes']
    for name in ('SD1-E', 'SD1-V', 'BV', 'VW'):
        assert labels[name]['separate_identity'] is False


def test_current_vera_operational_docs_do_not_hardcode_historical_lane():
    identity = (ROOT / 'docs/protocol/VERA_PROJECT_IDENTITY_AND_ATTUNEMENT_V1.md').read_text(encoding='utf-8')
    writer = (ROOT / 'docs/protocol/SHARED_VERA_WRITER_SAFETY_V1.md').read_text(encoding='utf-8')
    assert 'bus/vera-sol-v1' not in identity
    assert 'bus/vera-sol-v1' not in writer
    assert 'RADAR_TOPOLOGY_V1.json' in identity
    assert 'RADAR_TOPOLOGY_V1.json' in writer


def test_recovery_flow_is_runtime_neutral():
    text = (ROOT / 'architecture/diagrams/recovery-flow.md').read_text(encoding='utf-8')
    assert 'Fresh Radar ChatGPT session' not in text
    assert 'Fresh Radar execution runtime' in text
    assert 'permanent Radar chat is not required' in text
