"""Topology-bound, exact-head Git append primitive for Radar writer lanes.

The module is deliberately transport-neutral.  Concrete runtimes inject three
small sources/backends: canonical control state, complete identity history, and
Git object/ref operations.  The public append operation itself accepts only the
logical identity, exact expected current-lane head, and exact message bytes.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import re
from typing import Mapping, Protocol


_SHA40_RE = re.compile(r"^[0-9a-fA-F]{40}$")
_IDENTITY_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_MESSAGE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*-[A-Za-z0-9][A-Za-z0-9._-]*$")


@dataclass(frozen=True)
class LaneBinding:
    identity: str
    writer: str
    branch: str


@dataclass(frozen=True)
class ControlSnapshot:
    repository: str
    control_commit_sha: str
    topology_digest: str
    lanes: Mapping[str, LaneBinding]


@dataclass(frozen=True)
class CommittedMessage:
    message_id: str
    message_sha256: str
    commit_sha: str
    path: str
    blob_sha: str
    prev_message_id: str | None
    branch: str | None = None


@dataclass(frozen=True)
class IdentityHistory:
    complete: bool
    tip_message_ids: tuple[str, ...]
    messages: tuple[CommittedMessage, ...]


@dataclass(frozen=True)
class CommitReadback:
    parent_shas: tuple[str, ...]
    tree_sha: str
    changed_paths: tuple[str, ...]


@dataclass(frozen=True)
class FileReadback:
    blob_sha: str
    content: bytes


@dataclass(frozen=True)
class SafeAppendReceipt:
    schema: str
    result: str
    operation_key: str
    identity: str
    derived_writer: str
    asserted_writer: str
    lane_ref: str
    control_commit_sha: str
    topology_blob_sha: str
    expected_lane_head: str
    prewrite_observed_head: str
    commit_sha: str
    commit_parent_sha: str
    postwrite_observed_head: str
    tree_sha: str
    path: str
    message_id: str
    prev_message_id: str | None
    message_blob_sha: str
    message_sha256: str
    readback_verified: bool
    current_lane_after_readback: bool
    projection_state: str = "NOT_ESTABLISHED"
    delivery_state: str = "NOT_ESTABLISHED"
    incorporation_state: str = "NOT_ESTABLISHED"


class SafeAppendError(RuntimeError):
    """Stable operator-facing failure from the safe append state machine."""

    def __init__(
        self,
        code: str,
        *,
        phase: str,
        retry_class: str,
        effect_state: str,
        detail: str | None = None,
    ) -> None:
        self.code = code
        self.phase = phase
        self.retry_class = retry_class
        self.effect_state = effect_state
        self.detail = detail
        suffix = f": {detail}" if detail else ""
        super().__init__(f"{code}{suffix}")


class ControlSource(Protocol):
    def read(self) -> ControlSnapshot: ...


class HistorySource(Protocol):
    def read_identity(self, identity: str) -> IdentityHistory: ...


class GitBackend(Protocol):
    def read_branch_head(self, branch: str) -> str | None: ...

    def read_file_at_commit(self, commit_sha: str, path: str) -> FileReadback | None: ...

    def read_commit(self, commit_sha: str) -> CommitReadback | None: ...

    def create_blob(self, content: bytes) -> str: ...

    def create_tree(self, base_commit_sha: str, path: str, blob_sha: str) -> str: ...

    def create_commit(self, message: str, tree_sha: str, parent_sha: str) -> str: ...

    def update_ref_non_force(self, branch: str, candidate_sha: str) -> bool: ...


@dataclass(frozen=True)
class _ParsedMessage:
    message_id: str
    writer: str
    prev_message_id: str | None


_PREWRITE_RETRY = "REFRESH_OR_CORRECT_INPUT"
_OBJECT_RETRY = "RECONCILE_THEN_RETRY"
_REF_RETRY = "RECONCILE_EFFECT_FIRST"
_READBACK_RETRY = "RECONCILE_EFFECT_FIRST"


def _error(
    code: str,
    *,
    phase: str = "PREFLIGHT",
    retry_class: str = _PREWRITE_RETRY,
    effect_state: str = "NONE_ESTABLISHED",
    detail: str | None = None,
) -> SafeAppendError:
    return SafeAppendError(
        code,
        phase=phase,
        retry_class=retry_class,
        effect_state=effect_state,
        detail=detail,
    )


def _as_exact_utf8(message_utf8: str | bytes) -> tuple[str, bytes]:
    if isinstance(message_utf8, str):
        return message_utf8, message_utf8.encode("utf-8")
    if isinstance(message_utf8, bytes):
        try:
            return message_utf8.decode("utf-8"), message_utf8
        except UnicodeDecodeError as exc:
            raise _error("MESSAGE_NOT_UTF8", detail=str(exc)) from exc
    raise _error("MESSAGE_NOT_UTF8", detail="message must be str or bytes")


def _parse_message(text: str) -> _ParsedMessage:
    """Parse the Bus header block without rewriting or normalizing source bytes."""

    wanted = {"message_id", "writer", "prev_message_id"}
    values: dict[str, str] = {}
    started = False

    for line in text.splitlines():
        if not started:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip().casefold()
            if key not in wanted:
                continue
            started = True
        else:
            if not line.strip():
                break
            if ":" not in line:
                raise _error("MESSAGE_ENVELOPE_INVALID", detail="non-header line inside header block")
            key, value = line.split(":", 1)
            key = key.strip().casefold()
            if key not in wanted:
                # Other Bus metadata headers are allowed and left byte-exact.
                continue

        value = value.strip()
        if key in values:
            raise _error("MESSAGE_ENVELOPE_INVALID", detail=f"duplicate {key} header")
        values[key] = value

    message_id = values.get("message_id")
    writer = values.get("writer")
    if not message_id:
        raise _error("MESSAGE_ENVELOPE_INVALID", detail="message_id header missing")
    if not writer:
        raise _error("WRITER_MISSING")

    return _ParsedMessage(
        message_id=message_id,
        writer=writer,
        prev_message_id=values.get("prev_message_id") or None,
    )


def _validate_identity(identity: str) -> str:
    if not isinstance(identity, str) or not _IDENTITY_RE.fullmatch(identity):
        raise _error("IDENTITY_UNKNOWN")
    return identity


def _validate_expected_head(expected_lane_head: str) -> str:
    if not isinstance(expected_lane_head, str) or not _SHA40_RE.fullmatch(expected_lane_head):
        raise _error("EXPECTED_HEAD_INVALID")
    return expected_lane_head.lower()


def _validate_message_id(identity: str, message_id: str) -> None:
    if not _MESSAGE_ID_RE.fullmatch(message_id):
        raise _error("MESSAGE_ID_INVALID")
    if not message_id.startswith(f"{identity}-"):
        raise _error("MESSAGE_ID_INVALID", detail="message id is not writer-local to logical identity")


def _same_binding(a: ControlSnapshot, b: ControlSnapshot, identity: str) -> bool:
    if a.repository != b.repository or a.topology_digest != b.topology_digest:
        return False
    return a.lanes.get(identity) == b.lanes.get(identity)


class SafeLaneAppender:
    """Application-level V1 append operation with a three-argument public call."""

    def __init__(
        self,
        *,
        control_source: ControlSource,
        history_source: HistorySource,
        git_backend: GitBackend,
    ) -> None:
        self._control = control_source
        self._history = history_source
        self._git = git_backend

    def append_bus_message_v1(
        self,
        identity: str,
        expected_lane_head: str,
        message_utf8: str | bytes,
    ) -> SafeAppendReceipt:
        identity = _validate_identity(identity)
        expected_head = _validate_expected_head(expected_lane_head)
        text, message_bytes = _as_exact_utf8(message_utf8)
        parsed = _parse_message(text)
        _validate_message_id(identity, parsed.message_id)
        message_digest = sha256(message_bytes).hexdigest()
        operation_key = f"radar-safe-append-v1:{identity}:{parsed.message_id}:{message_digest}"

        try:
            control = self._control.read()
        except Exception as exc:
            if isinstance(exc, SafeAppendError):
                raise
            raise _error("TOPOLOGY_UNAVAILABLE", detail=str(exc)) from exc

        binding = control.lanes.get(identity)
        if binding is None:
            raise _error("IDENTITY_UNKNOWN")
        if binding.identity != identity:
            raise _error("TOPOLOGY_IDENTITY_AMBIGUOUS")
        if parsed.writer.casefold() != binding.writer.casefold():
            raise _error("WRITER_MISMATCH")

        try:
            observed_head = self._git.read_branch_head(binding.branch)
        except Exception as exc:
            raise _error("LANE_UNREGISTERED", detail=str(exc)) from exc
        if observed_head is None:
            raise _error("LANE_MISSING_BOOTSTRAP_REQUIRED")

        try:
            history = self._history.read_identity(identity)
        except Exception as exc:
            if isinstance(exc, SafeAppendError):
                raise
            raise _error("MESSAGE_ID_HISTORY_UNRESOLVED", detail=str(exc)) from exc
        if not history.complete:
            raise _error("MESSAGE_ID_HISTORY_UNRESOLVED")

        duplicates = [item for item in history.messages if item.message_id == parsed.message_id]
        if duplicates:
            if len(duplicates) != 1 or duplicates[0].message_sha256 != message_digest:
                raise _error("MESSAGE_ID_COLLISION")
            return self._reconstruct_existing(
                control=control,
                current_binding=binding,
                expected_head=expected_head,
                observed_head=observed_head,
                parsed=parsed,
                message_bytes=message_bytes,
                message_digest=message_digest,
                operation_key=operation_key,
                existing=duplicates[0],
            )

        if observed_head.lower() != expected_head:
            raise _error("STALE_LANE_HEAD")

        if len(history.tip_message_ids) > 1:
            raise _error("PREDECESSOR_UNRESOLVED")
        if history.messages and len(history.tip_message_ids) != 1:
            raise _error("PREDECESSOR_UNRESOLVED")
        if history.tip_message_ids:
            expected_prev = history.tip_message_ids[0]
            if parsed.prev_message_id is None:
                raise _error("PREDECESSOR_MISSING")
            if parsed.prev_message_id != expected_prev:
                raise _error("PREDECESSOR_MISMATCH")
        elif parsed.prev_message_id is not None:
            # A source-backed genesis has no predecessor; caller cannot invent one.
            raise _error("PREDECESSOR_MISMATCH")

        path = f"messages/{parsed.message_id}.md"
        try:
            preexisting_path = self._git.read_file_at_commit(expected_head, path)
        except Exception as exc:
            raise _error("MESSAGE_PATH_COLLISION", detail=str(exc)) from exc
        if preexisting_path is not None:
            raise _error("MESSAGE_PATH_COLLISION")

        try:
            blob_sha = self._git.create_blob(message_bytes)
        except Exception as exc:
            raise _error(
                "BLOB_CREATE_FAILED",
                phase="OBJECT_CONSTRUCTION",
                retry_class=_OBJECT_RETRY,
                detail=str(exc),
            ) from exc
        try:
            tree_sha = self._git.create_tree(expected_head, path, blob_sha)
        except Exception as exc:
            raise _error(
                "TREE_CREATE_FAILED",
                phase="OBJECT_CONSTRUCTION",
                retry_class=_OBJECT_RETRY,
                detail=str(exc),
            ) from exc
        try:
            candidate_sha = self._git.create_commit(
                f"bus: append {parsed.message_id}",
                tree_sha,
                expected_head,
            )
        except Exception as exc:
            raise _error(
                "COMMIT_CREATE_FAILED",
                phase="OBJECT_CONSTRUCTION",
                retry_class=_OBJECT_RETRY,
                detail=str(exc),
            ) from exc

        try:
            rebound = self._control.read()
        except Exception as exc:
            raise _error("TOPOLOGY_CHANGED_DURING_APPEND", detail=str(exc)) from exc
        if not _same_binding(control, rebound, identity):
            raise _error("TOPOLOGY_CHANGED_DURING_APPEND")

        update_error: Exception | None = None
        try:
            moved = self._git.update_ref_non_force(binding.branch, candidate_sha)
        except Exception as exc:  # ambiguous transport outcome: reconcile first
            moved = False
            update_error = exc

        try:
            after_update_head = self._git.read_branch_head(binding.branch)
        except Exception as exc:
            raise _error(
                "WRITE_OUTCOME_UNKNOWN",
                phase="REF_TRANSITION",
                retry_class=_REF_RETRY,
                effect_state="UNKNOWN",
                detail=str(exc),
            ) from exc

        if update_error is not None:
            if after_update_head != candidate_sha:
                reachability = self._candidate_reachability(candidate_sha, after_update_head)
                if reachability is True:
                    raise _error(
                        "POSTWRITE_HEAD_MISMATCH",
                        phase="READBACK",
                        retry_class=_READBACK_RETRY,
                        effect_state="PRESENT_UNVERIFIED",
                        detail="candidate became reachable but is no longer lane head",
                    ) from update_error
                if reachability is False and after_update_head != expected_head:
                    raise _error(
                        "REF_UPDATE_STALE",
                        phase="REF_TRANSITION",
                        retry_class=_REF_RETRY,
                        effect_state="NONE_ESTABLISHED",
                    ) from update_error
                raise _error(
                    "WRITE_OUTCOME_UNKNOWN",
                    phase="REF_TRANSITION",
                    retry_class=_REF_RETRY,
                    effect_state="UNKNOWN",
                    detail=str(update_error),
                ) from update_error
        elif not moved:
            if after_update_head == candidate_sha:
                moved = True
            elif after_update_head != expected_head:
                raise _error(
                    "REF_UPDATE_STALE",
                    phase="REF_TRANSITION",
                    retry_class=_REF_RETRY,
                    effect_state="NONE_ESTABLISHED",
                )
            else:
                raise _error(
                    "REF_UPDATE_REJECTED",
                    phase="REF_TRANSITION",
                    retry_class=_REF_RETRY,
                    effect_state="NONE_ESTABLISHED",
                )

        return self._verify_new_append(
            control=control,
            binding=binding,
            expected_head=expected_head,
            prewrite_observed_head=observed_head,
            candidate_sha=candidate_sha,
            tree_sha=tree_sha,
            path=path,
            blob_sha=blob_sha,
            parsed=parsed,
            message_bytes=message_bytes,
            message_digest=message_digest,
            operation_key=operation_key,
        )

    def _candidate_reachability(self, candidate_sha: str, head_sha: str | None) -> bool | None:
        if head_sha is None:
            return None
        method = getattr(self._git, "is_ancestor", None)
        if method is None:
            return None
        try:
            return bool(method(candidate_sha, head_sha))
        except Exception:
            return None

    def _reconstruct_existing(
        self,
        *,
        control: ControlSnapshot,
        current_binding: LaneBinding,
        expected_head: str,
        observed_head: str,
        parsed: _ParsedMessage,
        message_bytes: bytes,
        message_digest: str,
        operation_key: str,
        existing: CommittedMessage,
    ) -> SafeAppendReceipt:
        commit = self._git.read_commit(existing.commit_sha)
        file_record = self._git.read_file_at_commit(existing.commit_sha, existing.path)
        if commit is None or file_record is None or len(commit.parent_shas) != 1:
            raise _error(
                "RECEIPT_INCOMPLETE",
                phase="READBACK",
                retry_class=_READBACK_RETRY,
                effect_state="PRESENT_UNVERIFIED",
            )
        if file_record.content != message_bytes or sha256(file_record.content).hexdigest() != message_digest:
            raise _error(
                "POSTWRITE_CONTENT_MISMATCH",
                phase="READBACK",
                retry_class=_READBACK_RETRY,
                effect_state="PRESENT_UNVERIFIED",
            )
        if existing.blob_sha and existing.blob_sha != file_record.blob_sha:
            raise _error(
                "RECEIPT_INCOMPLETE",
                phase="READBACK",
                retry_class=_READBACK_RETRY,
                effect_state="PRESENT_UNVERIFIED",
                detail="history blob differs from Git readback",
            )
        readback_parsed = _parse_message(file_record.content.decode("utf-8"))
        if readback_parsed != parsed:
            raise _error(
                "POSTWRITE_METADATA_MISMATCH",
                phase="READBACK",
                retry_class=_READBACK_RETRY,
                effect_state="PRESENT_UNVERIFIED",
            )

        final_control = self._control.read()
        final_binding = final_control.lanes.get(parsed.message_id.split("-", 1)[0])
        lane_used = existing.branch or current_binding.branch
        current_lane = final_binding is not None and final_binding.branch == lane_used

        return SafeAppendReceipt(
            schema="RADAR_SAFE_LANE_APPEND_RECEIPT_V1",
            result="ALREADY_COMMITTED",
            operation_key=operation_key,
            identity=current_binding.identity,
            derived_writer=current_binding.writer,
            asserted_writer=parsed.writer,
            lane_ref=lane_used,
            control_commit_sha=control.control_commit_sha,
            topology_blob_sha=control.topology_digest,
            expected_lane_head=expected_head,
            prewrite_observed_head=observed_head,
            commit_sha=existing.commit_sha,
            commit_parent_sha=commit.parent_shas[0],
            postwrite_observed_head=observed_head,
            tree_sha=commit.tree_sha,
            path=existing.path,
            message_id=parsed.message_id,
            prev_message_id=parsed.prev_message_id,
            message_blob_sha=file_record.blob_sha,
            message_sha256=message_digest,
            readback_verified=True,
            current_lane_after_readback=current_lane,
        )

    def _verify_new_append(
        self,
        *,
        control: ControlSnapshot,
        binding: LaneBinding,
        expected_head: str,
        prewrite_observed_head: str,
        candidate_sha: str,
        tree_sha: str,
        path: str,
        blob_sha: str,
        parsed: _ParsedMessage,
        message_bytes: bytes,
        message_digest: str,
        operation_key: str,
    ) -> SafeAppendReceipt:
        head = self._git.read_branch_head(binding.branch)
        if head != candidate_sha:
            raise _error(
                "POSTWRITE_HEAD_MISMATCH",
                phase="READBACK",
                retry_class=_READBACK_RETRY,
                effect_state="PRESENT_UNVERIFIED",
            )

        commit = self._git.read_commit(candidate_sha)
        if (
            commit is None
            or commit.parent_shas != (expected_head,)
            or commit.tree_sha != tree_sha
        ):
            raise _error(
                "POSTWRITE_COMMIT_SHAPE_MISMATCH",
                phase="READBACK",
                retry_class=_READBACK_RETRY,
                effect_state="PRESENT_UNVERIFIED",
            )
        if commit.changed_paths != (path,):
            raise _error(
                "POSTWRITE_PATH_MISMATCH",
                phase="READBACK",
                retry_class=_READBACK_RETRY,
                effect_state="PRESENT_UNVERIFIED",
            )

        file_record = self._git.read_file_at_commit(candidate_sha, path)
        if file_record is None:
            raise _error(
                "POSTWRITE_PATH_MISMATCH",
                phase="READBACK",
                retry_class=_READBACK_RETRY,
                effect_state="PRESENT_UNVERIFIED",
            )
        if file_record.content != message_bytes or file_record.blob_sha != blob_sha:
            raise _error(
                "POSTWRITE_CONTENT_MISMATCH",
                phase="READBACK",
                retry_class=_READBACK_RETRY,
                effect_state="PRESENT_UNVERIFIED",
            )
        if sha256(file_record.content).hexdigest() != message_digest:
            raise _error(
                "POSTWRITE_CONTENT_MISMATCH",
                phase="READBACK",
                retry_class=_READBACK_RETRY,
                effect_state="PRESENT_UNVERIFIED",
            )
        try:
            readback_parsed = _parse_message(file_record.content.decode("utf-8"))
        except Exception as exc:
            raise _error(
                "POSTWRITE_METADATA_MISMATCH",
                phase="READBACK",
                retry_class=_READBACK_RETRY,
                effect_state="PRESENT_UNVERIFIED",
                detail=str(exc),
            ) from exc
        if readback_parsed != parsed:
            raise _error(
                "POSTWRITE_METADATA_MISMATCH",
                phase="READBACK",
                retry_class=_READBACK_RETRY,
                effect_state="PRESENT_UNVERIFIED",
            )

        try:
            final_control = self._control.read()
        except Exception:
            final_control = None
        final_binding = final_control.lanes.get(binding.identity) if final_control else None
        current_lane = final_binding is not None and final_binding.branch == binding.branch

        return SafeAppendReceipt(
            schema="RADAR_SAFE_LANE_APPEND_RECEIPT_V1",
            result="APPENDED",
            operation_key=operation_key,
            identity=binding.identity,
            derived_writer=binding.writer,
            asserted_writer=parsed.writer,
            lane_ref=binding.branch,
            control_commit_sha=control.control_commit_sha,
            topology_blob_sha=control.topology_digest,
            expected_lane_head=expected_head,
            prewrite_observed_head=prewrite_observed_head,
            commit_sha=candidate_sha,
            commit_parent_sha=expected_head,
            postwrite_observed_head=head,
            tree_sha=tree_sha,
            path=path,
            message_id=parsed.message_id,
            prev_message_id=parsed.prev_message_id,
            message_blob_sha=file_record.blob_sha,
            message_sha256=message_digest,
            readback_verified=True,
            current_lane_after_readback=current_lane,
        )


__all__ = [
    "CommitReadback",
    "CommittedMessage",
    "ControlSnapshot",
    "FileReadback",
    "GitBackend",
    "HistorySource",
    "IdentityHistory",
    "LaneBinding",
    "SafeAppendError",
    "SafeAppendReceipt",
    "SafeLaneAppender",
]
