from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "selfimage-blender-relay.yml"


def test_persistent_blender_relay_never_receives_repository_write_authority():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "publish_receipts:" not in workflow
    assert "contents: write" not in workflow
    assert "github.token" not in workflow
    assert "git push" not in workflow
    assert "Repository publication is intentionally disabled until a separately trusted publisher boundary exists." in workflow
    assert "Upload durable receipts for isolated publication" in workflow
