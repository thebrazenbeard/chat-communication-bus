from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKOUT_SHA = "11d5960a326750d5838078e36cf38b85af677262"
SETUP_PYTHON_SHA = "a26af69be951a213d495a4c3e4e4022e16d87065"


def test_writer_lane_guard_pins_third_party_actions_by_immutable_sha():
    workflow = (ROOT / ".github" / "workflows" / "writer-lane-guard.yml").read_text()

    assert "actions/checkout@v4" not in workflow
    assert "actions/setup-python@v5" not in workflow
    assert workflow.count(f"actions/checkout@{CHECKOUT_SHA}") == 2
    assert f"actions/setup-python@{SETUP_PYTHON_SHA}" in workflow
    assert workflow.count("persist-credentials: false") == 2


def test_ci_pins_third_party_actions_and_does_not_persist_checkout_credentials():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()

    assert "actions/checkout@v4" not in workflow
    assert "actions/setup-python@v5" not in workflow
    assert f"actions/checkout@{CHECKOUT_SHA}" in workflow
    assert f"actions/setup-python@{SETUP_PYTHON_SHA}" in workflow
    assert "persist-credentials: false" in workflow
