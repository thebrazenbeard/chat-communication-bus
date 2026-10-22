"""PORTAL V2 reviewer negative gates for mutable source/evidence fields."""
import copy
import json
from pathlib import Path
import unittest
from verify_live_two_pair_coordination import check_two_pair_contract
P=Path(__file__).with_name("PORTAL_LIVE_TWO_PAIR_COORDINATION_V2.json")

class SourceBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value=json.loads(P.read_text(encoding="utf-8"))

    def test_baseline_historic_scope_passes(self):
        self.assertEqual(check_two_pair_contract(self.value), [])

    def test_replaced_source_head_must_not_silently_pass(self):
        x=copy.deepcopy(self.value)
        x["heads_at_binding"]["mono_77"]="0"*40
        self.assertTrue(check_two_pair_contract(x))

    def test_provider_or_guest_ceiling_cannot_be_promoted(self):
        for k,v in (("provider_admission","QUALIFIED"),("graphical_guest","BOOTED"),
                    ("selected_runner_claim","LIVE"),("peer_acceptance","ACCEPTED")):
            x=copy.deepcopy(self.value)
            x["evidence_ceiling"][k]=v
            self.assertTrue(check_two_pair_contract(x),k)

    def test_historical_devices_not_current_connectivity(self):
        x=copy.deepcopy(self.value)
        x["connected_hosts_snapshot_is_historical"]=False
        self.assertTrue(check_two_pair_contract(x))

if __name__=="__main__":
    unittest.main()
