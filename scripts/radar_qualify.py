from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Sequence


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: bytes
    stderr: bytes
    executable: str


@dataclass(frozen=True)
class StageEvidence:
    ordinal: int
    stage_id: str
    started_at_utc: str
    completed_at_utc: str
    exit_code: int
    executable: str
    stdout_sha256: str
    stderr_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SourceState:
    commit: str
    tree: str


class QualificationError(RuntimeError):
    """Raised when local qualification cannot produce an admissible PASS."""

    def __init__(self, message: str, *, evidence: StageEvidence | None = None) -> None:
        super().__init__(message)
        self.evidence = evidence


CommandRunner = Callable[[list[str], Path], CommandResult]
Clock = Callable[[], datetime]


def _utc_iso(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise QualificationError("qualification timestamps must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _default_runner(command: list[str], cwd: Path) -> CommandResult:
    if not command:
        raise QualificationError("qualification command cannot be empty")
    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        shell=False,
    )
    return CommandResult(
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
        executable=command[0],
    )


def run_stage(
    *,
    ordinal: int,
    stage_id: str,
    command: list[str],
    cwd: Path,
    runner: CommandRunner = _default_runner,
    now: Clock = lambda: datetime.now(timezone.utc),
) -> StageEvidence:
    if isinstance(ordinal, bool) or not isinstance(ordinal, int) or ordinal < 1:
        raise QualificationError("stage ordinal must be a positive integer")
    if not stage_id:
        raise QualificationError("stage_id must be non-empty")

    started = now()
    result = runner(command, cwd)
    completed = now()
    evidence = StageEvidence(
        ordinal=ordinal,
        stage_id=stage_id,
        started_at_utc=_utc_iso(started),
        completed_at_utc=_utc_iso(completed),
        exit_code=result.returncode,
        executable=result.executable,
        stdout_sha256=_sha256(result.stdout),
        stderr_sha256=_sha256(result.stderr),
    )
    if result.returncode != 0:
        raise QualificationError(
            f"qualification stage {stage_id} failed with exit code {result.returncode}",
            evidence=evidence,
        )
    return evidence


def canonical_stage_bytes(stages: Sequence[StageEvidence]) -> bytes:
    return json.dumps(
        [stage.to_dict() for stage in stages],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def canonical_stage_digest(stages: Sequence[StageEvidence]) -> str:
    return _sha256(canonical_stage_bytes(stages))


def build_pass_receipt(
    *,
    source_commit: str,
    source_tree: str,
    qualification_mode: str,
    toolchain: dict[str, Any],
    stages: Sequence[StageEvidence],
    required_stage_instances: Sequence[str],
    completed_at: datetime,
) -> dict[str, Any]:
    observed_ids = [stage.stage_id for stage in stages]
    expected_ids = list(required_stage_instances)
    if observed_ids != expected_ids:
        raise QualificationError(
            f"qualification stage sequence mismatch: expected {expected_ids!r}, observed {observed_ids!r}"
        )
    expected_ordinals = list(range(1, len(stages) + 1))
    observed_ordinals = [stage.ordinal for stage in stages]
    if observed_ordinals != expected_ordinals:
        raise QualificationError(
            f"qualification stage ordinal mismatch: expected {expected_ordinals!r}, observed {observed_ordinals!r}"
        )
    failed = [stage.stage_id for stage in stages if stage.exit_code != 0]
    if failed:
        raise QualificationError(f"cannot build PASS receipt with failed stages: {failed!r}")

    stage_list = [stage.to_dict() for stage in stages]
    return {
        "schema_version": 2,
        "status": "PASS",
        "qualification_mode": qualification_mode,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "working_tree": "CLEAN",
        "toolchain": dict(toolchain),
        "stages": stage_list,
        "stage_evidence_sha256": canonical_stage_digest(stages),
        "completed_at_utc": _utc_iso(completed_at),
    }


def ensure_external_receipt_path(receipt_path: Path, repo_root: Path) -> Path:
    repo_root = repo_root.resolve()
    receipt_path = receipt_path.resolve()
    if receipt_path == repo_root or receipt_path.is_relative_to(repo_root):
        raise QualificationError("receipt path must be outside source checkout")
    return receipt_path


def _git(repo_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        shell=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise QualificationError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def read_clean_source_state(repo_root: Path) -> SourceState:
    repo_root = repo_root.resolve()
    top_level = Path(_git(repo_root, "rev-parse", "--show-toplevel")).resolve()
    if top_level != repo_root:
        raise QualificationError(
            f"repo_root is not the Git top-level: expected {top_level}, observed {repo_root}"
        )
    working_tree = _git(repo_root, "status", "--porcelain", "--untracked-files=all")
    if working_tree:
        raise QualificationError("qualification source working tree is not clean")
    commit = _git(repo_root, "rev-parse", "HEAD")
    tree = _git(repo_root, "rev-parse", "HEAD^{tree}")
    if len(commit) != 40 or len(tree) != 40:
        raise QualificationError("could not bind exact source commit/tree")
    return SourceState(commit=commit, tree=tree)


def write_external_receipt(*, receipt: dict[str, Any], receipt_path: Path, repo_root: Path) -> Path:
    path = ensure_external_receipt_path(receipt_path, repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(receipt, sort_keys=True, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def _load_contract(repo_root: Path) -> tuple[str, dict[str, Any], list[str]]:
    path = repo_root / "architecture/contracts/RADAR_QUALIFICATION_V1.json"
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise QualificationError(f"could not load qualification contract: {exc}") from exc
    if contract.get("policy") != "NO_PAID_SERVICES":
        raise QualificationError("qualification contract policy is not NO_PAID_SERVICES")
    authority = contract.get("authoritative_qualification")
    if not isinstance(authority, dict):
        raise QualificationError("qualification contract authoritative_qualification is invalid")
    mode = authority.get("mode")
    toolchain = authority.get("required_toolchain")
    stages = authority.get("required_stage_instances")
    if not isinstance(mode, str) or not mode:
        raise QualificationError("qualification mode is invalid")
    if not isinstance(toolchain, dict):
        raise QualificationError("qualification required_toolchain is invalid")
    if not isinstance(stages, list) or not stages or not all(isinstance(x, str) and x for x in stages):
        raise QualificationError("qualification required_stage_instances is invalid")
    return mode, dict(toolchain), list(stages)


def _checked(runner: CommandRunner, command: list[str], cwd: Path, *, label: str) -> CommandResult:
    result = runner(command, cwd)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        if not detail:
            detail = result.stdout.decode("utf-8", errors="replace").strip()
        raise QualificationError(f"{label} failed with exit code {result.returncode}: {detail or 'no output'}")
    return result


def _stdout_text(result: CommandResult) -> str:
    return result.stdout.decode("utf-8", errors="replace").strip()


def _probe_toolchain(
    *, repo_root: Path, runner: CommandRunner, required: dict[str, Any], platform_name: str
) -> dict[str, Any]:
    if platform_name != "nt":
        raise QualificationError("authoritative local qualification requires Windows")

    python_required = required.get("python")
    if python_required != ["3.11", "3.12"]:
        raise QualificationError(f"unexpected Python qualification contract: {python_required!r}")
    for version in python_required:
        result = _checked(
            runner,
            ["py", f"-{version}", "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"],
            repo_root,
            label=f"Python {version} probe",
        )
        if _stdout_text(result) != version:
            raise QualificationError(f"Python {version} required; observed {_stdout_text(result)!r}")

    deno = _checked(runner, ["deno", "--version"], repo_root, label="Deno probe")
    deno_version = _stdout_text(deno).splitlines()[0] if _stdout_text(deno) else ""
    expected_deno = required.get("deno")
    if deno_version != f"deno {expected_deno}":
        raise QualificationError(f"Deno {expected_deno} required; observed {deno_version!r}")

    supabase = _checked(runner, ["supabase", "--version"], repo_root, label="Supabase CLI probe")
    expected_supabase = required.get("supabase_cli")
    if _stdout_text(supabase) != expected_supabase:
        raise QualificationError(
            f"Supabase CLI {expected_supabase} required; observed {_stdout_text(supabase)!r}"
        )

    _checked(runner, ["docker", "info"], repo_root, label="Docker health probe")
    docker = _checked(runner, ["docker", "--version"], repo_root, label="Docker identity probe")
    psql = _checked(runner, ["psql", "--version"], repo_root, label="psql identity probe")
    docker_identity = _stdout_text(docker)
    psql_identity = _stdout_text(psql)
    if not docker_identity or not psql_identity:
        raise QualificationError("Docker and psql probes must record non-empty identities")

    return {
        "python": list(python_required),
        "pip": required.get("pip"),
        "deno": expected_deno,
        "supabase_cli": expected_supabase,
        "docker": docker_identity,
        "psql": psql_identity,
    }


def _venv_python(venv: Path) -> Path:
    return venv / "Scripts" / "python.exe"


def _preflight_supabase(repo_root: Path, runner: CommandRunner) -> None:
    status = runner(["supabase", "status"], repo_root)
    if status.returncode == 0:
        raise QualificationError("Local Supabase stack is already running; refusing destructive qualification")

    project_id = "chat-communication-bus"
    db_resource = f"supabase_db_{project_id}"
    if runner(["docker", "container", "inspect", db_resource], repo_root).returncode == 0:
        raise QualificationError("Local Supabase database container already exists; refusing destructive qualification")
    if runner(["docker", "volume", "inspect", db_resource], repo_root).returncode == 0:
        raise QualificationError("Local Supabase database volume already exists; refusing destructive qualification")

    label = f"com.supabase.cli.project={project_id}"
    probes = (
        ["docker", "ps", "-a", "--filter", f"label={label}", "--format", "{{.ID}}"],
        ["docker", "volume", "ls", "--filter", f"label={label}", "--format", "{{.Name}}"],
        ["docker", "network", "ls", "--filter", f"label={label}", "--format", "{{.ID}}"],
    )
    for command in probes:
        result = _checked(runner, command, repo_root, label="Supabase Docker resource probe")
        if _stdout_text(result):
            raise QualificationError("Local Supabase project Docker resources already exist; refusing destructive qualification")


def _sql_stage_runner(
    *, runner: CommandRunner, repo_root: Path, sql_files: Sequence[Path]
) -> CommandRunner:
    def aggregate(_command: list[str], _cwd: Path) -> CommandResult:
        stdout = bytearray()
        stderr = bytearray()
        for sql_path in sql_files:
            command = [
                "psql",
                "postgresql://postgres:postgres@127.0.0.1:54322/postgres",
                "-v",
                "ON_ERROR_STOP=1",
                "-f",
                str(sql_path),
            ]
            result = runner(command, repo_root)
            stdout.extend(result.stdout)
            stderr.extend(result.stderr)
            if result.returncode != 0:
                return CommandResult(
                    returncode=result.returncode,
                    stdout=bytes(stdout),
                    stderr=bytes(stderr),
                    executable="psql",
                )
        return CommandResult(returncode=0, stdout=bytes(stdout), stderr=bytes(stderr), executable="psql")

    return aggregate


def qualify(
    *,
    repo_root: Path,
    receipt_path: Path,
    runner: CommandRunner = _default_runner,
    now: Clock = lambda: datetime.now(timezone.utc),
    temp_parent: Path | None = None,
    platform_name: str = os.name,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    receipt_path = ensure_external_receipt_path(receipt_path, repo_root)
    mode, required_toolchain, required_stage_instances = _load_contract(repo_root)
    source = read_clean_source_state(repo_root)
    toolchain = _probe_toolchain(
        repo_root=repo_root,
        runner=runner,
        required=required_toolchain,
        platform_name=platform_name,
    )

    stages: list[StageEvidence] = []
    temp_dirs: list[Path] = []
    try:
        for version in required_toolchain["python"]:
            venv = Path(
                tempfile.mkdtemp(
                    prefix=f"radar-qualify-{version}-{source.commit[:12]}-",
                    dir=str(temp_parent) if temp_parent is not None else None,
                )
            )
            temp_dirs.append(venv)
            _checked(
                runner,
                ["py", f"-{version}", "-m", "venv", str(venv)],
                repo_root,
                label=f"Python {version} venv creation",
            )
            python = str(_venv_python(venv))
            pip_pin = required_toolchain["pip"]
            _checked(
                runner,
                [python, "-m", "pip", "install", f"pip=={pip_pin}"],
                repo_root,
                label=f"Python {version} pip pin",
            )
            pip_version = _checked(
                runner,
                [python, "-m", "pip", "--version", "--disable-pip-version-check"],
                repo_root,
                label=f"Python {version} pip version",
            )
            if not _stdout_text(pip_version).startswith(f"pip {pip_pin} "):
                raise QualificationError(
                    f"pip {pip_pin} required for Python {version}; observed {_stdout_text(pip_version)!r}"
                )
            _checked(
                runner,
                [python, "-m", "pip", "install", "-e", ".[test]"],
                repo_root,
                label=f"Python {version} test dependency install",
            )

            stages.append(
                run_stage(
                    ordinal=len(stages) + 1,
                    stage_id=f"python_compileall:{version}",
                    command=[python, "-m", "compileall", "-q", "src"],
                    cwd=repo_root,
                    runner=runner,
                    now=now,
                )
            )
            stages.append(
                run_stage(
                    ordinal=len(stages) + 1,
                    stage_id=f"python_pytest:{version}",
                    command=[python, "-m", "pytest", "-q"],
                    cwd=repo_root,
                    runner=runner,
                    now=now,
                )
            )
            stages.append(
                run_stage(
                    ordinal=len(stages) + 1,
                    stage_id=f"radar_source_hashes:{version}",
                    command=[python, "scripts/radar_source_hashes.py"],
                    cwd=repo_root,
                    runner=runner,
                    now=now,
                )
            )

        edge_dir = repo_root / "supabase/functions/github-bus-ingest"
        stages.append(
            run_stage(
                ordinal=len(stages) + 1,
                stage_id="deno_ci",
                command=["deno", "ci"],
                cwd=edge_dir,
                runner=runner,
                now=now,
            )
        )
        stages.append(
            run_stage(
                ordinal=len(stages) + 1,
                stage_id="deno_check",
                command=["deno", "check", "index.ts"],
                cwd=edge_dir,
                runner=runner,
                now=now,
            )
        )

        sql_files = sorted((repo_root / "supabase/tests").glob("radar_*.sql"), key=lambda path: path.name)
        if not sql_files:
            raise QualificationError("No Radar SQL assertion files found")
        _preflight_supabase(repo_root, runner)

        primary_failure: QualificationError | None = None
        cleanup_failure: QualificationError | None = None
        try:
            stages.append(
                run_stage(
                    ordinal=9,
                    stage_id="supabase_local_start",
                    command=["supabase", "start"],
                    cwd=repo_root,
                    runner=runner,
                    now=now,
                )
            )
            stages.append(
                run_stage(
                    ordinal=10,
                    stage_id="supabase_db_reset",
                    command=["supabase", "db", "reset"],
                    cwd=repo_root,
                    runner=runner,
                    now=now,
                )
            )
            stages.append(
                run_stage(
                    ordinal=11,
                    stage_id="all_radar_sql_assertions",
                    command=["psql", "all-radar-sql-assertions"],
                    cwd=repo_root,
                    runner=_sql_stage_runner(runner=runner, repo_root=repo_root, sql_files=sql_files),
                    now=now,
                )
            )
        except QualificationError as exc:
            primary_failure = exc
        finally:
            try:
                stop = run_stage(
                    ordinal=12,
                    stage_id="supabase_local_stop",
                    command=["supabase", "stop", "--no-backup"],
                    cwd=repo_root,
                    runner=runner,
                    now=now,
                )
                if primary_failure is None:
                    stages.append(stop)
            except QualificationError as exc:
                cleanup_failure = exc

        if primary_failure is not None and cleanup_failure is not None:
            raise QualificationError(f"{primary_failure}; {cleanup_failure}")
        if cleanup_failure is not None:
            raise cleanup_failure
        if primary_failure is not None:
            raise primary_failure

        final_source = read_clean_source_state(repo_root)
        if final_source != source:
            raise QualificationError("source commit/tree changed during qualification")

        receipt = build_pass_receipt(
            source_commit=source.commit,
            source_tree=source.tree,
            qualification_mode=mode,
            toolchain=toolchain,
            stages=stages,
            required_stage_instances=required_stage_instances,
            completed_at=now(),
        )
        write_external_receipt(receipt=receipt, receipt_path=receipt_path, repo_root=repo_root)
        return receipt
    finally:
        for path in temp_dirs:
            shutil.rmtree(path, ignore_errors=True)
