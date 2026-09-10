from __future__ import annotations

from types import SimpleNamespace

import pytest

from radar.branch_bound_append import BranchBindingError, BranchBoundSafeLaneAppender
from radar.safe_lane_append import (
    CommittedMessage,
    ControlSnapshot,
    IdentityHistory,
    LaneBinding,
)


HEAD = "1" * 40


class Control:
    def __init__(self, *branches: str) -> None:
        self.branches = list(branches)
        self.calls = 0

    def read(self):
        branch = self.branches[min(self.calls, len(self.branches) - 1)]
        self.calls += 1
        return SimpleNamespace(
            lanes={"four": SimpleNamespace(branch=branch)}
        )


class FakeGit:
    def __init__(self) -> None:
        self.delegate_effects = 0


class Delegate:
    def __init__(self, *, control_source, history_source, git_backend) -> None:
        self.control = control_source
        self.git = git_backend

    def append_bus_message_v1(self, identity, expected_lane_head, message_utf8):
        # Mirror the lower-level appender's preflight + before-ref topology reads.
        self.control.read()
        self.control.read()
        self.git.delegate_effects += 1
        return "ok"


class ProductionControl:
    def __init__(self, *branches: str) -> None:
        self.branches = list(branches)
        self.calls = 0

    def read(self) -> ControlSnapshot:
        branch = self.branches[min(self.calls, len(self.branches) - 1)]
        self.calls += 1
        return ControlSnapshot(
            repository="thebrazenbeard/chat-communication-bus",
            control_commit_sha="2" * 40,
            topology_digest="3" * 64,
            lanes={
                "four": LaneBinding(
                    identity="four",
                    writer="Four",
                    branch=branch,
                )
            },
        )


class ProductionHistory:
    def read_identity(self, identity: str) -> IdentityHistory:
        assert identity == "four"
        return IdentityHistory(
            complete=True,
            tip_message_ids=("four-old",),
            messages=(
                CommittedMessage(
                    message_id="four-old",
                    message_sha256="4" * 64,
                    commit_sha="5" * 40,
                    path="messages/four-old.md",
                    blob_sha="6" * 40,
                    prev_message_id=None,
                    branch="bus/four-v2",
                ),
            ),
        )


class ProductionGit:
    def __init__(self) -> None:
        self.created_objects: list[str] = []
        self.ref_updates = 0

    def read_branch_head(self, branch: str) -> str | None:
        return HEAD if branch == "bus/four-v2" else None

    def read_file_at_commit(self, commit_sha: str, path: str):
        return None

    def create_blob(self, content: bytes) -> str:
        self.created_objects.append("blob")
        return "a" * 40

    def create_tree(self, base_commit_sha: str, path: str, blob_sha: str) -> str:
        self.created_objects.append("tree")
        return "b" * 40

    def create_commit(self, message: str, tree_sha: str, parent_sha: str) -> str:
        self.created_objects.append("commit")
        return "c" * 40

    def update_ref_non_force(self, branch: str, candidate_sha: str) -> bool:
        self.ref_updates += 1
        raise AssertionError("branch mismatch must fail before ref update")


def _message(*, branch: str | None = "bus/four-v2") -> str:
    headers = [
        "# Four -> Radar",
        "",
        "message_id: four-branch-bound-test",
        "writer: Four",
    ]
    if branch is not None:
        headers.append(f"writer_branch: {branch}")
    headers.extend(
        [
            "prev_message_id: four-old",
            "requires_reply: false",
            "",
            "body",
            "",
        ]
    )
    return "\n".join(headers)


def _appender(control: Control) -> tuple[BranchBoundSafeLaneAppender, FakeGit]:
    git = FakeGit()
    return (
        BranchBoundSafeLaneAppender(
            control_source=control,
            history_source=object(),
            git_backend=git,
            delegate_factory=Delegate,
        ),
        git,
    )


def _production_appender(
    control: ProductionControl,
) -> tuple[BranchBoundSafeLaneAppender, ProductionGit]:
    git = ProductionGit()
    return (
        BranchBoundSafeLaneAppender(
            control_source=control,
            history_source=ProductionHistory(),
            git_backend=git,
        ),
        git,
    )


def test_matching_declared_branch_delegates_and_rechecks_topology():
    appender, git = _appender(Control("bus/four-v2"))
    assert appender.append_bus_message_v1("four", HEAD, _message()) == "ok"
    assert git.delegate_effects == 1


def test_wrong_target_main_is_rejected_before_delegate_effect():
    appender, git = _appender(Control("bus/four-v2"))
    with pytest.raises(BranchBindingError, match="WRITER_BRANCH_MISMATCH"):
        appender.append_bus_message_v1(
            "four",
            HEAD,
            _message(branch="main"),
        )
    assert git.delegate_effects == 0


def test_missing_writer_branch_is_rejected_before_control_or_delegate():
    control = Control("bus/four-v2")
    appender, git = _appender(control)
    with pytest.raises(BranchBindingError, match="WRITER_BRANCH_MISSING"):
        appender.append_bus_message_v1(
            "four",
            HEAD,
            _message(branch=None),
        )
    assert control.calls == 0
    assert git.delegate_effects == 0


def test_topology_retarget_between_reads_fails_before_ref_stage_effect():
    appender, git = _appender(Control("bus/four-v2", "bus/four-v3"))
    with pytest.raises(BranchBindingError, match="WRITER_BRANCH_MISMATCH"):
        appender.append_bus_message_v1("four", HEAD, _message())
    assert git.delegate_effects == 0


def test_body_writer_branch_text_cannot_authenticate_missing_header():
    text = (
        "# Four -> Radar\n\n"
        "message_id: four-branch-bound-test\n"
        "writer: Four\n"
        "prev_message_id: four-old\n\n"
        "writer_branch: bus/four-v2\n"
    )
    control = Control("bus/four-v2")
    appender, git = _appender(control)
    with pytest.raises(BranchBindingError, match="WRITER_BRANCH_MISSING"):
        appender.append_bus_message_v1("four", HEAD, text)
    assert control.calls == 0
    assert git.delegate_effects == 0


def test_real_safe_lane_appender_preserves_preflight_branch_mismatch_taxonomy():
    appender, git = _production_appender(ProductionControl("bus/four-v2"))

    with pytest.raises(BranchBindingError) as exc:
        appender.append_bus_message_v1("four", HEAD, _message(branch="main"))

    assert exc.value.code == "WRITER_BRANCH_MISMATCH"
    assert git.created_objects == []
    assert git.ref_updates == 0


def test_real_safe_lane_appender_preserves_second_read_branch_mismatch_taxonomy():
    appender, git = _production_appender(
        ProductionControl("bus/four-v2", "bus/four-v3")
    )

    with pytest.raises(BranchBindingError) as exc:
        appender.append_bus_message_v1("four", HEAD, _message())

    assert exc.value.code == "WRITER_BRANCH_MISMATCH"
    assert git.created_objects == ["blob", "tree", "commit"]
    assert git.ref_updates == 0
