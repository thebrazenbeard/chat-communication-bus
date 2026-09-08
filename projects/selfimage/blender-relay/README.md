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
- Blender's raw `execute_code` capability is used only behind fixed local templates or a named approved script committed with the relay source.
- `import_exact_cc0` is pinned to the audited Blender Human Base Mesh mirror bytes and fails closed on byte count, SHA-256, and Git blob SHA-1.
- Result commits live outside the request path, so result writes do not recursively trigger the runner.
- This is still a self-hosted Actions runner: anyone able to modify executable workflow/relay source on the execution branch could potentially run code on the machine. Keep repository write access tightly controlled and do not expose this runner to public-repository pull requests.

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
- `scene_audit_v1` — the approved read-only Self Image Blender audit prepared on the Self Image branch
- `import_exact_cc0` — imports only the byte-pinned audited CC0 transport and refuses a non-default/non-empty scene
- `save_blend_copy`
- `export_scene_glb`

There is deliberately no request operation for arbitrary `execute_code`, arbitrary file path, arbitrary URL, shell command, or package installation.

## Local one-time setup

Use the installer package generated from this branch and double-click `Install-VeraBlenderRelay.cmd`.

The installer:

1. verifies whether Blender MCP is reachable on localhost:9876 (non-blocking if Blender is closed);
2. installs the official GitHub CLI through Windows `winget` if `gh` is not already installed;
3. opens GitHub's browser authentication flow if the PC is not already authenticated;
4. asks GitHub directly for a short-lived repository runner registration token — Patrick does not need to copy/paste the token;
5. downloads the latest official Windows x64 GitHub Actions runner and verifies GitHub's published SHA-256 digest when the release API supplies one;
6. registers a repository-scoped runner with the dedicated `vera-blender` label;
7. creates a per-user startup shortcut so the runner starts automatically when Patrick logs into Windows;
8. starts the runner immediately.

The short-lived runner registration token is discarded after registration. Blender itself remains local and listens only on `127.0.0.1:9876`; no inbound router/firewall exposure is required.

Blender must be running with the MCP for Blender addon started when Blender jobs execute. If Blender is closed, the relay fails the job cleanly and writes a durable failure receipt rather than pretending execution occurred.

## Disable / uninstall

Double-click `Uninstall-VeraBlenderRelay.cmd`. The uninstaller disables startup, stops the local runner, obtains GitHub's short-lived removal token automatically through the authenticated GitHub CLI, unregisters the runner, and removes the runner files when safe.

## Status model

Keep these separate:

- **source built** — relay source exists on the feature branch;
- **reviewed/integrated** — PR disposition in the Bus;
- **installed** — the local runner has been registered on Patrick's machine;
- **runtime online** — GitHub sees the `vera-blender` runner available;
- **Blender reachable** — the local addon is listening on 127.0.0.1:9876;
- **end-to-end proven** — the first relay `ping` produces a successful durable result receipt.

Source/build presence alone does not claim local installation or Blender execution.