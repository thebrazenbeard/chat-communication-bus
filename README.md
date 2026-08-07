# chat-communication-bus

A runnable, nonproduction vertical slice for durable Chat Bus coordination.

## Commit 1 scope

This slice implements database-enforced lifecycle transitions, immutable assignment identity, architecture-bound final acceptance, predecessor-bound supersession, and strict lowercase SHA-256 validation. It includes regression tests for the defects identified in Chat Bus V3 review findings 001, 002, and 004.

The active single-coordinator fallback polling and readback gate belongs to commit 2 and is intentionally not claimed complete here.

## Run

```bash
python -m pip install -e '.[test]'
python -m compileall -q src
python -m pytest -q
```

No merge, deployment, credentials, paid service, production mutation, or external network operation is part of this slice.
