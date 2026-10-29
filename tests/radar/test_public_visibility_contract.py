"""Source-only public visibility transition regression checks; no provider effects."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
SECURITY = ROOT / "SECURITY.md"
DOC = ROOT / "docs" / "PUBLIC_TRANSITION_2026-10-29.md"
DISPATCHER = ROOT / ".github" / "workflows" / "radar-central-dispatcher.yml"


def test_readme_does_not_claim_confidential_branch_vault():
    text = README.read_text(encoding="utf-8")
    assert "Visibility changed to PUBLIC" in text
    assert "This private repository is" not in text
    assert "Do not append private mailbox messages" in text
    assert "273c93bc46683580024c1521fd2c523a8a6593bd" in text


def test_public_security_disclosure_contract_exists():
    assert SECURITY.is_file()
    content = SECURITY.read_text(encoding="utf-8")
    assert "already public exposure" in content
    assert "Do not post credentials" in content
    assert DOC.is_file()
    assert "does not revoke Git objects" not in content or "cannot" in content


def test_automatic_radar_projector_triggers_remain_disabled():
    text = DISPATCHER.read_text(encoding="utf-8")
    # Parse only the top-level trigger block, not comments or the called action.
    start = text.index("\non:\n")
    end = text.index("\npermissions:", start)
    trigger = text[start:end]
    assert "workflow_dispatch:" in trigger
    assert "workflow_run:" not in trigger
    assert "schedule:" not in trigger
    assert "id-token: write" in text  # explicit manually-triggered authority, not silent
    assert "radar-trusted-projector.yml@dfd3c639d058dcafaa1167e53ad4bdc152d52cf6" in text
