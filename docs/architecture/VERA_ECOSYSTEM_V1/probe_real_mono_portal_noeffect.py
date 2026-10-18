"""Execute the pinned Mono TASK_OPENED -> PORTAL advisory HELD seam, with zero routes.

This is a real cross-repository Python/SQLite source test on disposable state.
It DOES NOT inspect a live Project Runner lease or qualify a host effect.
Usage:
  python probe_real_mono_portal_noeffect.py <vera-mono-checkout> <portal-checkout>
The input repositories MUST be independent exact-head checkouts of the pinned
source. Nothing is installed or deployed; no provider, scheduler or model runs.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

MONO_HEAD = "89ba1d18da78e7e38f015cf8d8ef4f528aae9df8"
PORTAL_HEAD = "36fa04da4e5eb383fecf463c72a43b94ca47d7e5"


def head(path: Path) -> str:
    return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"],
                                   text=True, timeout=10).strip()


def main(mono: Path, portal: Path) -> dict:
    mono, portal = mono.resolve(strict=True), portal.resolve(strict=True)
    if head(mono) != MONO_HEAD or head(portal) != PORTAL_HEAD:
        raise RuntimeError("immutable source pin mismatch; no implicit rebind")
    roots = [str(p) for p in sorted((mono / "packages").glob("*/src"))]
    if not roots or not (portal / "portal/vera_task_handoff.py").is_file():
        raise RuntimeError("selected source roots unavailable")
    roots.insert(0, str(portal))
    sys.path[:0] = roots
    from vera_core import QualifiedVeraRuntime, VeraStateDirectory
    from vera_core.local_conversation import open_message, ConversationError
    from vera_core.portal_task_handoff import (
        export_portal_route_request, verify_portal_route_assessment,
    )
    from portal.vera_task_handoff import assess_vera_task_route
    from vera_core.task_execution import TaskExecutionError

    with tempfile.TemporaryDirectory(prefix="portal-mono-noeffect-") as td:
        root = Path(td) / "isolated-vera"
        state = VeraStateDirectory(root, project_id="VERA_MONO",
                                   identity_id="VERA_PROJECT_IDENTITY_V1")
        runtime = QualifiedVeraRuntime.from_state_directory(state)
        ledger = runtime.tasks
        text = "Exact canonical message, not a dispatch request."
        intake = open_message(ledger, "source-only-session", "literal-1", text)
        assert intake["origin_authenticated"] is False
        assert open_message(ledger, "source-only-session", "literal-1", text)["task_id"] == intake["task_id"]
        assert len(ledger.events(intake["task_id"])) == 1
        try:
            open_message(ledger, "source-only-session", "literal-1", "Substituted text")
        except ConversationError:
            pass
        else:
            raise AssertionError("substituted literal escaped task identity")

        request = export_portal_route_request(
            ledger, intake["task_id"], node_id="github-api",
            target_kind="repository", target_id="thebrazenbeard/portal",
            required_capabilities=("source_read",),
        )
        assert request["requested_effect"] == "NO_PROTECTED_EFFECT"
        assert request["task_journal_head"] == intake["opened_head"]
        assessment = assess_vera_task_route(request, ())
        assert assessment["state"] == "HELD"
        assert assessment["route"] is None
        assert assessment["reason"] == "NO_QUALIFIED_ADVISORY_ROUTE"
        assert verify_portal_route_assessment(ledger, request, assessment) == assessment

        forged = copy.deepcopy(request)
        forged["subject"] = "different subject"
        try:
            assess_vera_task_route(forged, ())
        except ValueError:
            pass
        else:
            raise AssertionError("tampered task request passed digest check")

        forged_reply = copy.deepcopy(assessment)
        forged_reply["state"] = "ROUTE_PROPOSED"
        forged_reply["route"] = {"adapter_id": "fake", "route_id": "fake"}
        forged_reply["reason"] = None
        try:
            verify_portal_route_assessment(ledger, request, forged_reply)
        except TaskExecutionError:
            pass
        else:
            raise AssertionError("forged route assessment passed digest check")

        assert len(ledger.events(intake["task_id"])) == 1
        assert not ledger.read(intake["task_id"]).closed

        # A *new operating-system process*, not a re-import in the same interpreter.
        cold_program = (
            "import json,sys;"
            "from vera_core import VeraStateDirectory,QualifiedVeraRuntime;"
            "from vera_core.local_conversation import open_message;"
            "s=VeraStateDirectory(sys.argv[1],project_id='VERA_MONO',"
            "identity_id='VERA_PROJECT_IDENTITY_V1');"
            "r=QualifiedVeraRuntime.from_state_directory(s);"
            "x=open_message(r.tasks,'source-only-session','literal-1',sys.argv[2]);"
            "print(json.dumps({'task_id':x['task_id'],"
            "'opened_head':x['opened_head'],"
            "'source_digest':x['source_digest'],"
            "'events':len(r.tasks.events(x['task_id'])),"
            "'closed':r.tasks.read(x['task_id']).closed}))"
        )
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1",
               "PYTHONPATH": os.pathsep.join(roots)}
        cold = subprocess.run(
            [sys.executable, "-c", cold_program, str(root), text],
            env=env, capture_output=True, text=True, timeout=25,
        )
        if cold.returncode:
            raise RuntimeError("cold process returned error: " + cold.stderr[-1000:])
        observed = json.loads(cold.stdout)
        assert observed == {
            "task_id": intake["task_id"], "opened_head": intake["opened_head"],
            "source_digest": intake["source_digest"], "events": 1, "closed": False,
        }
        assert len(ledger.events(intake["task_id"])) == 1
        return {
            "schema": "PORTAL_MONO_SOURCE_NOEFFECT_V1",
            "mono_head": MONO_HEAD, "portal_head": PORTAL_HEAD,
            "task_opened": True, "exact_replay": True,
            "substituted_literal_rejected": True,
            "request_source_and_head_bound": True,
            "zero_advisory_routes": True,
            "assessment": "HELD", "route": None,
            "forged_request_and_assessment_rejected": True,
            "independent_cold_process_recovered_same_task": True,
            "canonical_task_events": 1, "task_closed": False,
            "model_invocations": 0, "host_dispatch": "NOT_INVOKED",
            "selected_runner_claim": "NOT_OBSERVED",
            "effect": "NO_EFFECT",
            "evidence_ceiling": "SOURCE_ONLY_NOT_SELECTED_HOST_OR_GUEST",
        }


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: probe_real_mono_portal_noeffect.py MONO_DIR PORTAL_DIR")
    print(json.dumps(main(Path(sys.argv[1]), Path(sys.argv[2])),
                     indent=2, sort_keys=True))
