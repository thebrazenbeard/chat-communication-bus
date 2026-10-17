# Independent host ↔ VeraOS source-conformance execution receipt

**2026-10-17 — Lappy Windows 11, Python 3.12.10 — SOURCE ONLY.**
No QEMU, real image, Buildroot compilation, graphical panel, provider/model,
task from installed runtime, disk modification, memory promotion or effects.

## Inputs verified from actual Git checkout heads

- `vera-os` integration Draft #38 candidate source:
  `beef4a6d6e6339e4da8bc89702b1f1882c1fb968`
  (fresh owner head when this local source test was prepared; mutable PR).
- `vera-mono` integration #77:
  `89ba1d18da78e7e38f015cf8d8ef4f528aae9df8`
- `portal` integration #51:
  `36fa04da4e5eb383fecf463c72a43b94ca47d7e5`
- `pre-active` immutable selected source:
  `1f23a809d7274df506e03e2d9052525538c3bcf6`
- `volition` immutable selected source:
  `dbc628d376515a0a523b1eecdf62129cca5d6b08`

Private disposable source checkouts at
`%TEMP%/vera-os-v1-crosshost-source-20261017` matched ALL required
exact heads by `git rev-parse HEAD`. Pinned Pre-Active/Volition commits were
fetched by immutable Git SHA rather than using their newer main HEADs.
The owning branches, active Codex A1 and installed runtime were untouched.

Stage with exact owner script:
```powershell
python vera-os/tools/vm/Stage-VeraOSResidentSources.py `
  --checkouts <isolated-source-directory> `
  --output <isolated-stage> --repo-root <isolated-vera-os-source>
```

Stage produced **431 exact committed source files**, Mono 316,
PORTAL 89, Pre-Active 18, Volition 8. Source receipt SHA256:
`6f0031c1fcbaed41e4e3f6947e90a92ed5656ac3e09329de7d8e0b0f8417eca5`.
The staging script performed its byte readback. This is NOT an OS image.

Then set `VERAOS_CANONICAL_STAGE=<stage>/components`, add isolated
VeraOS `src` and `tests` to PYTHONPATH and execute:

```powershell
python -B -m pytest -q tests/test_host_resident_runtime_conformance.py `
  -p no:cacheprovider --disable-warnings --tb=short
```

**Actual result: 5 PASS / 0 FAIL / 0 SKIP, exit code 0, 6.12 seconds.**
These are real source/runtime Python tests of:
1. direct Mono task opener -> actual VeraOS resident HTTP and cold reentry;
2. scoped SQLite concurrent-write denial, not global state-root lease;
3. separate Python process same-byte replay vs changed-byte rejection;
4. handles closed/reopened with real Windows SQLite rename without GC;
5. Desktop's identity tuple remains distinct from VeraOS's tuple.

This is a **representative executable cross-host *source* contract**. It does
not certify the currently installed PORTAL Desktop binary, target Linux
Python libraries, runtime routing between Lappy/VN1, an actual ext2 image,
graphical Cog input, hardware disk or two-boot guest. The resident test
operates with a disposable task root and loopback fixture; it cannot grant
production/provider/effect authority.

The original V1 source-API verifier independently read five immutable Git
blobs (Mono, PORTAL Desktop/host/host bridge and VeraOS) and found expected
functions at the frozen source pin. Static method presence is materially
weaker evidence than these five source-level host behavior tests.
