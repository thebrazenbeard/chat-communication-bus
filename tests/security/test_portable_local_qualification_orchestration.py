from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
ENGINE_PATH = ROOT / "scripts/radar_qualify.py"
REQUIRED_STAGE_INSTANCES = [
    "python_compileall:3.11",
    "python_pytest:3.11",
    "radar_source_hashes:3.11",
    "python_compileall:3.12",
    "python_pytest:3.12",
    "radar_source_hashes:3.12",
    "deno_ci",
    "deno_check",
    "supabase_local_start",
    "supabase_db_reset",
    "all_radar_sql_assertions",
    "supabase_local_stop",
]


def _load_engine():
    spec = importlib.util.spec_from_file_location("radar_qualify_orchestration", ENGINE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _git(repo: Path, *args: str) -> str:
    import subprocess

    result = subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def _init_candidate(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "architecture/contracts").mkdir(parents=True)
    (repo / "supabase/functions/github-bus-ingest").mkdir(parents=True)
    (repo / "supabase/tests").mkdir(parents=True)
    contract = {
        "policy": "NO_PAID_SERVICES",
        "authoritative_qualification": {
            "mode": "LOCAL_NO_PAID_SERVICES",
            "platform": "windows_powershell",
            "receipt_schema_version": 2,
            "required_stage_instances": REQUIRED_STAGE_INSTANCES,
            "required_toolchain": {
                "python": ["3.11", "3.12"],
                "pip": "26.2.1",
                "deno": "2.9.6",
                "supabase_cli": "2.116.0",
                "docker": "required",
                "psql": "required",
            },
        },
    }
    (repo / "architecture/contracts/RADAR_QUALIFICATION_V1.json").write_text(
        json.dumps(contract), encoding="utf-8"
    )
    (repo / "supabase/tests/radar_b.sql").write_text("select 'b';\n", encoding="utf-8")
    (repo / "supabase/tests/radar_a.sql").write_text("select 'a';\n", encoding="utf-8")
    (repo / "supabase/functions/github-bus-ingest/index.ts").write_text("export {};\n", encoding="utf-8")
    (repo / "payload.txt").write_text("candidate\n", encoding="utf-8")
    _git(repo, "init")
    _git(repo, "config", "user.name", "Radar Test")
    _git(repo, "config", "user.email", "radar-test@example.invalid")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "candidate")
    return repo


class Clock:
    def __init__(self) -> None:
        self.current = datetime(2026, 9, 8, 1, 0, 0, tzinfo=timezone.utc)

    def __call__(self) -> datetime:
        value = self.current
        self.current += timedelta(seconds=1)
        return value


class FakeRunner:
    def __init__(self, engine, *, existing_container: bool = False, fail_sql: bool = False, fail_cleanup: bool = False) -> None:
        self.engine = engine
        self.calls: list[tuple[list[str], Path]] = []
        self.existing_container = existing_container
        self.fail_sql = fail_sql
        self.fail_cleanup = fail_cleanup

    def __call__(self, command: list[str], cwd: Path):
        self.calls.append((list(command), cwd))
        joined = " ".join(command)

        if command[:2] == ["py", "-3.11"] and "import sys" in joined:
            return self._result(command, stdout=b"3.11\n")
        if command[:2] == ["py", "-3.12"] and "import sys" in joined:
            return self._result(command, stdout=b"3.12\n")
        if command[:2] == ["deno", "--version"]:
            return self._result(
                command,
                stdout=b"deno 2.9.6 (stable, release, x86_64-pc-windows-msvc)\nv8 fixture\ntypescript fixture\n",
            )
        if command[:2] == ["supabase", "--version"]:
            return self._result(command, stdout=b"2.116.0\n")
        if command[:2] == ["docker", "info"]:
            return self._result(command, stdout=b"docker healthy\n")
        if command[:2] == ["docker", "--version"]:
            return self._result(command, stdout=b"Docker version fixture\n")
        if command[:2] == ["psql", "--version"]:
            return self._result(command, stdout=b"psql (PostgreSQL) fixture\n")
        if command[:2] == ["supabase", "status"]:
            return self._result(command, returncode=1, stderr=b"not running\n")
        if command[:3] == ["docker", "container", "inspect"]:
            return self._result(command, returncode=0 if self.existing_container else 1)
        if command[:3] == ["docker", "volume", "inspect"]:
            return self._result(command, returncode=1)
        if command[:2] == ["docker", "ps"]:
            return self._result(command, stdout=b"")
        if command[:3] == ["docker", "volume", "ls"]:
            return self._result(command, stdout=b"")
        if command[:3] == ["docker", "network", "ls"]:
            return self._result(command, stdout=b"")
        if command[:3] == ["supabase", "stop", "--no-backup"]:
            if self.fail_cleanup:
                return self._result(command, returncode=8, stderr=b"cleanup failed\n")
            return self._result(command, stdout=b"stopped\n")
        if command and command[0] == "psql" and "-f" in command:
            sql_path = Path(command[command.index("-f") + 1])
            if self.fail_sql and sql_path.name == "radar_a.sql":
                return self._result(command, returncode=7, stderr=b"sql failed\n")
            return self._result(command, stdout=f"{sql_path.name}\n".encode())
        if len(command) >= 4 and command[-3:-1] == ["pip", "--version"]:
            return self._result(command, stdout=b"pip 26.2.1 from fixture\n")
        return self._result(command, stdout=b"ok\n")

    def _result(self, command: list[str], *, returncode: int = 0, stdout: bytes = b"", stderr: bytes = b""):
        return self.engine.CommandResult(
            returncode=returncode,
            stdout=stdout,
            stderr=stderr,
            executable=command[0] if command else "",
        )


def test_qualify_emits_exact_stage_sequence_sorted_sql_and_external_receipt(tmp_path: Path) -> None:
    engine = _load_engine()
    repo = _init_candidate(tmp_path)
    receipt_path = tmp_path / "qualification.json"
    runner = FakeRunner(engine)

    receipt = engine.qualify(
        repo_root=repo,
        receipt_path=receipt_path,
        runner=runner,
        now=Clock(),
        temp_parent=tmp_path,
        platform_name="nt",
    )

    assert [stage["stage_id"] for stage in receipt["stages"]] == REQUIRED_STAGE_INSTANCES
    assert receipt_path.exists()
    assert json.loads(receipt_path.read_text(encoding="utf-8")) == receipt

    psql_calls = [command for command, _cwd in runner.calls if command and command[0] == "psql" and "-f" in command]
    assert [Path(command[command.index("-f") + 1]).name for command in psql_calls] == [
        "radar_a.sql",
        "radar_b.sql",
    ]
    assert all("ON_ERROR_STOP=1" in command for command in psql_calls)
    assert any(command[:3] == ["supabase", "stop", "--no-backup"] for command, _cwd in runner.calls)

    venv_commands = [command for command, _cwd in runner.calls if len(command) >= 4 and command[0] == "py" and command[2:4] == ["-m", "venv"]]
    assert len(venv_commands) == 2
    assert venv_commands[0][-1] != venv_commands[1][-1]
    assert any("pip==26.2.1" in command for command, _cwd in runner.calls)


def test_preexisting_supabase_container_blocks_before_start(tmp_path: Path) -> None:
    engine = _load_engine()
    repo = _init_candidate(tmp_path)
    runner = FakeRunner(engine, existing_container=True)

    with pytest.raises(engine.QualificationError, match="container already exists"):
        engine.qualify(
            repo_root=repo,
            receipt_path=tmp_path / "qualification.json",
            runner=runner,
            now=Clock(),
            temp_parent=tmp_path,
            platform_name="nt",
        )

    assert not any(command[:2] == ["supabase", "start"] for command, _cwd in runner.calls)


def test_sql_failure_and_cleanup_failure_are_both_preserved_and_no_receipt_is_written(tmp_path: Path) -> None:
    engine = _load_engine()
    repo = _init_candidate(tmp_path)
    receipt_path = tmp_path / "qualification.json"
    runner = FakeRunner(engine, fail_sql=True, fail_cleanup=True)

    with pytest.raises(engine.QualificationError) as caught:
        engine.qualify(
            repo_root=repo,
            receipt_path=receipt_path,
            runner=runner,
            now=Clock(),
            temp_parent=tmp_path,
            platform_name="nt",
        )

    message = str(caught.value)
    assert "all_radar_sql_assertions" in message
    assert "supabase_local_stop" in message
    assert not receipt_path.exists()
    assert any(command[:3] == ["supabase", "stop", "--no-backup"] for command, _cwd in runner.calls)
