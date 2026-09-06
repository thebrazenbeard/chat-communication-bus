from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKOUT_SHA = "3d3c42e5aac5ba805825da76410c181273ba90b1"
SETUP_PYTHON_SHA = "5fda3b95a4ea91299a34e894583c3862153e4b97"
OLD_CHECKOUT_SHA = "11d5960a326750d5838078e36cf38b85af677262"
OLD_SETUP_PYTHON_SHA = "a26af69be951a213d495a4c3e4e4022e16d87065"


def _assert_node24_native_control_pins(workflow: str) -> None:
    assert OLD_CHECKOUT_SHA not in workflow
    assert OLD_SETUP_PYTHON_SHA not in workflow
    assert "actions/checkout@v" not in workflow
    assert "actions/setup-python@v" not in workflow


def test_writer_lane_guard_pins_node24_native_actions_by_immutable_sha():
    workflow = (ROOT / ".github" / "workflows" / "writer-lane-guard.yml").read_text()

    _assert_node24_native_control_pins(workflow)
    assert workflow.count(f"actions/checkout@{CHECKOUT_SHA}") == 2
    assert f"actions/setup-python@{SETUP_PYTHON_SHA}" in workflow
    assert workflow.count("persist-credentials: false") == 2


def test_ci_pins_node24_native_actions_and_does_not_persist_checkout_credentials():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()

    _assert_node24_native_control_pins(workflow)
    assert workflow.count(f"actions/checkout@{CHECKOUT_SHA}") == 3
    assert f"actions/setup-python@{SETUP_PYTHON_SHA}" in workflow
    assert workflow.count("persist-credentials: false") == 3


def test_trusted_projector_uses_node24_native_control_actions_only():
    workflow = (ROOT / ".github" / "workflows" / "radar-trusted-projector.yml").read_text()

    _assert_node24_native_control_pins(workflow)
    assert workflow.count(f"actions/checkout@{CHECKOUT_SHA}") == 2
    assert f"actions/setup-python@{SETUP_PYTHON_SHA}" in workflow
    assert workflow.count("persist-credentials: false") == 2
