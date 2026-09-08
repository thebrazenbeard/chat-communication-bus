from __future__ import annotations

import hashlib
import json
import subprocess
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
