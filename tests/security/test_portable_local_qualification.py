from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
ENGINE_PATH = ROOT / "scripts/radar_qualify.py"
REQUIRED = ["one", "two"]


def _load_engine():
    spec = importlib.util.spec_from_file_location("radar_qualify", ENGINE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init")
    _git(repo, "config", "user.name", "Radar Test")
    _git(repo, "config", "user.email", "radar-test@example.invalid")
    (repo / "payload.txt").write_text("candidate\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "candidate")
    return repo


def test_run_stage_hashes_exact_output_and_assigns_identity(tmp_path: Path) -> None:
    engine = _load_engine()
    calls: list[tuple[list[str], Path]] = []
    times = iter(
        [
            datetime(2026, 9, 8, 1, 0, 0, tzinfo=timezone.utc),
            datetime(2026, 9, 8, 1, 0, 1, tzinfo=timezone.utc),
        ]
    )

    def runner(command: list[str], cwd: Path) -> object:
        calls.append((command, cwd))
        return engine.CommandResult(
            returncode=0,
            stdout=b"hello\n",
            stderr=b"warning\n",
            executable="python 3.11",
        )

    evidence = engine.run_stage(
        ordinal=3,
        stage_id="python_pytest:3.11",
        command=["python", "-m", "pytest", "-q"],
        cwd=tmp_path,
        runner=runner,
        now=lambda: next(times),
    )

    assert calls == [(["python", "-m", "pytest", "-q"], tmp_path)]
    assert evidence.ordinal == 3
    assert evidence.stage_id == "python_pytest:3.11"
    assert evidence.exit_code == 0
    assert evidence.executable == "python 3.11"
    assert evidence.stdout_sha256 == hashlib.sha256(b"hello\n").hexdigest()
    assert evidence.stderr_sha256 == hashlib.sha256(b"warning\n").hexdigest()
    assert evidence.started_at_utc == "2026-09-08T01:00:00+00:00"
    assert evidence.completed_at_utc == "2026-09-08T01:00:01+00:00"


def test_run_stage_failure_exposes_terminal_evidence(tmp_path: Path) -> None:
    engine = _load_engine()
    times = iter(
        [
            datetime(2026, 9, 8, 1, 0, 0, tzinfo=timezone.utc),
            datetime(2026, 9, 8, 1, 0, 1, tzinfo=timezone.utc),
        ]
    )

    def runner(command: list[str], cwd: Path) -> object:
        return engine.CommandResult(
            returncode=7,
            stdout=b"partial\n",
            stderr=b"failed\n",
            executable=command[0],
        )

    with pytest.raises(engine.QualificationError) as caught:
        engine.run_stage(
            ordinal=1,
            stage_id="one",
            command=["fake"],
            cwd=tmp_path,
            runner=runner,
            now=lambda: next(times),
        )

    evidence = caught.value.evidence
    assert evidence.stage_id == "one"
    assert evidence.exit_code == 7
    assert evidence.stdout_sha256 == hashlib.sha256(b"partial\n").hexdigest()
    assert evidence.stderr_sha256 == hashlib.sha256(b"failed\n").hexdigest()


def test_canonical_stage_digest_is_stable_and_exact() -> None:
    engine = _load_engine()
    stage = engine.StageEvidence(
        ordinal=1,
        stage_id="one",
        started_at_utc="2026-09-08T01:00:00+00:00",
        completed_at_utc="2026-09-08T01:00:01+00:00",
        exit_code=0,
        executable="fixture",
        stdout_sha256="1" * 64,
        stderr_sha256="2" * 64,
    )
    payload = [stage.to_dict()]
    expected_bytes = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")

    assert engine.canonical_stage_digest([stage]) == hashlib.sha256(expected_bytes).hexdigest()
    assert engine.canonical_stage_digest([stage]) == engine.canonical_stage_digest([stage])


def test_build_pass_receipt_requires_exact_stage_sequence() -> None:
    engine = _load_engine()
    stage = engine.StageEvidence(
        ordinal=1,
        stage_id="wrong",
        started_at_utc="2026-09-08T01:00:00+00:00",
        completed_at_utc="2026-09-08T01:00:01+00:00",
        exit_code=0,
        executable="fixture",
        stdout_sha256="1" * 64,
        stderr_sha256="2" * 64,
    )

    with pytest.raises(engine.QualificationError, match="stage sequence"):
        engine.build_pass_receipt(
            source_commit="a" * 40,
            source_tree="b" * 40,
            qualification_mode="LOCAL_NO_PAID_SERVICES",
            toolchain={"python": ["3.11", "3.12"]},
            stages=[stage],
            required_stage_instances=REQUIRED,
            completed_at=datetime(2026, 9, 8, 1, 2, 0, tzinfo=timezone.utc),
        )


def test_build_pass_receipt_emits_schema_v2_and_digest() -> None:
    engine = _load_engine()
    stages = [
        engine.StageEvidence(
            ordinal=index,
            stage_id=stage_id,
            started_at_utc=f"2026-09-08T01:00:0{(index - 1) * 2}+00:00",
            completed_at_utc=f"2026-09-08T01:00:0{(index - 1) * 2 + 1}+00:00",
            exit_code=0,
            executable="fixture",
            stdout_sha256="1" * 64,
            stderr_sha256="2" * 64,
        )
        for index, stage_id in enumerate(REQUIRED, 1)
    ]

    receipt = engine.build_pass_receipt(
        source_commit="a" * 40,
        source_tree="b" * 40,
        qualification_mode="LOCAL_NO_PAID_SERVICES",
        toolchain={"python": ["3.11", "3.12"]},
        stages=stages,
        required_stage_instances=REQUIRED,
        completed_at=datetime(2026, 9, 8, 1, 2, 0, tzinfo=timezone.utc),
    )

    assert receipt["schema_version"] == 2
    assert receipt["status"] == "PASS"
    assert receipt["working_tree"] == "CLEAN"
    assert receipt["stages"] == [stage.to_dict() for stage in stages]
    assert receipt["stage_evidence_sha256"] == engine.canonical_stage_digest(stages)


def test_external_receipt_guard_rejects_nested_and_allows_outside(tmp_path: Path) -> None:
    engine = _load_engine()
    repo = tmp_path / "repo"
    repo.mkdir()

    with pytest.raises(engine.QualificationError, match="outside source checkout"):
        engine.ensure_external_receipt_path(repo / "ignored" / "receipt.json", repo)

    outside = tmp_path / "receipt.json"
    assert engine.ensure_external_receipt_path(outside, repo) == outside.resolve()


def test_clean_source_state_binds_exact_commit_tree_and_rejects_dirty(tmp_path: Path) -> None:
    engine = _load_engine()
    repo = _init_repo(tmp_path)

    state = engine.read_clean_source_state(repo)
    assert state.commit == _git(repo, "rev-parse", "HEAD")
    assert state.tree == _git(repo, "rev-parse", "HEAD^{tree}")

    (repo / "payload.txt").write_text("dirty\n", encoding="utf-8")
    with pytest.raises(engine.QualificationError, match="working tree"):
        engine.read_clean_source_state(repo)
