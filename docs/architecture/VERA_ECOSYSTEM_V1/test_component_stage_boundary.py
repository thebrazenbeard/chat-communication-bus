"""Regression fence: source staging is not full host-service boot admission.

Run: python -m unittest discover -s docs/architecture/VERA_ECOSYSTEM_V1 -p test_component_stage_boundary.py
Tests review artifacts, not a Buildroot image, import closure, or running guest.
"""
import json
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def classify_current_stage(bom, graph):
    """Fail closed if the review BOM turns a stage proposal into boot authority."""
    staged = bom["staged_sources"]
    if len(staged) != 4 or len({x["repo"] for x in staged}) != 4:
        raise ValueError("four distinct source selections required")
    counts = {x["repo"]: x["files"] for x in staged}
    if counts != {"vera-mono": 316, "portal": 89, "pre-active": 18, "volition": 8}:
        raise ValueError("current 431-source composition drift")
    if sum(counts.values()) != bom["staged_total_files"]:
        raise ValueError("stage count mismatch")
    stage_edges = [e for e in graph["edges"] if e["type"] == "STAGED_SOURCE_SNAPSHOT"]
    if len(stage_edges) != 4 or {e["to"] for e in stage_edges} != set(counts):
        raise ValueError("typed stage mismatch")
    if any(e["from"] != "vera-os" or e.get("not_guest_boot_required") is not True
           for e in stage_edges):
        raise ValueError("source snapshot illegally promoted to boot dependency")
    if any(e["type"] == "VERIFIED_HARD_RUNTIME_IMPORT" for e in graph["edges"]):
        raise ValueError("hard runtime closure not evidenced by this source review")
    portal = next(x for x in staged if x["repo"] == "portal")
    if "NOT full host scheduler" not in portal["placement"]:
        raise ValueError("selected PORTAL source confused with full Windows host service")
    gates = {x["gate"]: x["status"] for x in bom["acceptance"]}
    for gate in ("KCONFIG", "IMAGE", "TARGET_IMPORT", "NORMAL_GUI", "COLD_TWO_BOOT"):
        if gates[gate] in ("PASS", "QUALIFIED", "SOURCE_ONLY_GREEN"):
            raise ValueError("unproven target or guest gate promoted")
    if bom["image_produces_authority"] is not False:
        raise ValueError("source/image promoted to effect authority")
    return counts


class StageBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bom = json.loads((HERE / "VERAOS_MINIMAL_BOM_V1.json").read_text(encoding="utf-8"))
        cls.graph = json.loads((HERE / "VERA_96_TYPED_DEPENDENCY_EDGES_V1.json").read_text(encoding="utf-8"))

    def test_current_selected_source_stage_not_full_portal_process(self):
        self.assertEqual(classify_current_stage(self.bom, self.graph)["portal"], 89)

    def test_false_host_service_promotion_rejected(self):
        import copy
        bom = copy.deepcopy(self.bom)
        next(x for x in bom["staged_sources"] if x["repo"] == "portal")["placement"] = "full Windows scheduler required"
        with self.assertRaisesRegex(ValueError, "full Windows host"):
            classify_current_stage(bom, self.graph)

    def test_lighter_mono_only_cannot_replace_current_stage_by_assertion(self):
        import copy
        bom = copy.deepcopy(self.bom)
        bom["staged_sources"] = [x for x in bom["staged_sources"] if x["repo"] == "vera-mono"]
        bom["staged_total_files"] = 316
        with self.assertRaisesRegex(ValueError, "four distinct"):
            classify_current_stage(bom, self.graph)

    def test_staged_edge_and_guest_gate_promotions_rejected(self):
        import copy
        graph = copy.deepcopy(self.graph)
        next(e for e in graph["edges"] if e["type"] == "STAGED_SOURCE_SNAPSHOT")["not_guest_boot_required"] = False
        with self.assertRaisesRegex(ValueError, "boot dependency"):
            classify_current_stage(self.bom, graph)
        bom = copy.deepcopy(self.bom)
        next(e for e in bom["acceptance"] if e["gate"] == "NORMAL_GUI")["status"] = "PASS"
        with self.assertRaisesRegex(ValueError, "guest gate promoted"):
            classify_current_stage(bom, self.graph)


if __name__ == "__main__":
    unittest.main()
