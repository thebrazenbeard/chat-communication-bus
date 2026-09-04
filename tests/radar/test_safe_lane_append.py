from __future__ import annotations

from hashlib import sha256

import pytest

from radar.safe_lane_append import (
    CommitReadback,
    CommittedMessage,
    ControlSnapshot,
    FileReadback,
    IdentityHistory,
    LaneBinding,
    SafeAppendError,
    SafeLaneAppender,
)


HEAD = "1" * 40
OTHER_HEAD = "2" * 40
CONTROL_SHA = "3" * 40
TOPOLOGY_DIGEST = "4" * 64


def _message(
    *,
    message_id: str = "four-0007",
    writer: str = "Four",
    prev: str | None = "four-0006",
    body: str = "hello",
) -> str:
    headers = [
        "# Four -> Radar",
        "",
        f"message_id: {message_id}",
        f"writer: {writer}",
    ]
    if prev is not None:
        headers.append(f"prev_message_id: {prev}")
    headers.extend(["requires_reply: true", "", body, ""])
    return "\n".join(headers)


def _snapshot(branch: str = "bus/four-v2") -> ControlSnapshot:
    return ControlSnapshot(
        repository="thebrazenbeard/chat-communication-bus",
        control_commit_sha=CONTROL_SHA,
        topology_digest=TOPOLOGY_DIGEST,
        lanes={"four": LaneBinding(identity="four", writer="Four", branch=branch)},
    )


class SequenceControlSource:
    def __init__(self, *snapshots: ControlSnapshot):
        self.snapshots = list(snapshots)
        self.index = 0

    def read(self) -> ControlSnapshot:
        if not self.snapshots:
            raise AssertionError("no control snapshot configured")
        index = min(self.index, len(self.snapshots) - 1)
        self.index += 1
        return self.snapshots[index]


class StaticHistorySource:
    def __init__(self, history: IdentityHistory):
        self.history = history
        self.calls: list[str] = []

    def read_identity(self, identity: str) -> IdentityHistory:
        self.calls.append(identity)
        return self.history


class FakeGit:
    def __init__(self, *, branch: str = "bus/four-v2", head: str = HEAD):
        self.heads = {branch: head}
        self.blobs: dict[str, bytes] = {}
        self.trees: dict[str, tuple[str, str, str]] = {}
        self.commits: dict[str, CommitReadback] = {}
        self.files: dict[tuple[str, str], FileReadback] = {}
        self.created_objects: list[str] = []
        self.before_update = None
        self.corrupt_postwrite_content = False

    def read_branch_head(self, branch: str) -> str | None:
        return self.heads.get(branch)

    def read_file_at_commit(self, commit_sha: str, path: str) -> FileReadback | None:
        record = self.files.get((commit_sha, path))
        if record and self.corrupt_postwrite_content and self.heads.get("bus/four-v2") == commit_sha:
            return FileReadback(blob_sha=record.blob_sha, content=b"corrupt")
        return record

    def read_commit(self, commit_sha: str) -> CommitReadback | None:
        return self.commits.get(commit_sha)

    def create_blob(self, content: bytes) -> str:
        blob_sha = "b" + sha256(content).hexdigest()[:39]
        self.blobs[blob_sha] = content
        self.created_objects.append("blob")
        return blob_sha

    def create_tree(self, base_commit_sha: str, path: str, blob_sha: str) -> str:
        tree_sha = f"t{len(self.trees) + 1:039d}"
        self.trees[tree_sha] = (base_commit_sha, path, blob_sha)
        self.created_objects.append("tree")
        return tree_sha

    def create_commit(self, message: str, tree_sha: str, parent_sha: str) -> str:
        commit_sha = f"c{len(self.commits) + 1:039d}"
        base_commit_sha, path, blob_sha = self.trees[tree_sha]
        assert base_commit_sha == parent_sha
        self.commits[commit_sha] = CommitReadback(
            parent_shas=(parent_sha,),
            tree_sha=tree_sha,
            changed_paths=(path,),
        )
        self.files[(commit_sha, path)] = FileReadback(
            blob_sha=blob_sha,
            content=self.blobs[blob_sha],
        )
        self.created_objects.append("commit")
        return commit_sha

    def update_ref_non_force(self, branch: str, candidate_sha: str) -> bool:
        if self.before_update is not None:
            self.before_update(self, branch, candidate_sha)
        parent = self.commits[candidate_sha].parent_shas[0]
        if self.heads.get(branch) != parent:
            return False
        self.heads[branch] = candidate_sha
        return True


def _history(
    *,
    complete: bool = True,
    tip: tuple[str, ...] = ("four-0006",),
    messages: tuple[CommittedMessage, ...] = (),
) -> IdentityHistory:
    if not messages and tip == ("four-0006",):
        messages = (
            CommittedMessage(
                message_id="four-0006",
                message_sha256="a" * 64,
                commit_sha="9" * 40,
                path="messages/0006-four-old.md",
                blob_sha="8" * 40,
                prev_message_id="four-0005",
            ),
        )
    return IdentityHistory(complete=complete, tip_message_ids=tip, messages=messages)


def _appender(
    *,
    controls: SequenceControlSource | None = None,
    history: IdentityHistory | None = None,
    git: FakeGit | None = None,
) -> tuple[SafeLaneAppender, FakeGit]:
    backend = git or FakeGit()
    appender = SafeLaneAppender(
        control_source=controls or SequenceControlSource(_snapshot()),
        history_source=StaticHistorySource(history or _history()),
        git_backend=backend,
    )
    return appender, backend


def test_success_is_topology_bound_parent_bound_and_exactly_read_back():
    appender, git = _appender()
    text = _message()

    receipt = appender.append_bus_message_v1("four", HEAD, text)

    assert receipt.schema == "RADAR_SAFE_LANE_APPEND_RECEIPT_V1"
    assert receipt.result == "APPENDED"
    assert receipt.identity == "four"
    assert receipt.derived_writer == "Four"
    assert receipt.asserted_writer == "Four"
    assert receipt.lane_ref == "bus/four-v2"
    assert receipt.expected_lane_head == HEAD
    assert receipt.commit_parent_sha == HEAD
    assert receipt.path == "messages/four-0007.md"
    assert receipt.message_id == "four-0007"
    assert receipt.prev_message_id == "four-0006"
    assert receipt.readback_verified is True
    assert receipt.current_lane_after_readback is True
    assert receipt.projection_state == "NOT_ESTABLISHED"
    assert receipt.delivery_state == "NOT_ESTABLISHED"
    assert receipt.incorporation_state == "NOT_ESTABLISHED"
    assert git.heads["bus/four-v2"] == receipt.commit_sha
    assert git.created_objects == ["blob", "tree", "commit"]


def test_stale_expected_head_fails_before_object_creation():
    appender, git = _appender()

    with pytest.raises(SafeAppendError) as exc:
        appender.append_bus_message_v1("four", OTHER_HEAD, _message())

    assert exc.value.code == "STALE_LANE_HEAD"
    assert exc.value.effect_state == "NONE_ESTABLISHED"
    assert git.created_objects == []


def test_writer_mismatch_is_rejected_before_write():
    appender, git = _appender()

    with pytest.raises(SafeAppendError) as exc:
        appender.append_bus_message_v1("four", HEAD, _message(writer="Seven"))

    assert exc.value.code == "WRITER_MISMATCH"
    assert git.created_objects == []


def test_predecessor_mismatch_is_rejected_across_lane_generations():
    appender, git = _appender()

    with pytest.raises(SafeAppendError) as exc:
        appender.append_bus_message_v1("four", HEAD, _message(prev="four-0005"))

    assert exc.value.code == "PREDECESSOR_MISMATCH"
    assert git.created_objects == []


def test_incomplete_identity_history_fails_closed():
    appender, git = _appender(history=_history(complete=False))

    with pytest.raises(SafeAppendError) as exc:
        appender.append_bus_message_v1("four", HEAD, _message())

    assert exc.value.code == "MESSAGE_ID_HISTORY_UNRESOLVED"
    assert git.created_objects == []


def test_duplicate_id_with_different_bytes_is_collision():
    existing = CommittedMessage(
        message_id="four-0007",
        message_sha256="0" * 64,
        commit_sha="7" * 40,
        path="messages/four-0007.md",
        blob_sha="6" * 40,
        prev_message_id="four-0006",
    )
    appender, git = _appender(history=_history(tip=("four-0007",), messages=(existing,)))

    with pytest.raises(SafeAppendError) as exc:
        appender.append_bus_message_v1("four", HEAD, _message())

    assert exc.value.code == "MESSAGE_ID_COLLISION"
    assert git.created_objects == []


def test_duplicate_id_with_identical_bytes_returns_verified_already_committed():
    text = _message()
    digest = sha256(text.encode("utf-8")).hexdigest()
    existing = CommittedMessage(
        message_id="four-0007",
        message_sha256=digest,
        commit_sha="7" * 40,
        path="messages/four-0007.md",
        blob_sha="6" * 40,
        prev_message_id="four-0006",
    )
    git = FakeGit()
    git.commits[existing.commit_sha] = CommitReadback(
        parent_shas=("5" * 40,),
        tree_sha="4" * 40,
        changed_paths=(existing.path,),
    )
    git.files[(existing.commit_sha, existing.path)] = FileReadback(
        blob_sha=existing.blob_sha,
        content=text.encode("utf-8"),
    )
    appender, git = _appender(
        history=_history(tip=("four-0007",), messages=(existing,)),
        git=git,
    )

    receipt = appender.append_bus_message_v1("four", HEAD, text)

    assert receipt.result == "ALREADY_COMMITTED"
    assert receipt.commit_sha == existing.commit_sha
    assert receipt.readback_verified is True
    assert git.created_objects == []


def test_topology_change_before_ref_move_aborts_with_only_orphan_objects():
    changed = _snapshot(branch="bus/four-v3")
    controls = SequenceControlSource(_snapshot(), changed)
    appender, git = _appender(controls=controls)

    with pytest.raises(SafeAppendError) as exc:
        appender.append_bus_message_v1("four", HEAD, _message())

    assert exc.value.code == "TOPOLOGY_CHANGED_DURING_APPEND"
    assert exc.value.effect_state == "NONE_ESTABLISHED"
    assert git.heads["bus/four-v2"] == HEAD
    assert git.created_objects == ["blob", "tree", "commit"]


def test_non_force_ref_race_fails_stale_instead_of_rebasing():
    appender, git = _appender()

    def advance(backend: FakeGit, branch: str, candidate_sha: str) -> None:
        backend.heads[branch] = OTHER_HEAD

    git.before_update = advance

    with pytest.raises(SafeAppendError) as exc:
        appender.append_bus_message_v1("four", HEAD, _message())

    assert exc.value.code == "REF_UPDATE_STALE"
    assert exc.value.effect_state == "NONE_ESTABLISHED"
    assert git.heads["bus/four-v2"] == OTHER_HEAD


def test_message_id_cannot_escape_deterministic_messages_path():
    appender, git = _appender()

    with pytest.raises(SafeAppendError) as exc:
        appender.append_bus_message_v1(
            "four",
            HEAD,
            _message(message_id="four-../../README"),
        )

    assert exc.value.code == "MESSAGE_ID_INVALID"
    assert git.created_objects == []


def test_postwrite_content_mismatch_is_present_but_unverified():
    appender, git = _appender()
    git.corrupt_postwrite_content = True

    with pytest.raises(SafeAppendError) as exc:
        appender.append_bus_message_v1("four", HEAD, _message())

    assert exc.value.code == "POSTWRITE_CONTENT_MISMATCH"
    assert exc.value.effect_state == "PRESENT_UNVERIFIED"
    assert git.heads["bus/four-v2"] != HEAD


def test_topology_move_after_verified_append_is_reported_not_erased():
    changed = _snapshot(branch="bus/four-v3")
    controls = SequenceControlSource(_snapshot(), _snapshot(), changed)
    appender, git = _appender(controls=controls)

    receipt = appender.append_bus_message_v1("four", HEAD, _message())

    assert receipt.result == "APPENDED"
    assert receipt.readback_verified is True
    assert receipt.current_lane_after_readback is False
    assert git.heads["bus/four-v2"] == receipt.commit_sha
