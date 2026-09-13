import json
from pathlib import Path


def test_contract_reconciles_cursor_facility_before_successor_creation():
    path = Path(__file__).parents[2] / 'architecture/contracts/RADAR_WRITER_GENERATION_V1.json'
    sequence = json.loads(path.read_text())['required_order']
    reconciliation = 'PROVIDER_CURSOR_RECONCILIATION_REQUIRED_BEFORE_ACTIVATION_OR_CURRENT_ROUTE_CLAIM_IF_FACILITY_NOT_INSTALLED'
    assert sequence.index(reconciliation) < sequence.index('CREATE_SUCCESSORS_FROM_EXACT_BOOTSTRAP')
    assert sequence.index('CREATE_SUCCESSORS_FROM_EXACT_BOOTSTRAP') < sequence.index('VERIFY_SUCCESSOR_BOOTSTRAP')
