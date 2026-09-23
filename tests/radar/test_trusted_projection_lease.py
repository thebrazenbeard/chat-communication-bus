from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "radar_trusted_project.py"
WORKFLOW = ROOT / ".github" / "workflows" / "radar-trusted-projector.yml"


def test_projection_claim_lease_exceeds_trusted_job_timeout() -> None:
    script = SCRIPT.read_text(encoding="utf-8")
    workflow = WORKFLOW.read_text(encoding="utf-8")

    lease = re.search(r"CLAIM_LEASE_SECONDS\s*=\s*(\d+)\s*\*\s*(\d+)", script)
    timeout = re.search(r"timeout-minutes:\s*(\d+)", workflow)
    assert lease and timeout

    lease_seconds = int(lease.group(1)) * int(lease.group(2))
    workflow_seconds = int(timeout.group(1)) * 60
    assert lease_seconds > workflow_seconds
    assert "lease_seconds=CLAIM_LEASE_SECONDS" in script
