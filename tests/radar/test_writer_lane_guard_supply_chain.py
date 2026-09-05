from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_writer_lane_guard_pins_third_party_actions_by_immutable_sha():
    workflow = (ROOT / ".github" / "workflows" / "writer-lane-guard.yml").read_text()

    assert "actions/checkout@v4" not in workflow
    assert "actions/setup-python@v5" not in workflow
    assert workflow.count("actions/checkout@11d5960a326750d5838078e36cf38b85af677262") == 2
    assert "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065" in workflow
