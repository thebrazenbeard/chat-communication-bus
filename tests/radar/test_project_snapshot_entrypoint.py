from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


def test_snapshot_entrypoint_uses_read_only_gh_and_emits_deterministic_json(tmp_path):
    root = Path(__file__).resolve().parents[2]
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    log = tmp_path / "gh.log"
    gh = fake_bin / "gh"
    gh.write_text(
        """#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
with open(os.environ["FAKE_GH_LOG"], "a", encoding="utf-8") as fh:
    fh.write(json.dumps(args) + "\\n")
if args[:2] == ["project", "view"]:
    print(json.dumps({"id":"PVT_test","number":10,"title":"Radar's Chat Bus Fix"}))
elif args[:2] == ["project", "field-list"]:
    print(json.dumps({"totalCount":1,"fields":[{"id":"PVTSSF_status","name":"Status","type":"ProjectV2SingleSelectField","options":[{"id":"a","name":"Backlog"},{"id":"b","name":"Ready"},{"id":"c","name":"In progress"},{"id":"d","name":"In review"},{"id":"e","name":"Done"}]}]}))
elif args[:2] == ["project", "item-list"]:
    print(json.dumps({"totalCount":1,"items":[{"id":"PVTI_69","status":"Backlog","content":{"type":"Issue","number":69,"title":"Writer race","repository":"thebrazenbeard/chat-communication-bus","url":"https://github.com/thebrazenbeard/chat-communication-bus/issues/69"}}]}))
else:
    print("unexpected", file=sys.stderr)
    sys.exit(3)
""",
        encoding="utf-8",
    )
    gh.chmod(0o755)

    env = dict(os.environ)
    env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH','')}"
    env["FAKE_GH_LOG"] = str(log)

    completed = subprocess.run(
        [sys.executable, str(root / "scripts" / "radar_project_snapshot.py")],
        cwd=root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    snapshot = json.loads(completed.stdout)
    assert snapshot["authority"] == "QUEUE_METADATA_ONLY"
    assert snapshot["mutation_supported"] is False
    assert snapshot["items"][0]["content_key"] == "thebrazenbeard/chat-communication-bus#69"

    calls = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]
    assert [call[:2] for call in calls] == [
        ["project", "view"],
        ["project", "field-list"],
        ["project", "item-list"],
    ]
    flat = " ".join(" ".join(call) for call in calls).lower()
    assert "item-edit" not in flat
    assert "memex" not in flat


def test_snapshot_entrypoint_fails_bounded_when_gh_is_missing(tmp_path):
    root = Path(__file__).resolve().parents[2]
    env = dict(os.environ)
    env["PATH"] = str(tmp_path)
    completed = subprocess.run(
        [sys.executable, str(root / "scripts" / "radar_project_snapshot.py")],
        cwd=root,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    assert completed.returncode == 1
    assert completed.stdout == ""
    assert "GH_CLI_UNAVAILABLE" in completed.stderr
