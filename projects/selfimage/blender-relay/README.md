# Self Image Blender Relay V1

A private, GitHub-backed relay from the Chat Communication Bus to Patrick's local Blender instance.

## Purpose

The relay removes Codex/Work availability from the Blender transport path. GitHub remains the durable mailbox and provenance surface; a repository-scoped Windows self-hosted runner on Patrick's machine receives bounded relay jobs and talks only to the already-running Blender MCP addon on `127.0.0.1:9876`.

The relay is intentionally not a general remote shell. It accepts a strict operation allowlist and writes a durable JSON result for every request. Binary outputs such as viewport screenshots and exported `.blend`/`.glb` files are emitted as workflow artifacts rather than committed to Git history.

## Security boundary

- Repository must remain private.
- No `pull_request` execution trigger exists.
- Jobs run only for pushes to the dedicated relay branch and only when request files change.
- Workflow is actor-gated to `thebrazenbeard`.
- Runner has a dedicated label: `vera-blender`.
- Request operations are allowlisted; request JSON cannot supply shell or Python source.
- Blender's raw `execute_code` capability is used only behind fixed local templates for bounded operations such as mesh audit/import/export.
- `import_exact_cc0` is pinned to the audited Blender Human Base Mesh mirror bytes and fails closed on byte count, SHA-256, and Git blob SHA-1.
- Result commits live outside the request path, so result writes do not recursively trigger the runner.
- This is still a self-hosted Actions runner: anyone who can write executable workflow changes to the private repository can potentially run code on the machine. Keep write access tightly controlled.

## Branch

`feature/selfimage-blender-relay-v1`

## Relay mailbox

- Requests: `projects/selfimage/blender-relay/requests/*.json`
- Durable result summaries: `projects/selfimage/blender-relay/results/*.json`
- Binary results: GitHub Actions artifact `vera-blender-relay-<run_id>`

## Request contract

Each request is one JSON object:

```json
{
  "version": 1,
  "request_id": "unique-safe-id",
  "operation": "scene_info",
  "args": {},
  "created_at": "2026-09-08T02:00:00Z"
}
```

`request_id` must match `[A-Za-z0-9][A-Za-z0-9._-]{0,79}`.

V1 operations:

- `ping`
- `addon_info`
- `scene_info`
- `object_info` (`args.name` required)
- `world_state`
- `viewport_capture` (`args.max_size` optional, clamped to 256..2000)
- `mesh_audit`
- `import_exact_cc0` (fails if the scene contains anything other than the untouched default Cube/Light/Camera unless explicitly extended in source)
- `save_blend_copy`
- `export_scene_glb`

There is deliberately no arbitrary `execute_code`, arbitrary path, arbitrary URL, or shell operation in the request contract.

## Local one-time setup

Use `installer/Install-VeraBlenderRunner.ps1` from this branch. It installs a repository-scoped GitHub Actions runner under the current Windows user, registers the `vera-blender` label, and creates a per-user logon scheduled task so the runner starts without Patrick manually keeping a terminal open.

The only GitHub credential required locally is GitHub's short-lived runner registration token. Obtain it from the private repository's **Settings → Actions → Runners → New self-hosted runner** page. It is used once to register the runner and is not retained by the relay.

Blender must be running with the MCP for Blender addon started on port 9876 for Blender jobs to succeed. When Blender is closed, requests fail cleanly and preserve a result receipt instead of hanging indefinitely.

## Disable / uninstall

Use `installer/Uninstall-VeraBlenderRunner.ps1`. It stops/removes the logon task and invokes the runner's normal removal flow. A fresh short-lived removal token from GitHub may be required by GitHub for unregistering the runner.

## Status

Source/build presence is not the same thing as local installation or runtime health. The relay becomes operational only after Patrick completes the one-time runner registration and the first `ping` request succeeds on the `vera-blender` runner.