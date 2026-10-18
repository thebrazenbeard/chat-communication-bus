"""Adversarial mutations that passed the original five-surface shape-only checker.

These tests protect an immutable reviewed *source snapshot*. They cannot certify
the source assertions as true, owner-authenticated or selected at runtime.
"""
from __future__ import annotations

import copy
import unittest

from verify_five_surface_cut import check_source_cut, load_artifacts

class SemanticEvidenceLockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_artifacts()

    def check_mutation(self, change):
        p, t, b = copy.deepcopy(self.baseline)
        change(p, t, b)
        self.assertTrue(check_source_cut(p, t, b),
                        "semantic mutation falsely accepted against frozen baseline")

    def test_frozen_baseline_itself_accepted(self):
        self.assertEqual(check_source_cut(*self.baseline), [])

    def test_invented_nonempty_owner_rejected(self):
        self.check_mutation(lambda p,t,b: p["repositories"][0].__setitem__(
            "owner", "Invented owner with no source or review"))

    def test_fake_forty_character_source_sha_rejected(self):
        self.check_mutation(lambda p,t,b: p["repositories"][0].__setitem__(
            "default_head", "0"*40))

    def test_swapped_os_and_android_interface_rejected(self):
        def swap(p,t,b):
            a = next(x for x in p["repositories"] if x["repository"] == "vera-apk")
            o = next(x for x in p["repositories"] if x["repository"] == "vera-os")
            a["interface_kind"], o["interface_kind"] = o["interface_kind"], a["interface_kind"]
        self.check_mutation(swap)

    def test_mutually_edited_catalog_and_edge_still_rejected(self):
        def change(p,t,b):
            row = next(x for x in p["repositories"] if x["repository"] == "abil")
            assert "portal" in row["intended_consumers"]
            assert "vera-mono" not in row["intended_consumers"]
            row["intended_consumers"].remove("portal")
            row["intended_consumers"].append("vera-mono")
            edge = next(x for x in t["edges"] if x["type"] == "PROPOSED_CONSUMER"
                        and x["from"] == "abil" and x["to"] == "portal")
            edge["to"] = "vera-mono"
        self.check_mutation(change)

    def test_consistent_bogus_staged_receipt_rejected(self):
        def change(p,t,b):
            for e in t["edges"]:
                if e["type"] == "STAGED_SOURCE_SNAPSHOT":
                    e["stage_receipt_sha256"] = "0"*64
        self.check_mutation(change)

    def test_arbitrary_gui_status_not_silently_admitted(self):
        def change(p,t,b):
            entry = next(x for x in b["acceptance"] if x["gate"] == "NORMAL_GUI")
            entry["status"] = "UNKNOWN_BUT_WE_ASSUME_GOOD"
        self.check_mutation(change)

    def test_silent_mono_image_removal_rejected(self):
        def change(p,t,b):
            next(x for x in p["repositories"] if x["repository"] == "vera-mono")[
                "in_veraos_minimal_image"] = False
        self.check_mutation(change)

    def test_replacement_of_signed_snapshot_requires_rebind(self):
        def change(p,t,b):
            p["repositories"][0]["acceptance_gate"] += "; user changed policy"
        self.check_mutation(change)

if __name__ == "__main__":
    unittest.main()
