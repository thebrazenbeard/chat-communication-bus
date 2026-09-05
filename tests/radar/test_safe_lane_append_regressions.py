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


class StaticHistorySource:
    def __init__(self, history: IdentityHistory):
        self.history = history

    def read_identity(self, identity: str) -> IdentityHistory:
        return self.history


class ExistingEffectGit:
    def __init__(self, *, branch: str, message: CommittedMessage, content: bytes):
        self.branch = branch
        self.head = HEAD
        self.message = message
        self.content = content

    def read_branch_head(self, branch: str) -> str | None:
        return self.head if branch == self.branch else None

    def read_file_at_commit(self, commit_sha: str, path: str) -> FileReadback | None:
        if commit_sha == self.message.commit_sha and path == self.message.path:
            return FileReadback(blob_sha=self.message.blob_sha, content=self.content)
        return None

    def read_commit(self, commit_sha: str) -> CommitReadback | None:
        if commit_sha == self.message.commit_sha:
            return CommitReadback(
                parent_shas=("5" * 40,),
                tree_sha="4" * 40,
                changed_paths=(self.message.path,),
            )
        return None

    def create_blob(self, content: bytes) -> str:
        raise AssertionError("idempotent recovery must not create objects")

    def create_tree(self, base_commit_sha: str, path: str, blob_sha: str) -> str:
        raise AssertionError("idempotent recovery must not create objects")

    def create_commit(self, message: str, tree_sha: str, parent_sha: str) -> str:
        raise AssertionError("idempotent recovery must not create objects")

    def update_ref_non_force(self, branch: str, candidate_sha: str) -> bool:
        raise AssertionError("idempotent recovery must not move refs")


class SequenceControl:
    def __init__(self, *items):
        self.items = list(items)
        self.index = 0

    def read(self) -> ControlSnapshot:
        item = self.items[min(self.index, len(self.items) - 1)]
        self.index += 1
        if isinstance(item, Exception):
            raise item
        return item


def test_hyphenated_identity_idempotent_readback_uses_logical_identity_not_prefix_split():
    text = (
        "# Five-Five -> Radar\n\n"
        "message_id: five-five-0009\n"
        "writer: Five-Five\n"
        "prev_message_id: five-five-0008\n"
        "requires_reply: true\n\nhello\n"
    )
    content = text.encode("utf-8")
    existing = CommittedMessage(
        message_id="five-five-0009",
        message_sha256=sha256(content).hexdigest(),
        commit_sha="7" * 40,
        path="messages/five-five-0009.md",
        blob_sha="6" * 40,
        prev_message_id="five-five-0008",
        branch="bus/five-five-v2",
    )
    snapshot = ControlSnapshot(
        repository="thebrazenbeard/chat-communication-bus",
        control_commit_sha="3" * 40,
        topology_digest="4" * 64,
        lanes={
            "five-five": LaneBinding(
                identity="five-five",
                writer="Five-Five",
                branch="bus/five-five-v2",
            )
        },
    )
    appender = SafeLaneAppender(
        control_source=SequenceControl(snapshot),
        history_source=StaticHistorySource(
            IdentityHistory(
                complete=True,
                tip_message_ids=("five-five-0009",),
                messages=(existing,),
            )
        ),
        git_backend=ExistingEffectGit(
            branch="bus/five-five-v2",
            message=existing,
            content=content,
        ),
    )

    receipt = appender.append_bus_message_v1("five-five", HEAD, text)

    assert receipt.result == "ALREADY_COMMITTED"
    assert receipt.identity == "five-five"
    assert receipt.current_lane_after_readback is True


def test_postwrite_control_unavailable_does_not_turn_unknown_currentness_into_false():
    # Reuse the primary suite's behavior shape with a tiny write-capable fake.
    from tests.radar.test_safe_lane_append import FakeGit, _history, _message, _snapshot

    controls = SequenceControl(_snapshot(), _snapshot(), RuntimeError("control unavailable"))
    git = FakeGit()
    appender = SafeLaneAppender(
        control_source=controls,
        history_source=StaticHistorySource(_history()),
        git_backend=git,
    )

    with pytest.raises(SafeAppendError) as exc:
        appender.append_bus_message_v1("four", HEAD, _message())

    assert exc.value.code == "RECEIPT_INCOMPLETE"
    assert exc.value.effect_state == "PRESENT_VERIFIED"
    assert git.heads["bus/four-v2"] != HEAD
