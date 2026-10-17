"""Hostile typed-dependency review tests; no guest/runtime execution."""
import copy
import json
import unittest
from pathlib import Path
from build_typed_dependency_edges import (
    construct, validate_edges, _cycle, STAGE_PINS,
)

HERE=Path(__file__).resolve().parent
FILE=HERE/"VERA_96_TYPED_DEPENDENCY_EDGES_V1.json"
SIX={"portal","vera-mono","vera-os","vera-apk","model-training","executor"}
class TypedEdgesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph=construct()
    def test_catalog_and_proposed_consumers_exact(self):
        x=self.graph
        self.assertEqual(len(x["repositories"]),96)
        self.assertEqual(len(set(x["repositories"])),96)
        self.assertEqual(x["consumer_edge_count"],147)
        self.assertEqual(len(x["edges"]),151)
    def test_no_proposal_is_promoted_to_hard_runtime(self):
        x=self.graph
        self.assertEqual(validate_edges(x)["hard_runtime_imports"],0)
        self.assertEqual(len([e for e in x["edges"]
                             if e["type"]=="PROPOSED_CONSUMER"]),147)
        self.assertEqual(len([e for e in x["edges"]
                             if e["type"]=="STAGED_SOURCE_SNAPSHOT"]),4)
    def test_stage_pins_are_source_not_guest_requirement(self):
        stage=[e for e in self.graph["edges"] if e["type"]=="STAGED_SOURCE_SNAPSHOT"]
        self.assertEqual({e["to"]:e["source_head"] for e in stage},STAGE_PINS)
        self.assertTrue(all(e["from"]=="vera-os" and e["not_guest_boot_required"] for e in stage))
    def test_naively_promoted_consumer_edges_have_boot_cycle(self):
        full=[e for e in self.graph["edges"] if e["type"]=="PROPOSED_CONSUMER"]
        cycle=_cycle(full)
        self.assertTrue(cycle,"untyped graph incorrectly appears acyclic")
        self.assertTrue(SIX <= set(e["from"] for e in full)|set(e["to"] for e in full))
    def test_unproven_hard_dependency_fails_closed(self):
        changed=copy.deepcopy(self.graph)
        row=next(e for e in changed["edges"] if e["type"]=="PROPOSED_CONSUMER")
        row["type"]="VERIFIED_HARD_RUNTIME_IMPORT"
        with self.assertRaisesRegex(ValueError,"unproved hard runtime"):
            validate_edges(changed)
    def test_forged_strings_cannot_promote_acyclic_hard_import(self):
        changed=copy.deepcopy(self.graph)
        row=next(e for e in changed["edges"] if e["type"]=="PROPOSED_CONSUMER")
        row["type"]="VERIFIED_HARD_RUNTIME_IMPORT"
        row["runtime_import_proof"]={
            "consumer_commit":"a"*40,"importer_file_blob":"b"*40,
            "imported_module":"fake","verified_test":"fake"}
        with self.assertRaisesRegex(ValueError,"lacks independent source verification"):
            validate_edges(changed)
    def test_six_node_proposal_subgraph_has_false_runtime_cycle(self):
        six_edges=[e for e in self.graph["edges"]
            if e["type"]=="PROPOSED_CONSUMER"
            and e["from"] in SIX and e["to"] in SIX]
        self.assertTrue(_cycle(six_edges))
        self.assertFalse(_cycle([e for e in six_edges if e["type"]=="VERIFIED_HARD_RUNTIME_IMPORT"]))
    def test_claimed_proof_is_not_enough_if_hard_cycle_exists(self):
        changed=copy.deepcopy(self.graph)
        for e in changed["edges"]:
            if e["type"]=="PROPOSED_CONSUMER":
                e["type"]="VERIFIED_HARD_RUNTIME_IMPORT"
                e["runtime_import_proof"]={
                  "consumer_commit":"a"*40,"importer_file_blob":"b"*40,
                  "imported_module":"fake","verified_test":"fake"}
        with self.assertRaisesRegex(ValueError,"runtime cycle"):
            validate_edges(changed)
    def test_unsupported_type_and_duplicates_rejected(self):
        changed=copy.deepcopy(self.graph)
        changed["edges"][0]["type"]="SECRETLY_DEPLOYED"
        with self.assertRaisesRegex(ValueError,"unknown type"):
            validate_edges(changed)
        changed=copy.deepcopy(self.graph)
        changed["edges"].append(copy.deepcopy(changed["edges"][0]))
        with self.assertRaisesRegex(ValueError,"duplicate edge"):
            validate_edges(changed)
    def test_emitted_json_matches_generator(self):
        self.assertEqual(json.loads(FILE.read_text(encoding="utf-8")),self.graph)
if __name__=="__main__":
    unittest.main()
