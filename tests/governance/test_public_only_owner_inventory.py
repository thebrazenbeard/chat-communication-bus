"""Source-only public owner inventory schema and disclosure guard.

Offline tests cannot establish current GitHub visibility; exact live membership,
branch ancestry, and historic exposure still require independent review.
"""

import copy
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
INVENTORY = ROOT / "portfolio" / "PUBLIC_ONLY_OWNER_INVENTORY_V1.json"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
REPO = re.compile(r"^thebrazenbeard/[A-Za-z0-9_.-]+$")
ALLOWED = {
    "schema", "event_id", "evidence_class", "observed_at_utc",
    "source", "authority", "coverage", "public_repositories", "limitations",
}
ROW_KEYS = {"repository_full_name", "default_branch", "head_sha", "archived", "visibility"}
COUNT_KEYS = {
    "total_repositories", "active_repositories", "archived_repositories",
    "public_repositories", "public_active_repositories",
    "public_archived_repositories", "private_aggregate",
}
PRIVATE_AGG_KEYS = {"repositories", "active", "archived"}


def validate(payload):
    assert isinstance(payload, dict) and set(payload) == ALLOWED
    assert payload["schema"] == "CCB_PUBLIC_ONLY_OWNER_INVENTORY_V1"
    assert payload["event_id"] == "project_unfuck_runtime_coordination"
    assert payload["evidence_class"] == "VERIFIED_LIVE_GITHUB_METADATA_SNAPSHOT"
    assert payload["authority"] == "SOURCE_ONLY_NOT_RUNTIME_OR_DEPLOYMENT"
    assert re.fullmatch(r"20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z", payload["observed_at_utc"])

    c = payload["coverage"]
    assert isinstance(c, dict) and set(c) == COUNT_KEYS
    p = c["private_aggregate"]
    assert isinstance(p, dict) and set(p) == PRIVATE_AGG_KEYS
    for k, v in c.items():
        if k == "private_aggregate":
            continue
        assert type(v) is int and v >= 0
    for value in p.values():
        assert type(value) is int and value >= 0
    assert c["total_repositories"] == c["public_repositories"] + p["repositories"]
    assert c["active_repositories"] + c["archived_repositories"] == c["total_repositories"]
    assert c["public_active_repositories"] + c["public_archived_repositories"] == c["public_repositories"]
    assert p["active"] + p["archived"] == p["repositories"]
    assert c["active_repositories"] == c["public_active_repositories"] + p["active"]
    assert c["archived_repositories"] == c["public_archived_repositories"] + p["archived"]

    rows = payload["public_repositories"]
    assert isinstance(rows, list) and len(rows) == c["public_repositories"]
    names = []
    for row in rows:
        assert isinstance(row, dict) and set(row) == ROW_KEYS
        assert row["visibility"] == "public"
        assert type(row["archived"]) is bool
        assert isinstance(row["repository_full_name"], str) and REPO.fullmatch(row["repository_full_name"])
        assert isinstance(row["default_branch"], str) and row["default_branch"].strip()
        assert isinstance(row["head_sha"], str) and SHA40.fullmatch(row["head_sha"])
        names.append(row["repository_full_name"])
    assert names == sorted(names, key=str.casefold)
    assert len(set(names)) == len(names)
    assert sum(row["archived"] for row in rows) == c["public_archived_repositories"]


def test_snapshot_is_public_only_and_count_consistent():
    data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    validate(data)
    assert data["coverage"]["total_repositories"] == 107
    assert data["coverage"]["public_repositories"] == 89
    assert data["coverage"]["private_aggregate"]["repositories"] == 18


@pytest.mark.parametrize(
    "corrupt",
    [
        lambda x: x["public_repositories"][0].update(visibility="private"),
        lambda x: x["public_repositories"][0].update(private_source_path="secret"),
        lambda x: x.update(private_repositories=["do-not-publish"]),
        lambda x: x["coverage"].update(private_aggregate={"repositories": 18, "active": 14, "archived": 4, "names": ["do-not-publish"]}),
        lambda x: x["public_repositories"][0].update(head_sha="not-a-git-sha"),
        lambda x: x["public_repositories"].append(copy.deepcopy(x["public_repositories"][0])),
        lambda x: x["coverage"].update(total_repositories=108),
    ],
)
def test_private_disclosure_or_integrity_mutations_fail(corrupt):
    data = json.loads(INVENTORY.read_text(encoding="utf-8"))
    corrupt(data)
    with pytest.raises(AssertionError):
        validate(data)
