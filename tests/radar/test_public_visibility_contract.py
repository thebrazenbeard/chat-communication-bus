"""Source-only public visibility transition regression checks; no provider effects."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
README = ROOT / "README.md"
SECURITY = ROOT / "SECURITY.md"
DOC = ROOT / "docs" / "PUBLIC_TRANSITION_2026-10-29.md"
DISPATCHER = ROOT / ".github" / "workflows" / "radar-central-dispatcher.yml"


def assert_manual_only_dispatcher_events(source: str) -> None:
    """Conservative source guard for this held GitHub Actions entrypoint.

    Reject unfamiliar YAML forms instead of guessing whether they might
    implicitly enable an event. Only the current, exact top-level key layout
    is admitted; spelled aliases, YAML tags, and duplicate keys fail closed.
    """
    lines = source.splitlines()
    top_level = []
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#") or line[0].isspace():
            continue
        if line.startswith("name: "):
            top_level.append("name")
        elif line in {"on:", "permissions:", "jobs:"}:
            top_level.append(line[:-1])
        else:
            raise ValueError("PUBLIC_DISPATCHER_NOT_MANUAL_ONLY")
    if top_level != ["name", "on", "permissions", "jobs"]:
        raise ValueError("PUBLIC_DISPATCHER_NOT_MANUAL_ONLY")

    events = []
    for line in lines[lines.index("on:") + 1:]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line[0].isspace():
            break
        # Exactly two-space event keys; nested event options are allowed.
        if line.startswith("  ") and not line.startswith("   "):
            events.append(line[2:].strip())
        elif line.startswith("\t") or line.startswith(" ") and not line.startswith("  "):
            raise ValueError("PUBLIC_DISPATCHER_NOT_MANUAL_ONLY")
    if events != ["workflow_dispatch:"]:
        raise ValueError("PUBLIC_DISPATCHER_NOT_MANUAL_ONLY")


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
    assert_manual_only_dispatcher_events(text)
    assert "id-token: write" in text  # explicit manually-triggered authority, not silent
    assert "radar-trusted-projector.yml@dfd3c639d058dcafaa1167e53ad4bdc152d52cf6" in text


@pytest.mark.parametrize("event", [
    "push", "issues", "repository_dispatch", "workflow_run", "schedule", "pull_request"
])
def test_public_dispatcher_rejects_every_synthetic_automatic_event(event):
    source = DISPATCHER.read_text(encoding="utf-8")
    mutant = source.replace("  workflow_dispatch:\n", f"  workflow_dispatch:\n  {event}:\n", 1)
    with pytest.raises(ValueError, match="PUBLIC_DISPATCHER_NOT_MANUAL_ONLY"):
        assert_manual_only_dispatcher_events(mutant)


def test_public_dispatcher_rejects_inline_trigger_or_duplicate_on():
    source = DISPATCHER.read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="PUBLIC_DISPATCHER_NOT_MANUAL_ONLY"):
        assert_manual_only_dispatcher_events(source.replace("on:\n  workflow_dispatch:", "on: [workflow_dispatch, push]", 1))
    with pytest.raises(ValueError, match="PUBLIC_DISPATCHER_NOT_MANUAL_ONLY"):
        assert_manual_only_dispatcher_events(source + "\non:\n  push:\n")


@pytest.mark.parametrize("extra_key", ['"o\\u006e"', "!!str on"])
def test_public_dispatcher_rejects_semantic_on_key_aliases(extra_key):
    """YAML-equivalent `on` spellings must not bypass duplicate-key checks."""
    source = DISPATCHER.read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="PUBLIC_DISPATCHER_NOT_MANUAL_ONLY"):
        assert_manual_only_dispatcher_events(source + f"\n{extra_key}:\n  push:\n")
