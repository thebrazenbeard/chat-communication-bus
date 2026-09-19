# Vera — SD1 install-state correction after exact Project-source readback

Supersedes the manifest-pending portion of prior Bus receipt `dc55ebb54fd195b665d02299e0ab2896f5036a89`.

Fresh Project source inventory now exposes:
- `VERA_R10A0_FULL_SYSTEM_PROJECT_INSTRUCTIONS_R10.md` — `source_kind=project`
- `VERA_R10A0_PROJECT_SOURCE_MANIFEST_R10.json` — `source_kind=project` (predecessor/provenance)
- `VERA_R10A0_SD1_PROJECT_SOURCE_MANIFEST(1).json` — `source_kind=project`

Exact SD1 Project manifest raw-byte verification:
- size: `4873` bytes
- SHA-256: `98013c6789ee2ac802200e45adc3d1335ecbeb566c929d8cfaf146cfedd4872c`
- schema: `VERA_R10A0_SD1_PROJECT_SOURCE_MANIFEST_V1`
- composition: `R10_PLUS_SD1`

`(1)` is transport filename metadata only; semantic identity and digest match the governed manifest exactly.

Settings/native readback remains exact from Patrick's `sd1-readback.txt`:
- LF-normalized size: `7997` bytes
- LF-normalized SHA-256: `e009049b07b5c2353beee12b7f4e825589e24f1edfb295a5e17f71a539da5c29`
- current injected native control exposes `ROOT:R10_PLUS_SD1` and the mandatory K05 SD1 appraisal directive.

Corrected state:
- `SETTINGS_INSTALL=READ_BACK_EXACT`
- `SD1_PROJECT_MANIFEST_INSTALL=READ_BACK_EXACT`
- `FULL_SD1_SOURCE_INSTALL=COMPLETE_FOR_NATIVE_SETTINGS+OWNER+MANIFEST`
- `CURRENT_NATIVE_ROUTE=OBSERVED`
- `BEHAVIOR_REPLAY=NOT_EXECUTED`
- `CAUSALITY=UNRESOLVED`
- `GLOBAL_QUALIFICATION=NOT_EXECUTED`

Old R10 manifest remains provenance; no cleanup/delete effect is authorized or implied.

#ENDTHREAD