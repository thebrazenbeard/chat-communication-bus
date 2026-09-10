import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "projects" / "selfimage" / "blender-relay"
WORKFLOW = ROOT / ".github" / "workflows" / "selfimage-blender-relay.yml"
WORKFLOW_DIR = ROOT / ".github" / "workflows"
CHECKOUT_PIN = "actions/checkout@11d5960a326750d5838078e36cf38b85af677262"
UPLOAD_PIN = "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"


def selfimage_workflows():
    return sorted(WORKFLOW_DIR.glob("selfimage-*.yml"))


def test_request_schema_is_strict_and_has_no_arbitrary_execution_operation():
    schema = json.loads((BASE / "schema" / "request.schema.json").read_text(encoding="utf-8"))
    assert schema["additionalProperties"] is False
    ops = schema["properties"]["operation"]["enum"]
    assert "execute_code" not in ops
    assert "shell" not in ops
    assert "run_command" not in ops
    assert "import_exact_cc0" in ops
    assert "viewport_capture" in ops
    assert "scene_audit_v1" in ops


def test_workflow_never_runs_on_pull_request_and_is_bound_to_private_relay_lane():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "pull_request:" not in text
    assert "feature/selfimage-blender-relay-v1" in text
    assert "projects/selfimage/blender-relay/requests/**" in text
    assert "github.actor == 'thebrazenbeard'" in text
    assert "runs-on: [self-hosted, windows, x64, vera-blender]" in text


def test_relay_uses_windows_powershell_without_pwsh_only_json_flags():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    process = (BASE / "relay" / "Process-PendingRequests.ps1").read_text(encoding="utf-8")
    relay = (BASE / "relay" / "Invoke-BlenderRelay.ps1").read_text(encoding="utf-8")
    assert "shell: pwsh" not in workflow
    assert workflow.count("shell: powershell") >= 3
    assert "ConvertFrom-Json -Depth" not in process
    assert "ConvertFrom-Json -Depth" not in relay


def test_selfhosted_workflows_pin_external_actions_and_exact_event_source():
    workflows = selfimage_workflows()
    assert workflows
    for path in workflows:
        text = path.read_text(encoding="utf-8")
        assert "actions/checkout@v4" not in text, path.name
        assert "actions/upload-artifact@v4" not in text, path.name
        if "actions/checkout@" in text:
            assert CHECKOUT_PIN in text, path.name
            assert "ref: ${{ github.sha }}" in text, path.name
            assert "persist-credentials: false" in text, path.name
            assert "ref: feature/selfimage-blender-relay-v1" not in text, path.name
        if "actions/upload-artifact@" in text:
            assert UPLOAD_PIN in text, path.name


def test_relay_does_not_refresh_mutable_branch_tip_before_processing():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "Refresh relay branch tip" not in workflow
    assert "git pull --ff-only origin '${{ github.ref_name }}'" not in workflow
    assert "ref: ${{ github.sha }}" in workflow
    assert "persist-credentials: false" in workflow


def test_outer_processor_preserves_detailed_failure_receipts_and_version_identity():
    process = (BASE / "relay" / "Process-PendingRequests.ps1").read_text(encoding="utf-8")
    relay = (BASE / "relay" / "Invoke-BlenderRelay.ps1").read_text(encoding="utf-8")
    assert "$resultPath = $null" in process
    assert "Test-Path -LiteralPath $resultPath" in process
    assert "preserving that receipt" in process
    assert "$RelayVersion = '1.1.2'" in relay
    assert "relay_version = '1.1.2'" in process
    assert "relay_version = '1.1.1'" not in process


def test_relay_pins_exact_cc0_transport_and_rejects_unlisted_operations():
    text = (BASE / "relay" / "Invoke-BlenderRelay.ps1").read_text(encoding="utf-8")
    assert "09b0e4af53d3e9436be5e37d9aefa3c5e882b272" in text
    assert "1644424" in text
    assert "835d2bf3b55f7e7249bc8fbaa98f40d51e88c7fde55653884d67e6bdd658c8e0" in text
    assert "df189d7ff267ab47fd6069232395401391399868" in text
    assert "Operation '$operation' is not allowlisted." in text
    assert "import_exact_cc0 refuses a non-default/non-empty scene." in text


def test_approved_scene_audit_is_named_and_request_cannot_supply_python_source():
    relay = (BASE / "relay" / "Invoke-BlenderRelay.ps1").read_text(encoding="utf-8")
    audit = BASE / "approved-scripts" / "selfimage_blender_scene_audit_v1.py"
    assert audit.exists()
    assert "scene_audit_v1" in relay
    assert "selfimage_blender_scene_audit_v1.py" in relay
    assert "No filesystem, network, subprocess" in audit.read_text(encoding="utf-8")
    schema = json.loads((BASE / "schema" / "request.schema.json").read_text(encoding="utf-8"))
    assert set(schema["properties"]) == {"version", "request_id", "operation", "args", "created_at"}


def test_results_do_not_retrigger_request_path():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "projects/selfimage/blender-relay/results" in text
    path_block = text.split("paths:", 1)[1].split("workflow_dispatch:", 1)[0]
    assert "results" not in path_block


def test_windows_installer_does_not_depend_on_gh_jq_shell_quoting():
    installer = (BASE / "installer" / "Install-VeraBlenderRunner.ps1").read_text(encoding="utf-8")
    uninstaller = (BASE / "installer" / "Uninstall-VeraBlenderRunner.ps1").read_text(encoding="utf-8")
    assert "--jq" not in installer
    assert "--jq" not in uninstaller
    assert "ConvertFrom-Json" in installer
    assert "ConvertFrom-Json" in uninstaller
    assert "visibility -ne 'PRIVATE'" in installer
    assert "actions/runners/registration-token" in installer
    assert "actions/runners/remove-token" in uninstaller
