"""Executable source-level Mono/PORTAL stale advisory falsifier.

Not a Project Runner claim/fence or live host route. Invoke with exact independent
Mono#77 and selected PORTAL#51 source checkouts; ephemeral SQLite only.
  python probe_real_mono_portal_stale_advisory.py <mono-root> <portal-root>
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from probe_real_mono_portal_noeffect import MONO_HEAD, PORTAL_HEAD, head


def check(mono: Path, portal: Path) -> dict:
    mono, portal = mono.resolve(strict=True), portal.resolve(strict=True)
    if head(mono) != MONO_HEAD or head(portal) != PORTAL_HEAD:
        raise RuntimeError("source head mismatch; no implicit rebind")
    roots = [str(p) for p in sorted((mono / "packages").glob("*/src"))]
    if not roots or not (portal / "portal/vera_task_handoff.py").is_file():
        raise RuntimeError("canonical source roots missing")
    roots.insert(0, str(portal))
    sys.path[:0] = roots

    from vera_core import QualifiedVeraRuntime, VeraStateDirectory
    from vera_core.local_conversation import open_message
    from vera_core.portal_task_handoff import (
        export_portal_route_request, verify_portal_route_assessment)
    from vera_core.task_execution import TaskExecutionError
    from portal.vera_task_handoff import assess_vera_task_route

    with tempfile.TemporaryDirectory(prefix="portal-stale-advisory-") as td:
        state_root = Path(td) / "canonical"
        s = VeraStateDirectory(state_root, project_id="VERA_MONO",
                               identity_id="VERA_PROJECT_IDENTITY_V1")
        rt = QualifiedVeraRuntime.from_state_directory(s)
        ledger = rt.tasks
        intake = open_message(ledger, "stale-source-review", "message-1",
                              "Read-only advisory must bind a current task head")
        first = export_portal_route_request(
            ledger, intake["task_id"], node_id="github-api",
            target_kind="repository", target_id="thebrazenbeard/portal",
            required_capabilities=("source_read",))
        initial = assess_vera_task_route(first, ())
        assert verify_portal_route_assessment(ledger, first, initial) == initial
        assert initial["state"] == "HELD" and initial["route"] is None

        ledger.checkpoint(
            intake["task_id"], "test-only-source-head-advance",
            completed_evidence=("TEST_ONLY: task advanced without execution",),
            blockers=("no authenticated provider or host effect",),
            protected_effects_still_gated=("COGNITION_TURN",),
            next_frontier="fresh advisory requires new canonical head",
            lifecycle_evidence_digest=intake["source_digest"],
            expected_task_head=intake["opened_head"],
        )
        assert len(ledger.events(intake["task_id"])) == 2
        assert not ledger.read(intake["task_id"]).closed
        try:
            verify_portal_route_assessment(ledger, first, initial)
        except TaskExecutionError:
            pass
        else:
            raise AssertionError("STALE_ADVISORY_ACCEPTED after real checkpoint")

        fresh = export_portal_route_request(
            ledger, intake["task_id"], node_id="github-api",
            target_kind="repository", target_id="thebrazenbeard/portal",
            required_capabilities=("source_read",))
        assert fresh["task_journal_head"] != first["task_journal_head"]
        latest = assess_vera_task_route(fresh, ())
        assert verify_portal_route_assessment(ledger, fresh, latest) == latest
        assert latest["state"] == "HELD" and latest["route"] is None

        # Fresh Python OS process reopens SAME disposable canonical ledger.
        child = (
            "import json,sys;"
            "from vera_core import QualifiedVeraRuntime,VeraStateDirectory;"
            "from vera_core.task_execution import TaskExecutionError;"
            "from vera_core.portal_task_handoff import verify_portal_route_assessment;"
            "s=VeraStateDirectory(sys.argv[1],project_id='VERA_MONO',"
            "identity_id='VERA_PROJECT_IDENTITY_V1');"
            "r=QualifiedVeraRuntime.from_state_directory(s);"
            "q=json.loads(sys.argv[2]);a=json.loads(sys.argv[3]);"
            "success=False\n"
            "try:\n verify_portal_route_assessment(r.tasks,q,a)\n"
            "except TaskExecutionError:\n success=True\n"
            "print(json.dumps({'stale_rejected':success,"
            "'count':len(r.tasks.events(q['task_id'])),"
            "'closed':r.tasks.read(q['task_id']).closed}))"
        )
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
               "PYTHONPATH": os.pathsep.join(roots)}
        proc = subprocess.run(
            [sys.executable, "-c", child, str(state_root),
             json.dumps(first), json.dumps(initial)],
            capture_output=True, text=True, env=env, timeout=25)
        if proc.returncode:
            raise RuntimeError("cold process failed: " + proc.stderr[-1200:])
        cold = json.loads(proc.stdout)
        assert cold == {"stale_rejected": True, "count": 2, "closed": False}
        assert len(ledger.events(intake["task_id"])) == 2
        return {
            "schema": "PORTAL_MONO_STALE_ADVISORY_FENCE_SOURCE_PROBE_V1",
            "source_heads": {"mono": MONO_HEAD, "portal": PORTAL_HEAD},
            "initial_advisory": "HELD",
            "task_head_advanced_by_test_only_checkpoint": True,
            "stale_assessment_rejected": True,
            "independent_cold_process_stale_assessment_rejected": True,
            "fresh_head_advisory": "HELD",
            "task_events": 2, "task_closed": False,
            "real_runner_claim_observed": False,
            "provider_calls": 0, "host_dispatch": "NOT_INVOKED",
            "effect": "NO_EFFECT",
            "evidence_ceiling": "SOURCE_ONLY_NOT_SELECTED_HOST_OR_GUEST",
        }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: probe_real_mono_portal_stale_advisory.py MONO PORTAL")
    print(json.dumps(check(Path(sys.argv[1]), Path(sys.argv[2])),
                     sort_keys=True, indent=2))
