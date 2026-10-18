"""Adversarial source-cut tests; not five-chat acceptance or guest execution."""
import copy
import unittest

from verify_five_surface_cut import (
    check_source_cut, cut_report, load_artifacts, CURRENT_STAGE,
)


class FiveSurfaceSourceCutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.portfolio, cls.typed, cls.bom = load_artifacts()

    def errors(self, portfolio=None, typed=None, bom=None):
        return check_source_cut(
            self.portfolio if portfolio is None else portfolio,
            self.typed if typed is None else typed,
            self.bom if bom is None else bom,
        )

    def test_all_96_and_147_plus_four_consistent(self):
        self.assertEqual(self.errors(), [])
        r = cut_report(self.portfolio, self.typed, self.bom)
        self.assertEqual(
            (r["repository_dispositions"], r["proposed_consumer_links"],
             r["selected_source_snapshots"]), (96, 147, 4))
        self.assertEqual(r["reviewed_five_surface_architecture"], "HOLD_PENDING_OWNER_ACCEPTANCE")

    def test_missing_placement_or_owner_rejected(self):
        p = copy.deepcopy(self.portfolio)
        p["repositories"][0]["owner"] = ""
        self.assertTrue(any("missing mechanism" in x for x in self.errors(portfolio=p)))

    def test_missing_proposed_consumer_rejected(self):
        g = copy.deepcopy(self.typed)
        g["edges"] = [e for i, e in enumerate(g["edges"]) if i != 0]
        self.assertTrue(any("147 proposed" in x for x in self.errors(typed=g)))

    def test_forged_hard_runtime_import_rejected(self):
        g = copy.deepcopy(self.typed)
        g["edges"][0]["type"] = "VERIFIED_HARD_RUNTIME_IMPORT"
        self.assertTrue(any("hard runtime import" in x for x in self.errors(typed=g)))

    def test_selected_four_source_composition_cannot_shrink_by_assertion(self):
        b = copy.deepcopy(self.bom)
        b["staged_sources"] = [r for r in b["staged_sources"] if r["repo"] == "vera-mono"]
        b["staged_total_files"] = 316
        self.assertEqual(sum(CURRENT_STAGE.values()), 431)
        self.assertTrue(any("431-file stage" in x for x in self.errors(bom=b)))

    def test_portal_full_host_is_not_guest_required(self):
        p = copy.deepcopy(self.portfolio)
        row = next(r for r in p["repositories"] if r["repository"] == "portal")
        row["in_veraos_minimal_image"] = True
        self.assertTrue(any("full PORTAL host" in x for x in self.errors(portfolio=p)))

    def test_fake_graphical_boot_pass_rejected(self):
        b = copy.deepcopy(self.bom)
        next(r for r in b["acceptance"] if r["gate"] == "NORMAL_GUI")["status"] = "PASS"
        self.assertTrue(any("falsely passed" in x for x in self.errors(bom=b)))

    def test_effect_authority_never_follows_source_stage(self):
        b = copy.deepcopy(self.bom)
        b["image_produces_authority"] = True
        self.assertTrue(any("effect authority" in x for x in self.errors(bom=b)))
        p = copy.deepcopy(self.portfolio)
        p["repositories"][0]["runtime_admission"]["effect_authority"] = "SOURCE_GRANTED"
        self.assertTrue(any("unapproved effect authority" in x for x in self.errors(portfolio=p)))


if __name__ == "__main__":
    unittest.main()
