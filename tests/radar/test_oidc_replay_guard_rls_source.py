from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "supabase" / "migrations"
ORIGINAL = BASE / "20260905230823_radar_oidc_replay_guard_v1.sql"
HARDENING = BASE / "20260922171230_radar_oidc_replay_guard_rls_v1.sql"


def normalized(path: Path) -> str:
    return path.read_text(encoding="utf-8").lower()


def test_original_replay_guard_remains_service_role_only():
    sql = normalized(ORIGINAL)
    assert "revoke all on table radar.github_oidc_replay_guard from public" in sql
    assert "revoke all on table radar.github_oidc_replay_guard from anon" in sql
    assert "revoke all on table radar.github_oidc_replay_guard from authenticated" in sql
    assert "security definer" in sql
    assert (
        "grant execute on function radar.consume_github_oidc_jti_v1"
        "(text,timestamptz) to service_role"
    ) in sql


def test_hardening_enables_rls_without_adding_permissive_policy():
    sql = normalized(HARDENING)
    assert "alter table radar.github_oidc_replay_guard enable row level security" in sql
    assert (
        "alter table radar.github_oidc_replay_guard force row level security"
        not in sql
    )
    assert "create policy" not in sql
    assert "grant select on" not in sql
    assert "grant insert on" not in sql
    assert "grant update on" not in sql
    assert "grant delete on" not in sql


def test_hardening_reasserts_client_revocations_and_rpc_boundary():
    sql = normalized(HARDENING)
    for role in ("public", "anon", "authenticated"):
        assert f"revoke all on table radar.github_oidc_replay_guard from {role}" in sql
        assert (
            "revoke all on function radar.consume_github_oidc_jti_v1"
            f"(text,timestamptz) from {role}"
        ) in sql
        assert (
            "revoke all on function public.radar_consume_github_oidc_jti_v1"
            f"(text,timestamptz) from {role}"
        ) in sql

    assert (
        "grant execute on function radar.consume_github_oidc_jti_v1"
        "(text,timestamptz) to service_role"
    ) in sql
    assert (
        "grant execute on function public.radar_consume_github_oidc_jti_v1"
        "(text,timestamptz) to service_role"
    ) in sql
