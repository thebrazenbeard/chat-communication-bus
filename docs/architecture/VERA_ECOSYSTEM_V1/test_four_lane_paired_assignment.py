"""Two named contributors per live execution lane; no runtime/authority inference.

Run: python -m unittest discover -s docs/architecture/VERA_ECOSYSTEM_V1 -p test_four_lane_paired_assignment.py -v
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
PAIRS = {
    "L1": (("Integration", "VN2", "source_owner"),
           ("PORTAL", "Lappy", "integration_contract_and_coordination")),
    "L2": (("Training", "Lappy", "cognitive_source_owner"),
           ("Integration", "VN2", "runtime_abi_reviewer")),
    "L3": (("VN1", "VERA-NODE-1", "independent_falsifier"),
           ("Training", "Lappy", "test_fixture_and_source_context_provider")),
    "L4": (("Codex", "Lappy", "single_serial_implementation_owner"),
           ("VN1", "VERA-NODE-1", "independent_falsifier")),
}


def validate(contract):
    problems = []
    if contract.get("schema") != "VERA_PORTAL_FOUR_LANE_PAIRED_ASSIGNMENT_V1":
        problems.append("unrecognized source contract")
    if contract.get("status") != "USER_DIRECT_ASSIGNMENT_SOURCE_CONTRACT_NOT_WORKER_EXECUTION_ATTESTATION":
        problems.append("assignment promoted to execution proof")
    if contract.get("execution_mode") != "ONE_LIVE_INVOCATION_NO_SCHEDULED_AUTOMATION":
        problems.append("scheduled or background operation substituted for live event")
    control = contract.get("governance", {})
    if control.get("coordinator") != "PORTAL" or control.get("coordinator_host") != "Lappy":
        problems.append("lost PORTAL coordination")
    required_true = (
        "active_chats_not_inferred_from_comments",
        "code_mutation_by_branch_owner_only",
        "peer_review_never_substitutes_for_independent_falsification",
        "one_serial_codex_worker", "no_duplicate_scheduler",
        "no_implicit_protected_effects",
    )
    if any(control.get(flag) is not True for flag in required_true):
        problems.append("owner, independent review, serial Codex, or authority fence missing")
    if control.get("accepted_architecture") != "HOLD_PENDING_SOURCE_SEMANTICS_AND_OWNER_ACCEPTANCE":
        problems.append("architecture accepted without owners")
    lanes = contract.get("lanes", [])
    if type(lanes) is not list or len(lanes) != 4:
        problems.append("exactly four paired lanes required")
        return problems
    identities = [x.get("id") for x in lanes]
    if len(set(identities)) != 4 or set(identities) != set(PAIRS):
        problems.append("duplicate or unrecognized lane identity")
    assignments = []
    for lane in lanes:
        lid = lane.get("id")
        for slot in ("primary", "second"):
            person = lane.get(slot)
            if type(person) is not dict or set(person) != {"worker", "host", "role"}:
                problems.append(f"{lid}: missing named {slot} contributor")
                continue
            assignments.append(person["worker"])
        expected = PAIRS.get(lid)
        if expected:
            actual = tuple(
                tuple(lane.get(slot, {}).get(field) for field in ("worker", "host", "role"))
                for slot in ("primary", "second")
            )
            if actual != expected:
                problems.append(f"{lid}: paired role/host drift")
        if len(lane.get("owned_subjects", [])) < 1 or not lane.get("handoff"):
            problems.append(f"{lid}: ownership or handoff missing")
    if assignments.count("Codex") != 1:
        problems.append("Codex not exactly one serial lane owner")
    if assignments.count("VN1") != 2 or any(
        slot.get("role") != "independent_falsifier"
        for lane in lanes for slot in (lane.get("primary", {}), lane.get("second", {}))
        if slot.get("worker") == "VN1"
    ):
        problems.append("VN1 independence violated")
    required_hosts = {"Lappy", "VERA-NODE-1", "VN2"}
    evidence = contract.get("live_binding_evidence", {})
    if set(evidence.get("executor_connected_devices", [])) != required_hosts:
        problems.append("host claims differ from verified device list")
    if evidence.get("integration_vn2_host") != "CONNECTED_AND_OWNER_SOURCE_RETURNED_NOT_VERA_RUNTIME_ATTESTED":
        problems.append("VN2 activation overstated")
    if evidence.get("vn1_architecture_guard") != "7_OF_7_ADVERSARIAL_MUTATIONS_FALSE_GREEN_REQUIRE_PORTAL_REPAIR":
        problems.append("independent source graph falsifiers hidden")
    banned = contract.get("prohibited_claims", [])
    if not any("two active processes" in x for x in banned):
        problems.append("no explicit process-activation evidence ceiling")
    return problems


class PairContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(
            (HERE / "PORTAL_FOUR_LANE_PAIRED_ASSIGNMENT_V1.json").read_text(encoding="utf-8")
        )

    def test_exact_four_lanes_two_assignees_each(self):
        self.assertEqual(validate(self.contract), [])
        self.assertEqual(sum(len([lane["primary"], lane["second"]])
                             for lane in self.contract["lanes"]), 8)

    def test_missing_second_worker_rejected(self):
        c = copy.deepcopy(self.contract)
        c["lanes"][0].pop("second")
        self.assertTrue(any("missing named" in x for x in validate(c)))

    def test_old_one_owner_lane_topology_rejected(self):
        c = copy.deepcopy(self.contract)
        c["lanes"] = c["lanes"][:3]
        self.assertTrue(any("four paired" in x for x in validate(c)))

    def test_changed_pair_or_host_rejected(self):
        c = copy.deepcopy(self.contract)
        c["lanes"][1]["second"]["worker"] = "PORTAL"
        self.assertTrue(any("paired role/host drift" in x for x in validate(c)))
        c = copy.deepcopy(self.contract)
        c["lanes"][0]["primary"]["host"] = "VERA-NODE-1"
        self.assertTrue(any("paired role/host drift" in x for x in validate(c)))

    def test_duplicate_codex_or_vn1_source_edit_role_rejected(self):
        c = copy.deepcopy(self.contract)
        c["lanes"][0]["second"] = dict(c["lanes"][3]["primary"])
        self.assertTrue(any("Codex not exactly one" in x for x in validate(c)))
        c = copy.deepcopy(self.contract)
        c["lanes"][3]["second"]["role"] = "implementation_owner"
        self.assertTrue(any("VN1 independence violated" in x for x in validate(c)))

    def test_no_scheduling_or_fabricated_execution(self):
        for field, value in (
            ("execution_mode", "HOURLY_SCHEDULED_CHECK"),
            ("status", "ALL_WORKERS_RUNNING"),
        ):
            c = copy.deepcopy(self.contract)
            c[field] = value
            self.assertTrue(validate(c))

    def test_no_implicit_authority_or_owner_acceptance(self):
        for field in ("no_implicit_protected_effects", "code_mutation_by_branch_owner_only"):
            c = copy.deepcopy(self.contract)
            c["governance"][field] = False
            self.assertTrue(validate(c))
        c = copy.deepcopy(self.contract)
        c["governance"]["accepted_architecture"] = "LOCKED_V1"
        self.assertTrue(any("without owners" in x for x in validate(c)))

    def test_host_evidence_and_vn1_adversarial_red_preserved(self):
        c = copy.deepcopy(self.contract)
        c["live_binding_evidence"]["executor_connected_devices"] = ["Lappy", "VERA-NODE-1"]
        self.assertTrue(any("host claims" in x for x in validate(c)))
        c = copy.deepcopy(self.contract)
        c["live_binding_evidence"]["vn1_architecture_guard"] = "ALL_PASS"
        self.assertTrue(any("falsifiers hidden" in x for x in validate(c)))


if __name__ == "__main__":
    unittest.main()
