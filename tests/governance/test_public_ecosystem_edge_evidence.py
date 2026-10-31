"""Require public-safe, provenance-bound distinctions for sampled ecosystem edges."""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "portfolio" / "PUBLIC_ONLY_OWNER_INVENTORY_V1.json"
EDGES = ROOT / "portfolio" / "PUBLIC_ECOSYSTEM_EDGE_EVIDENCE_V1.json"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
TYPES = {"DOC_LINK", "DEPENDENCY", "SOURCE_IMPORT", "TEST", "HOST_PROBE", "UNKNOWN"}
EVIDENCE = {"DOC", "DEP_METADATA", "SOURCE_INSPECTION", "TEST", "REAL_SYSTEM_PROBE"}


def validate(data, inventory):
    assert set(data) == {
        "schema", "event_id", "observed_at_utc", "scope", "inventory",
        "relation_type_vocabulary", "relations", "limitations",
    }
    assert data["schema"] == "CCB_PUBLIC_ECOSYSTEM_EDGE_EVIDENCE_V1"
    assert data["event_id"] == "project_unfuck_runtime_coordination"
    assert data["scope"] == "SAMPLED_PUBLIC_SOURCE_ONLY_NOT_EXHAUSTIVE"
    assert data["inventory"] == "portfolio/PUBLIC_ONLY_OWNER_INVENTORY_V1.json"
    assert data["observed_at_utc"] == inventory["observed_at_utc"]
    assert set(data["relation_type_vocabulary"]) == TYPES
    heads = {item["repository_full_name"]: item["head_sha"] for item in inventory["public_repositories"]}
    seen = set()
    assert isinstance(data["relations"], list) and data["relations"]
    for edge in data["relations"]:
        assert set(edge) == {"source", "target", "relation_type", "evidence_class", "finding", "evidence", "authority"}
        assert edge["source"] != edge["target"]
        assert edge["source"] in heads and edge["target"] in heads
        assert edge["relation_type"] in TYPES
        assert edge["evidence_class"] in EVIDENCE
        assert edge["relation_type"] != "HOST_PROBE" or edge["evidence_class"] == "REAL_SYSTEM_PROBE"
        assert edge["relation_type"] != "DOC_LINK" or edge["evidence_class"] == "DOC"
        assert edge["authority"] in {"DOCUMENTATION_ONLY_NOT_HOST_RUNTIME", "PACKAGE_METADATA_NOT_HOST_INSTALL"}
        assert edge["relation_type"] != "DOC_LINK" or edge["authority"] == "DOCUMENTATION_ONLY_NOT_HOST_RUNTIME"
        assert edge["relation_type"] != "UNKNOWN" or edge["authority"] == "PACKAGE_METADATA_NOT_HOST_INSTALL"
        assert isinstance(edge["finding"], str) and edge["finding"].strip()
        assert isinstance(edge["evidence"], list) and edge["evidence"]
        key = (edge["source"], edge["target"], edge["relation_type"])
        assert key not in seen
        seen.add(key)
        for proof in edge["evidence"]:
            assert set(proof) == {"repository", "head_sha", "path", "blob_sha"}
            assert proof["repository"] in (edge["source"], edge["target"])
            assert proof["repository"] in heads
            assert proof["head_sha"] == heads[proof["repository"]]
            assert SHA40.fullmatch(proof["blob_sha"])
            assert proof["path"] and ".." not in Path(proof["path"]).parts
    assert isinstance(data["limitations"], list) and data["limitations"]


def test_public_source_evidence_edges_are_bounded():
    validate(json.loads(EDGES.read_text(encoding="utf-8")), json.loads(INVENTORY.read_text(encoding="utf-8")))


@pytest.mark.parametrize("mutation", [
    lambda x: x["relations"][0].update(target="thebrazenbeard/private-example"),
    lambda x: x["relations"][0].update(relation_type="HOST_PROBE"),
    lambda x: x["relations"][0]["evidence"][0].update(head_sha="0" * 40),
    lambda x: x["relations"][0]["evidence"][0].update(path="../secret"),
    lambda x: x["relations"][0].update(authority="HOST_AUTHORIZED"),
])
def test_unsafe_relation_promotions_fail(mutation):
    edges = json.loads(EDGES.read_text(encoding="utf-8"))
    snapshot = json.loads(INVENTORY.read_text(encoding="utf-8"))
    mutation(edges)
    with pytest.raises(AssertionError):
        validate(edges, snapshot)
