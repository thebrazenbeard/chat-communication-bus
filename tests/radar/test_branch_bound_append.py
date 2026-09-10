from __future__ import annotations

from types import SimpleNamespace

import pytest

from radar.branch_bound_append import BranchBindingError, BranchBoundSafeLaneAppender
from radar.safe_lane_append import (
    CommitReadback,
    CommittedMessage,
    ControlSnapshot,
    FileReadback,
    IdentityHistory,
    LaneBinding,
    SafeAppendError,
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
    def __init__(self, *, allow_ref_update: bool = False) -> None:
        self.created_objects: list[str] = []
        self.ref_updates = 0
        self.allow_ref_update = allow_ref_update
        self.current_head = HEAD
        self.blobs: dict[str, bytes] = {}
        self.trees: dict[str, tuple[str, str, str]] = {}
        self.commits: dict[str, CommitReadback] = {}
        self.files: dict[tuple[str, str], FileReadback] = {}

    def read_branch_head(self, branch: str) -> str | None:
        return self.current_head if branch == "bus/four-v2" else None

    def read_file_at_commit(self, commit_sha: str, path: str):
        return self.files.get((commit_sha, path))

    def read_commit(self, commit_sha: str):
        return self.commits.get(commit_sha)

    def create_blob(self, content: bytes) -> str:
        self.created_objects.append("blob")
        blob_sha = "a" * 40
        self.blobs[blob_sha] = content
        return blob_sha

    def create_tree(self, base_commit_sha: str, path: str, blob_sha: str) -> str:
        self.created_objects.append("tree")
        tree_sha = "b" * 40
        self.trees[tree_sha] = (base_commit_sha, path, blob_sha)
        return tree_sha

    def create_commit(self, message: str, tree_sha: str, parent_sha: str) -> str:
        self.created_objects.append("commit")
        commit_sha = "c" * 40
        _, path, blob_sha = self.trees[tree_sha]
        self.commits[commit_sha] = CommitReadback(
            parent_shas=(parent_sha,),
            tree_sha=tree_sha,
            changed_paths=(path,),
        )
        self.files[(commit_sha, path)] = FileReadback(
            blob_sha=blob_sha,
            content=self.blobs[blob_sha],
        )
        return commit_sha

    def update_ref_non_force(self, branch: str, candidate_sha: str) -> bool:
        self.ref_updates += 1
        if not self.allow_ref_update:
            raise AssertionError("branch mismatch must fail before ref update")
        self.current_head = candidate_sha
        return True


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
    *,
    allow_ref_update: bool = False,
) -> tuple[BranchBoundSafeLaneAppender, ProductionGit]:
    git = ProductionGit(allow_ref_update=allow_ref_update)
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


def test_postwrite_branch_mismatch_preserves_verified_effect_state():
    appender, git = _production_appender(
        ProductionControl("bus/four-v2", "bus/four-v2", "bus/four-v3"),
        allow_ref_update=True,
    )

    with pytest.raises(SafeAppendError) as exc:
        appender.append_bus_message_v1("four", HEAD, _message())

    assert exc.value.code == "RECEIPT_INCOMPLETE"
    assert exc.value.effect_state == "PRESENT_VERIFIED"
    assert isinstance(exc.value.__cause__, BranchBindingError)
    assert exc.value.__cause__.code == "WRITER_BRANCH_MISMATCH"
    assert git.ref_updates == 1
    assert git.current_head == "c" * 40
