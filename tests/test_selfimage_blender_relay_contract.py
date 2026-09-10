import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "projects" / "selfimage" / "blender-relay"
WORKFLOW = ROOT / ".github" / "workflows" / "selfimage-blender-relay.yml"
WORKFLOW_DIR = ROOT / ".github" / "workflows"
CHECKOUT_PIN = "actions/checkout@11d5960a326750d5838078e36cf38b85af677262"
UPLOAD_PIN = "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"
DOWNLOAD_PIN = "actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093"
RUNNER_SHA256 = "1150692afa94e71f872017e254ea55b6eece1eece3fe7e3a6d4c93d0a1b85cfc"


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
        assert "actions/download-artifact@v4" not in text, path.name
        if "actions/checkout@" in text:
            assert CHECKOUT_PIN in text, path.name
            assert "ref: ${{ github.sha }}" in text, path.name
            assert "persist-credentials: false" in text, path.name
            assert "ref: feature/selfimage-blender-relay-v1" not in text, path.name
        if "actions/upload-artifact@" in text:
            assert UPLOAD_PIN in text, path.name
        if "actions/download-artifact@" in text:
            assert DOWNLOAD_PIN in text, path.name


def test_all_standalone_blender_studies_emit_exact_source_provenance():
    study_names = (
        "selfimage-proportion-study-v1.yml",
        "selfimage-proportion-study-v2.yml",
        "selfimage-proportion-study-v3.yml",
        "selfimage-thorax-correction-study-v3.yml",
        "selfimage-thorax-correction-study-v3r2.yml",
        "selfimage-thorax-v3r2-clean-evidence.yml",
        "selfimage-thorax-v3r3-breast-signal-sweep.yml",
        "selfimage-v4lb1-posterior-largeform-sweep.yml",
    )
    for name in study_names:
        text = (WORKFLOW_DIR / name).read_text(encoding="utf-8")
        assert "source_commit" in text, name
        assert "source_tree" in text, name
        assert "rev-parse 'HEAD^{tree}'" in text, name


def test_relay_does_not_refresh_mutable_branch_tip_before_processing():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "Refresh relay branch tip" not in workflow
    assert "git pull --ff-only origin '${{ github.ref_name }}'" not in workflow
    assert "ref: ${{ github.sha }}" in workflow
    assert "persist-credentials: false" in workflow
    process_pos = workflow.index("Process pending Blender requests")
    publish_job_pos = workflow.index("publish_receipts:")
    token_pos = workflow.index("GH_TOKEN: ${{ github.token }}")
    assert process_pos < publish_job_pos < token_pos


def test_blender_execution_job_is_read_only_and_write_token_isolated_to_publisher():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "permissions:\n  contents: read" in workflow
    relay_block = workflow.split("  relay:\n", 1)[1].split("  publish_receipts:\n", 1)[0]
    publisher_block = workflow.split("  publish_receipts:\n", 1)[1]
    assert "contents: write" not in relay_block
    assert "GH_TOKEN: ${{ github.token }}" not in relay_block
    assert "Process pending Blender requests" in relay_block
    assert "permissions:\n      contents: write" in publisher_block
    assert "GH_TOKEN: ${{ github.token }}" in publisher_block
    assert "Process pending Blender requests" not in publisher_block
    assert DOWNLOAD_PIN in publisher_block
    assert "Validate and overlay receipt-only payload" in publisher_block
    assert "Unexpected receipt filename" in publisher_block
    assert "Receipt is not valid JSON" in publisher_block


def test_relay_receipts_bind_executed_commit_tree_and_version_identity():
    process = (BASE / "relay" / "Process-PendingRequests.ps1").read_text(encoding="utf-8")
    relay = (BASE / "relay" / "Invoke-BlenderRelay.ps1").read_text(encoding="utf-8")
    assert "$resultPath = $null" in process
    assert "Test-Path -LiteralPath $resultPath" in process
    assert "preserving that receipt" in process
    assert "$RelayVersion = '1.1.2'" in relay
    assert "relay_version = '1.1.2'" in process
    assert "relay_version = '1.1.1'" not in process
    assert "source_commit" in process
    assert "source_tree" in process
    assert "rev-parse HEAD" in process
    assert "rev-parse 'HEAD^{tree}'" in process


def test_recovery_workflows_require_explicit_bounded_cross_repo_token():
    for name in ("selfimage-aug18-exact-recovery.yml", "selfimage-reference-recovery.yml"):
        text = (WORKFLOW_DIR / name).read_text(encoding="utf-8")
        assert "GH_TOKEN: ${{ secrets.SELFIMAGE_READ_TOKEN }}" in text
        assert "refusing ambient local gh authentication" in text
        assert "gh auth" not in text


def test_runner_bootstrap_is_pinned_ephemeral_and_low_privilege():
    installer = (BASE / "installer" / "Install-VeraBlenderRunner.ps1").read_text(encoding="utf-8")
    assert "$RequiredWindowsAccount = 'vera-blender-runner'" in installer
    assert "WindowsBuiltInRole]::Administrator" in installer
    assert "$RunnerVersion = '2.337.0'" in installer
    assert "actions-runner-win-x64-2.337.0.zip" in installer
    assert RUNNER_SHA256 in installer
    assert "$RunnerAssetBytes = 103528051" in installer
    assert "releases/latest" not in installer
    assert "winget" not in installer
    assert "gh auth login" not in installer
    assert "GITHUB_RUNNER_ADMIN_TOKEN" in installer
    assert "$env:GITHUB_RUNNER_ADMIN_TOKEN = $null" in installer


def test_runner_uninstaller_uses_only_process_scoped_admin_authority():
    uninstaller = (BASE / "installer" / "Uninstall-VeraBlenderRunner.ps1").read_text(encoding="utf-8")
    assert "$RequiredWindowsAccount = 'vera-blender-runner'" in uninstaller
    assert "WindowsBuiltInRole]::Administrator" in uninstaller
    assert "GITHUB_RUNNER_ADMIN_TOKEN" in uninstaller
    assert "$env:GITHUB_RUNNER_ADMIN_TOKEN = $null" in uninstaller
    assert "$env:GH_TOKEN = $adminToken" in uninstaller
    assert "$env:GH_TOKEN = $priorGhToken" in uninstaller
    assert "gh auth status" not in uninstaller
    assert "gh auth login" not in uninstaller
    assert "Persistent gh login is not accepted" in uninstaller
    assert "actions/runners/remove-token" in uninstaller


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


def test_windows_installer_and_uninstaller_use_json_without_gh_jq_quoting():
    installer = (BASE / "installer" / "Install-VeraBlenderRunner.ps1").read_text(encoding="utf-8")
    uninstaller = (BASE / "installer" / "Uninstall-VeraBlenderRunner.ps1").read_text(encoding="utf-8")
    assert "--jq" not in installer
    assert "--jq" not in uninstaller
    assert "ConvertFrom-Json" in installer
    assert "ConvertFrom-Json" in uninstaller
    assert "visibility -ne 'PRIVATE'" in installer
    assert "visibility -ne 'PRIVATE'" in uninstaller
    assert "actions/runners/registration-token" in installer
    assert "actions/runners/remove-token" in uninstaller
