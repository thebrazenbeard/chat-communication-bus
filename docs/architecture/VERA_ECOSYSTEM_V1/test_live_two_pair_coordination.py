"""Live two-pair protocol regression: no silent return to overlapping four-lane slots.

This validates an *assignment and handoff* document, never authenticates other
conversations, an active process, runtime installation, selected routes or effects.
"""
import copy
import json
from pathlib import Path
import unittest

from verify_live_two_pair_coordination import check_two_pair_contract

HERE = Path(__file__).resolve().parent
DOC = HERE / "PORTAL_LIVE_TWO_PAIR_COORDINATION_V2.json"


class LiveTwoPairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(DOC.read_text(encoding="utf-8"))

    def test_exactly_two_cross_host_pairs_with_portal_review(self):
        self.assertEqual(check_two_pair_contract(self.source), [])
        self.assertEqual({p["id"] for p in self.source["pairs"]},
                         {"INTEGRATION_TRAINING", "CODEX_VN1"})

    def test_third_pair_or_four_overlapping_lanes_rejected(self):
        x = copy.deepcopy(self.source)
        x["pairs"].append(copy.deepcopy(x["pairs"][0]))
        self.assertTrue(check_two_pair_contract(x))
        x = copy.deepcopy(self.source)
        x["execution_topology"] = "FOUR_OVERLAPPING_LANES"
        self.assertTrue(check_two_pair_contract(x))

    def test_missing_partner_and_disconnected_pair_rejected(self):
        x = copy.deepcopy(self.source)
        x["pairs"][0]["partners"].pop()
        self.assertTrue(check_two_pair_contract(x))
        x = copy.deepcopy(self.source)
        x["pairs"][1]["shared_work_packet"] = ""
        self.assertTrue(check_two_pair_contract(x))

    def test_swapped_hosts_and_undeclared_workers_rejected(self):
        x = copy.deepcopy(self.source)
        x["pairs"][0]["partners"][0]["host"] = "VERA-NODE-1"
        self.assertTrue(check_two_pair_contract(x))
        x = copy.deepcopy(self.source)
        x["pairs"][1]["partners"][1]["worker"] = "PORTAL"
        self.assertTrue(check_two_pair_contract(x))

    def test_codex_single_worker_and_vn1_independence(self):
        x = copy.deepcopy(self.source)
        x["governance"]["single_serial_codex"] = False
        self.assertTrue(check_two_pair_contract(x))
        x = copy.deepcopy(self.source)
        x["pairs"][1]["partners"][1]["role"] = "code_coauthor"
        self.assertTrue(check_two_pair_contract(x))

    def test_portal_is_reviewing_both_pairs_not_third_worker(self):
        x = copy.deepcopy(self.source)
        x["coordinator"]["review_scope"] = ["INTEGRATION_TRAINING"]
        self.assertTrue(check_two_pair_contract(x))
        x = copy.deepcopy(self.source)
        x["pairs"][0]["partners"][1]["worker"] = "PORTAL"
        self.assertTrue(check_two_pair_contract(x))

    def test_no_scheduling_or_false_worker_activation(self):
        x = copy.deepcopy(self.source)
        x["mode"] = "HOURLY_TASK"
        self.assertTrue(check_two_pair_contract(x))
        x = copy.deepcopy(self.source)
        x["claimed_activity"] = "BOTH_PAIRS_RUNNING_UNATTENDED"
        self.assertTrue(check_two_pair_contract(x))

    def test_preserve_canonical_authority_and_guest_hold(self):
        x = copy.deepcopy(self.source)
        x["governance"]["protected_effects"] = "PREAUTHORIZED"
        self.assertTrue(check_two_pair_contract(x))
        x = copy.deepcopy(self.source)
        x["governance"]["architecture_acceptance"] = "LOCKED"
        self.assertTrue(check_two_pair_contract(x))

    def test_pair_returns_require_two_distinct_evidence_sources(self):
        x = copy.deepcopy(self.source)
        x["return_requirements"].remove("each_partner_distinct_source_and_test")
        self.assertTrue(check_two_pair_contract(x))
        x = copy.deepcopy(self.source)
        x["governance"]["comments_are_worker_execution_proof"] = True
        self.assertTrue(check_two_pair_contract(x))

    def test_legacy_four_lane_contract_explicitly_superseded(self):
        x = copy.deepcopy(self.source)
        x["supersedes"] = []
        self.assertTrue(check_two_pair_contract(x))


if __name__ == "__main__":
    unittest.main()
