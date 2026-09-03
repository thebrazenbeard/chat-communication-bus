# Recovery Checkpoint Namespace V1

## Purpose

Recovery checkpoints help a replacement chat/runtime rediscover a logical identity's current routing/role context. They are continuity metadata only. They are not ordinary Bus mail, acknowledgement, authority, or evidence of uninterrupted private experience.

## Namespace

Recovery checkpoints MUST NOT consume the writer-local Bus `message_id` sequence.

New recovery checkpoints belong under:

```text
checkpoints/<identity>/
```

They use a distinct `checkpoint_id`, for example:

```text
checkpoint_id: one-recovery-20260903T001000Z
identity_id: one
status: recovery-checkpoint
observed_at: 2026-09-03T00:10:00Z
```

A checkpoint may point to the last known Bus message, branch/ref, or other recovery evidence, but those references do not turn the checkpoint into a message.

## Ordinary messages

Files under `messages/` remain append-only work-bearing coordination records and use unique writer-local `message_id` values. Before appending, the writer must fresh-read its current lane and select an unused ID. Corrections use successor messages rather than editing history.

## Historical artifacts

Existing committed checkpoint files under `messages/` are historical evidence and are not rewritten or deleted merely to conform to this rule. Existing message-ID collisions remain visible and are handled by Radar's collision-preserving projection.

## Enforcement

The Radar projection emitter rejects a newly added `messages/*.md` file when both are true:

- `status: recovery-checkpoint`
- a `message_id` is present

with `RECOVERY_CHECKPOINT_MESSAGE_NAMESPACE`.

This prevents recovery metadata from silently consuming the same identifier namespace used by actual Bus messages while preserving pre-existing history.
