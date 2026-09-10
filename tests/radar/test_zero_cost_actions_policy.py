from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"


def test_source_ci_does_not_duplicate_radar_branch_push_and_pr_runs():
    ci = (WORKFLOWS / "ci.yml").read_text(encoding="utf-8")
    assert '      - "main"' in ci
    assert "pull_request:" in ci
    assert '      - "radar/**"' not in ci
    assert "concurrency:" in ci
    assert "cancel-in-progress: ${{ github.event_name == 'pull_request' }}" in ci
    assert "cancel-in-progress: true" not in ci


def test_single_automatic_writer_validator_observes_every_bus_push():
    guard = (WORKFLOWS / "writer-lane-guard.yml").read_text(encoding="utf-8")
    projection = (WORKFLOWS / "radar-bus-projection.yml").read_text(encoding="utf-8")
    trusted = (WORKFLOWS / "radar-trusted-projector.yml").read_text(encoding="utf-8")

    assert "workflow_dispatch:" in guard
    assert '      - "bus/**"' not in guard
    assert '      - "bus/**"' in projection
    assert "paths:" not in projection
    assert "radar-trusted-projector.yml@" in projection
    assert "scripts/radar_emit_bus_projection.py" in trusted
    assert "--base" in trusted
    assert "--cutover" in trusted
    assert "--bootstrap-main" in trusted


def test_manual_writer_guard_requires_explicit_range_base():
    guard = (WORKFLOWS / "writer-lane-guard.yml").read_text(encoding="utf-8")
    assert "base_sha:" in guard
    assert "required: true" in guard
    assert "RADAR_BASE: ${{ inputs.base_sha }}" in guard
    assert "rev-parse \"${RADAR_HEAD}^\"" not in guard


def test_zero_cost_policy_keeps_hosted_workflows_read_only_except_oidc_projection():
    guard = (WORKFLOWS / "writer-lane-guard.yml").read_text(encoding="utf-8").lower()
    ci = (WORKFLOWS / "ci.yml").read_text(encoding="utf-8").lower()
    projection = (WORKFLOWS / "radar-bus-projection.yml").read_text(encoding="utf-8").lower()

    assert "contents: write" not in guard
    assert "contents: write" not in ci
    assert "contents: write" not in projection
    assert "contents: read" in guard
    assert "contents: read" in ci
    assert "contents: read" in projection
    assert "id-token: write" in projection
