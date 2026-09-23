from __future__ import annotations

from pathlib import Path
import subprocess

from radar.trusted_reconciler import LocalGitRepository


ROOT = Path(__file__).resolve().parents[2]
CHECKOUT_SHA = "3d3c42e5aac5ba805825da76410c181273ba90b1"


def _git(repo, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def test_remote_tracking_writer_ref_is_read_without_local_branch_materialization(tmp_path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "radar@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "Radar Test"], check=True)

    (repo / "README.md").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", "README.md"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)
    head = _git(repo, "rev-parse", "HEAD")

    subprocess.run(
        ["git", "-C", str(repo), "update-ref", "refs/remotes/origin/bus/yin-v2", head],
        check=True,
    )

    adapter = LocalGitRepository(repo, use_remote_tracking_refs=True)
    assert adapter.branch_head("bus/yin-v2") == head
    assert subprocess.run(
        ["git", "-C", str(repo), "show-ref", "--verify", "--quiet", "refs/heads/bus/yin-v2"],
        check=False,
    ).returncode != 0


def _assert_ref_read_only_script(path: str) -> None:
    script = (ROOT / path).read_text(encoding="utf-8")
    assert "materialize_inert_remote_bus_refs" not in script
    assert "use_remote_tracking_refs=True" in script


def test_validate_only_cli_reads_remote_refs_without_materializing_local_writer_branches() -> None:
    _assert_ref_read_only_script("scripts/radar_trusted_reconcile.py")


def test_provider_projector_reads_remote_refs_without_materializing_local_writer_branches() -> None:
    _assert_ref_read_only_script("scripts/radar_trusted_project.py")


def test_trusted_wakeup_exposes_no_local_writer_ref_materialization_primitive() -> None:
    source = (ROOT / "src/radar/trusted_wakeup.py").read_text(encoding="utf-8")
    assert "materialize_inert_remote_bus_refs" not in source
    assert '"update-ref"' not in source
    assert "refs/heads/" not in source


def test_trusted_projector_fetches_all_canonical_remote_branch_refs_for_read_only_observation() -> None:
    workflow = (ROOT / ".github/workflows/radar-trusted-projector.yml").read_text(encoding="utf-8")
    start = workflow.index("- name: Check out current canonical main as inert Git data")
    end = workflow.index("- name: Set up Python", start)
    canonical_checkout = workflow[start:end]

    assert f"uses: actions/checkout@{CHECKOUT_SHA}" in canonical_checkout
    assert "ref: main" in canonical_checkout
    assert "path: canonical" in canonical_checkout
    assert "fetch-depth: 0" in canonical_checkout
    assert "persist-credentials: false" in canonical_checkout
