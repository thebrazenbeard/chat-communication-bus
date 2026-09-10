from __future__ import annotations

from types import SimpleNamespace

import pytest

from radar.branch_bound_append import BranchBindingError, BranchBoundSafeLaneAppender


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
