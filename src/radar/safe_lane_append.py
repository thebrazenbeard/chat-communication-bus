"""Topology-bound, exact-head Git append primitive for Radar writer lanes.

Concrete runtimes inject canonical control state, complete cross-generation
identity history, and Git object/ref operations.  The public append operation
itself accepts only logical identity, exact expected current-lane head, and
exact message bytes/text.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import re
from typing import Mapping, Protocol


_SHA40_RE = re.compile(r"^[0-9a-fA-F]{40}$")
_IDENTITY_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_MESSAGE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*-[A-Za-z0-9][A-Za-z0-9._-]*$")


class RetryClass(str, Enum):
    """Retry guidance for operator handling of SafeAppendError."""

    PREWRITE = "REFRESH_OR_CORRECT_INPUT"
    OBJECT = "RECONCILE_THEN_RETRY"
    REF = "RECONCILE_EFFECT_FIRST"
    READBACK = "RECONCILE_EFFECT_FIRST"


class ReceiptState(str, Enum):
    """State machine values for receipt tracking fields."""

    NOT_ESTABLISHED = "NOT_ESTABLISHED"
    PRESENT_VERIFIED = "PRESENT_VERIFIED"
    PRESENT_UNVERIFIED = "PRESENT_UNVERIFIED"


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
    projection_state: str = ReceiptState.NOT_ESTABLISHED.value
    delivery_state: str = ReceiptState.NOT_ESTABLISHED.value
    incorporation_state: str = ReceiptState.NOT_ESTABLISHED.value


class SafeAppendError(RuntimeError):
    """Stable operator-facing failure from the safe append state machine.

    Attributes:
        code: Error classification code (e.g., "STALE_LANE_HEAD").
        phase: Append phase where error occurred (e.g., "PREFLIGHT", "REF_TRANSITION", "READBACK").
        retry_class: Operator guidance on recovery strategy (e.g., retry, refresh input, reconcile).
        effect_state: Indicates whether Git objects/refs were created before failure.
        detail: Optional implementation-level detail for debugging.
    """

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
    """Provides current topology binding and writer lanes."""

    def read(self) -> ControlSnapshot:
        """Read current control topology snapshot.

        Returns:
            ControlSnapshot with current repository, control commit, and lane bindings.

        Raises:
            SafeAppendError or arbitrary Exception on availability issues.
        """
        ...


class HistorySource(Protocol):
    """Provides complete identity message history for consistency checks."""

    def read_identity(self, identity: str) -> IdentityHistory:
        """Read complete message history for a logical identity.

        Args:
            identity: Logical identity to query.

        Returns:
            IdentityHistory with all committed messages and tip state.

        Raises:
            SafeAppendError or arbitrary Exception on incomplete/unavailable history.
        """
        ...


class GitBackend(Protocol):
    """Git object and ref operations."""

    def read_branch_head(self, branch: str) -> str | None:
        """Read current ref HEAD (SHA40) for a branch.

        Returns None if branch does not exist. Raises on read errors.
        """
        ...

    def read_file_at_commit(
        self, commit_sha: str, path: str
    ) -> FileReadback | None:
        """Read file content and blob SHA at a specific commit.

        Returns None if file does not exist at that commit. Raises on read errors.
        """
        ...

    def read_commit(self, commit_sha: str) -> CommitReadback | None:
        """Read commit metadata (parents, tree, changed paths).

        Returns None if commit does not exist. Raises on read errors.
        """
        ...

    def create_blob(self, content: bytes) -> str:
        """Create a new blob object; return its SHA40."""
        ...

    def create_tree(self, base_commit_sha: str, path: str, blob_sha: str) -> str:
        """Create a new tree based on base_commit, updating/inserting file at path."""
        ...

    def create_commit(self, message: str, tree_sha: str, parent_sha: str) -> str:
        """Create a new commit; return its SHA40."""
        ...

    def update_ref_non_force(self, branch: str, candidate_sha: str) -> bool:
        """Atomically update branch ref to candidate_sha (fast-forward only).

        Returns True if update succeeded, False if rejected (not a fast-forward).
        Raises on unexpected errors (permissions, I/O, etc.).
        """
        ...


@dataclass(frozen=True)
class _ParsedMessage:
    message_id: str
    writer: str
    prev_message_id: str | None


def _error(
    code: str,
    *,
    phase: str = "PREFLIGHT",
    retry_class: str = RetryClass.PREWRITE.value,
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
    """Parse the metadata block while preserving submitted bytes unchanged.

    Expected format:
        message_id: <id>
        writer: <writer>
        prev_message_id: <id>  (optional)

        <rest of message body>

    Args:
        text: UTF-8 decoded message.

    Returns:
        Parsed metadata (message_id, writer, prev_message_id).

    Raises:
        SafeAppendError on malformed or missing required headers.
    """

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
                raise _error(
                    "MESSAGE_ENVELOPE_INVALID",
                    detail="non-header line inside header block",
                )
            key, value = line.split(":", 1)
            key = key.strip().casefold()
            if key not in wanted:
                continue

        value = value.strip()
        if key in values:
            raise _error(
                "MESSAGE_ENVELOPE_INVALID",
                detail=f"duplicate {key} header",
            )
        values[key] = value

    message_id = values.get("message_id")
    writer = values.get("writer")
    if not message_id:
        raise _error(
            "MESSAGE_ENVELOPE_INVALID",
            detail="message_id header missing",
        )
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
    if (
        not isinstance(expected_lane_head, str)
        or not _SHA40_RE.fullmatch(expected_lane_head)
    ):
        raise _error("EXPECTED_HEAD_INVALID")
    return expected_lane_head.lower()


def _validate_message_id(identity: str, message_id: str) -> None:
    if not _MESSAGE_ID_RE.fullmatch(message_id):
        raise _error("MESSAGE_ID_INVALID")
    if not message_id.startswith(f"{identity}-"):
        raise _error(
            "MESSAGE_ID_INVALID",
            detail="message id is not writer-local to logical identity",
        )


def _same_binding(
    first: ControlSnapshot,
    second: ControlSnapshot,
    identity: str,
) -> bool:
    if (
        first.repository != second.repository
        or first.topology_digest != second.topology_digest
    ):
        return False
    return first.lanes.get(identity) == second.lanes.get(identity)


class SafeLaneAppender:
    """Application-level V1 append operation with a three-argument public call.

    Provides strong consistency guarantees:
      - Idempotent: duplicate messages (same ID and content) are safely redetected.
      - Exact-head: appends only if branch head matches expected value (optimistic lock).
      - Verified: all Git objects/refs are read back and byte-verified after write.
    """

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
        """Append a message to a lane with strong topology and consistency guarantees.

        Enforces:
          - Identity is registered in current topology.
          - Writer identity matches topology binding.
          - Lane head has not advanced (optimistic concurrency lock).
          - Message ID is unique and locally scoped to the identity.
          - Predecessor chain is valid (single tip, matching prev_message_id).

        Args:
            identity: Logical identity scoped to this control topology.
                Must match pattern ^[a-z0-9][a-z0-9_-]*$.
            expected_lane_head: SHA40 of the expected current lane head.
                Ensures optimistic concurrency control; fails (STALE_LANE_HEAD)
                if another writer has moved the branch.
            message_utf8: UTF-8 message with metadata envelope:
                message_id: <id>
                writer: <writer>
                prev_message_id: <id>  (optional for first message)

                <rest of message body, preserved exactly>

        Returns:
            SafeAppendReceipt with full post-write state, including operation key,
            commit SHAs, verified blob content, and lane routing status.

        Raises:
            SafeAppendError: One of ~15 failure modes, classified by code, phase, and
                retry_class. See SafeAppendError attributes for routing guidance.
                Common codes:
                  - IDENTITY_UNKNOWN: identity not in topology.
                  - WRITER_MISMATCH: asserted writer ≠ topology binding.
                  - STALE_LANE_HEAD: expected_lane_head does not match current branch.
                  - MESSAGE_ID_COLLISION: message_id exists with different content.
                  - TOPOLOGY_CHANGED_DURING_APPEND: topology changed between preflight and ref update.
                  - REF_UPDATE_REJECTED: ref update lost a race.
        """
        identity = _validate_identity(identity)
        expected_head = _validate_expected_head(expected_lane_head)
        text, message_bytes = _as_exact_utf8(message_utf8)
        parsed = _parse_message(text)
        _validate_message_id(identity, parsed.message_id)
        message_digest = sha256(message_bytes).hexdigest()
        operation_key = (
            f"radar-safe-append-v1:{identity}:"
            f"{parsed.message_id}:{message_digest}"
        )

        control = self._read_control_preflight()
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

        history = self._read_history(identity)
        duplicates = [
            item
            for item in history.messages
            if item.message_id == parsed.message_id
        ]
        if duplicates:
            if (
                len(duplicates) != 1
                or duplicates[0].message_sha256 != message_digest
            ):
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

        self._validate_predecessor(history, parsed)
        path = f"messages/{parsed.message_id}.md"
        try:
            preexisting_path = self._git.read_file_at_commit(
                expected_head,
                path,
            )
        except Exception as exc:
            raise _error("MESSAGE_PATH_COLLISION", detail=str(exc)) from exc
        if preexisting_path is not None:
            raise _error("MESSAGE_PATH_COLLISION")

        blob_sha = self._create_blob(message_bytes)
        tree_sha = self._create_tree(expected_head, path, blob_sha)
        candidate_sha = self._create_commit(
            parsed.message_id,
            tree_sha,
            expected_head,
        )

        rebound = self._read_control_before_ref()
        if not _same_binding(control, rebound, identity):
            raise _error("TOPOLOGY_CHANGED_DURING_APPEND")

        self._move_ref_or_reconcile(
            binding.branch,
            candidate_sha,
            expected_head,
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

    def _read_control_preflight(self) -> ControlSnapshot:
        try:
            return self._control.read()
        except Exception as exc:
            if isinstance(exc, SafeAppendError):
                raise
            raise _error("TOPOLOGY_UNAVAILABLE", detail=str(exc)) from exc

    def _read_control_before_ref(self) -> ControlSnapshot:
        try:
            return self._control.read()
        except Exception as exc:
            raise _error(
                "TOPOLOGY_CHANGED_DURING_APPEND",
                detail=str(exc),
            ) from exc

    def _read_control_after_verified_effect(self) -> ControlSnapshot:
        try:
            return self._control.read()
        except Exception as exc:
            # The Git effect is already byte/shape verified.  Current-routing
            # status is still unknown, so do not collapse UNKNOWN into False.
            raise _error(
                "RECEIPT_INCOMPLETE",
                phase="READBACK",
                retry_class=RetryClass.READBACK.value,
                effect_state=ReceiptState.PRESENT_VERIFIED.value,
                detail=f"current topology readback unavailable: {exc}",
            ) from exc

    def _read_history(self, identity: str) -> IdentityHistory:
        try:
            history = self._history.read_identity(identity)
        except Exception as exc:
            if isinstance(exc, SafeAppendError):
                raise
            raise _error(
                "MESSAGE_ID_HISTORY_UNRESOLVED",
                detail=str(exc),
            ) from exc
        if not history.complete:
            raise _error("MESSAGE_ID_HISTORY_UNRESOLVED")
        return history

    def _validate_predecessor(
        self,
        history: IdentityHistory,
        parsed: _ParsedMessage,
    ) -> None:
        """Validate that prev_message_id matches history tip and single lineage.

        Requires:
          - At most one tip (single predecessor or first message).
          - If history has messages, must have exactly one tip.
          - If tip exists, prev_message_id must match it.
          - If no tip exists, prev_message_id must be None (first message).
        """
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
            raise _error("PREDECESSOR_MISMATCH")

    def _create_blob(self, content: bytes) -> str:
        try:
            return self._git.create_blob(content)
        except Exception as exc:
            raise _error(
                "BLOB_CREATE_FAILED",
                phase="OBJECT_CONSTRUCTION",
                retry_class=RetryClass.OBJECT.value,
                detail=str(exc),
            ) from exc

    def _create_tree(
        self,
        expected_head: str,
        path: str,
        blob_sha: str,
    ) -> str:
        try:
            return self._git.create_tree(
                expected_head,
                path,
                blob_sha,
            )
        except Exception as exc:
            raise _error(
                "TREE_CREATE_FAILED",
                phase="OBJECT_CONSTRUCTION",
                retry_class=RetryClass.OBJECT.value,
                detail=str(exc),
            ) from exc

    def _create_commit(
        self,
        message_id: str,
        tree_sha: str,
        expected_head: str,
    ) -> str:
        try:
            return self._git.create_commit(
                f"bus: append {message_id}",
                tree_sha,
                expected_head,
            )
        except Exception as exc:
            raise _error(
                "COMMIT_CREATE_FAILED",
                phase="OBJECT_CONSTRUCTION",
                retry_class=RetryClass.OBJECT.value,
                detail=str(exc),
            ) from exc

    def _move_ref_or_reconcile(
        self,
        branch: str,
        candidate_sha: str,
        expected_head: str,
    ) -> None:
        """Atomically update branch ref and reconcile on failure.

        Attempts a fast-forward ref update. If it fails or the readback shows
        an unexpected state, raises detailed error with retry guidance.
        """
        update_error: Exception | None = None
        try:
            moved = self._git.update_ref_non_force(branch, candidate_sha)
        except Exception as exc:
            moved = False
            update_error = exc

        try:
            after_update_head = self._git.read_branch_head(branch)
        except Exception as exc:
            raise _error(
                "WRITE_OUTCOME_UNKNOWN",
                phase="REF_TRANSITION",
                retry_class=RetryClass.REF.value,
                effect_state="UNKNOWN",
                detail=str(exc),
            ) from exc

        if update_error is not None:
            if after_update_head == candidate_sha:
                return
            reachability = self._candidate_reachability(
                candidate_sha,
                after_update_head,
            )
            if reachability is True:
                raise _error(
                    "POSTWRITE_HEAD_MISMATCH",
                    phase="READBACK",
                    retry_class=RetryClass.READBACK.value,
                    effect_state=ReceiptState.PRESENT_UNVERIFIED.value,
                    detail="candidate became reachable but is no longer lane head",
                ) from update_error
            if reachability is False and after_update_head != expected_head:
                raise _error(
                    "REF_UPDATE_STALE",
                    phase="REF_TRANSITION",
                    retry_class=RetryClass.REF.value,
                    effect_state="NONE_ESTABLISHED",
                ) from update_error
            raise _error(
                "WRITE_OUTCOME_UNKNOWN",
                phase="REF_TRANSITION",
                retry_class=RetryClass.REF.value,
                effect_state="UNKNOWN",
                detail=str(update_error),
            ) from update_error

        if moved:
            return
        if after_update_head == candidate_sha:
            return
        if after_update_head != expected_head:
            raise _error(
                "REF_UPDATE_STALE",
                phase="REF_TRANSITION",
                retry_class=RetryClass.REF.value,
                effect_state="NONE_ESTABLISHED",
            )
        raise _error(
            "REF_UPDATE_REJECTED",
            phase="REF_TRANSITION",
            retry_class=RetryClass.REF.value,
            effect_state="NONE_ESTABLISHED",
        )

    def _candidate_reachability(
        self,
        candidate_sha: str,
        head_sha: str | None,
    ) -> bool | None:
        """Check if candidate is reachable from head (optional backend capability).

        Returns:
          True if candidate is an ancestor of head.
          False if candidate is not an ancestor.
          None if backend does not support reachability queries.
        """
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
        """Handle idempotent re-submission of an already-committed message.

        Verifies that the existing commit's content and metadata match the current
        submission byte-for-byte.
        """
        commit = self._git.read_commit(existing.commit_sha)
        file_record = self._git.read_file_at_commit(
            existing.commit_sha,
            existing.path,
        )
        if (
            commit is None
            or file_record is None
            or len(commit.parent_shas) != 1
            or existing.path not in commit.changed_paths
        ):
            raise _error(
                "RECEIPT_INCOMPLETE",
                phase="READBACK",
                retry_class=RetryClass.READBACK.value,
                effect_state=ReceiptState.PRESENT_UNVERIFIED.value,
            )
        if (
            file_record.content != message_bytes
            or sha256(file_record.content).hexdigest() != message_digest
        ):
            raise _error(
                "POSTWRITE_CONTENT_MISMATCH",
                phase="READBACK",
                retry_class=RetryClass.READBACK.value,
                effect_state=ReceiptState.PRESENT_UNVERIFIED.value,
            )
        if existing.blob_sha and existing.blob_sha != file_record.blob_sha:
            raise _error(
                "RECEIPT_INCOMPLETE",
                phase="READBACK",
                retry_class=RetryClass.READBACK.value,
                effect_state=ReceiptState.PRESENT_UNVERIFIED.value,
                detail="history blob differs from Git readback",
            )
        try:
            readback_parsed = _parse_message(
                file_record.content.decode("utf-8")
            )
        except Exception as exc:
            raise _error(
                "POSTWRITE_METADATA_MISMATCH",
                phase="READBACK",
                retry_class=RetryClass.READBACK.value,
                effect_state=ReceiptState.PRESENT_UNVERIFIED.value,
                detail=str(exc),
            ) from exc
        if readback_parsed != parsed:
            raise _error(
                "POSTWRITE_METADATA_MISMATCH",
                phase="READBACK",
                retry_class=RetryClass.READBACK.value,
                effect_state=ReceiptState.PRESENT_UNVERIFIED.value,
            )

        final_control = self._read_control_after_verified_effect()
        final_binding = final_control.lanes.get(current_binding.identity)
        lane_used = existing.branch or current_binding.branch
        current_lane = (
            final_binding is not None
            and final_binding.branch == lane_used
        )

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
        """Verify that a newly-created commit is correctly placed and matches input.

        Performs full readback and byte-verification of blob, tree, commit shape,
        and metadata.
        """
        try:
            head = self._git.read_branch_head(binding.branch)
        except Exception as exc:
            raise _error(
                "POSTWRITE_HEAD_MISMATCH",
                phase="READBACK",
                retry_class=RetryClass.READBACK.value,
                effect_state=ReceiptState.PRESENT_UNVERIFIED.value,
                detail=str(exc),
            ) from exc
        if head != candidate_sha:
            raise _error(
                "POSTWRITE_HEAD_MISMATCH",
                phase="READBACK",
                retry_class=RetryClass.READBACK.value,
                effect_state=ReceiptState.PRESENT_UNVERIFIED.value,
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
                retry_class=RetryClass.READBACK.value,
                effect_state=ReceiptState.PRESENT_UNVERIFIED.value,
            )
        if commit.changed_paths != (path,):
            raise _error(
                "POSTWRITE_PATH_MISMATCH",
                phase="READBACK",
                retry_class=RetryClass.READBACK.value,
                effect_state=ReceiptState.PRESENT_UNVERIFIED.value,
            )

        file_record = self._git.read_file_at_commit(candidate_sha, path)
        if file_record is None:
            raise _error(
                "POSTWRITE_PATH_MISMATCH",
                phase="READBACK",
                retry_class=RetryClass.READBACK.value,
                effect_state=ReceiptState.PRESENT_UNVERIFIED.value,
            )
        if (
            file_record.content != message_bytes
            or file_record.blob_sha != blob_sha
            or sha256(file_record.content).hexdigest() != message_digest
        ):
            raise _error(
                "POSTWRITE_CONTENT_MISMATCH",
                phase="READBACK",
                retry_class=RetryClass.READBACK.value,
                effect_state=ReceiptState.PRESENT_UNVERIFIED.value,
            )
        try:
            readback_parsed = _parse_message(
                file_record.content.decode("utf-8")
            )
        except Exception as exc:
            raise _error(
                "POSTWRITE_METADATA_MISMATCH",
                phase="READBACK",
                retry_class=RetryClass.READBACK.value,
                effect_state=ReceiptState.PRESENT_UNVERIFIED.value,
                detail=str(exc),
            ) from exc
        if readback_parsed != parsed:
            raise _error(
                "POSTWRITE_METADATA_MISMATCH",
                phase="READBACK",
                retry_class=RetryClass.READBACK.value,
                effect_state=ReceiptState.PRESENT_UNVERIFIED.value,
            )

        final_control = self._read_control_after_verified_effect()
        final_binding = final_control.lanes.get(binding.identity)
        current_lane = (
            final_binding is not None
            and final_binding.branch == binding.branch
        )

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
    "ReceiptState",
    "RetryClass",
    "SafeAppendError",
    "SafeAppendReceipt",
    "SafeLaneAppender",
]
