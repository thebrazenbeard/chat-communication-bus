from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[2]


def test_provider_readback_declares_stable_supabase_py_optional_dependency():
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    deps = data["project"]["optional-dependencies"]["provider-readback"]
    assert deps == ["supabase==2.31.0"]


def test_provider_architecture_keeps_write_readback_and_management_separate():
    text = (ROOT / "architecture/contracts/RADAR_SUPABASE_V1.md").read_text(
        encoding="utf-8"
    )
    assert "supabase-py" in text
    assert "independent read-only data-plane readback" in text
    assert "does not replace provider management" in text
    assert "does not replace GitHub OIDC ingress" in text
    assert "verify_jwt = false" in text
