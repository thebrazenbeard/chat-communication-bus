from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from radar.supabase_provider_reader import (
    ProviderReadback,
    ProviderReadbackError,
    SupabaseProviderReader,
)


DEFAULT_URL_ENV = "SUPABASE_URL"
DEFAULT_KEY_ENV = "SUPABASE_SERVICE_ROLE_KEY"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read Radar provider state through supabase-py")
    parser.add_argument("--url-env", default=DEFAULT_URL_ENV)
    parser.add_argument("--key-env", default=DEFAULT_KEY_ENV)
    sub = parser.add_subparsers(dest="command", required=True)

    lane = sub.add_parser("lane", help="Read one projection-lane state via read-only RPC")
    lane.add_argument("--identity-id", required=True)
    lane.add_argument("--branch", required=True)

    messages = sub.add_parser("messages", help="Read operator message-status view")
    messages.add_argument("--recipient-identity-id", required=True)
    messages.add_argument("--limit", type=int, default=100)

    assignments = sub.add_parser("assignments", help="Read open-assignment operator view")
    assignments.add_argument("--limit", type=int, default=100)
    return parser


def _payload(readback: ProviderReadback) -> dict[str, object]:
    return {
        "status": "READBACK",
        "surface": readback.surface,
        "transport": readback.transport,
        "canonical": readback.canonical,
        "provider_subject": readback.provider_subject,
        "query_scope": readback.query_scope,
        "observed_at": readback.observed_at,
        "completeness": readback.completeness,
        "requested_limit": readback.requested_limit,
        "probe_count": readback.probe_count,
        "row_digest_sha256": readback.row_digest_sha256,
        "rows": list(readback.rows),
    }


def _error(code: str, detail: str = "") -> dict[str, object]:
    payload: dict[str, object] = {"status": "ERROR", "code": code}
    if detail:
        payload["detail"] = detail
    return payload


def _credential(environ: Mapping[str, str], name: str) -> str:
    value = environ.get(name, "")
    if not value:
        raise ProviderReadbackError("PROVIDER_CREDENTIAL_ENV_MISSING", name)
    return value


def main(
    argv: Sequence[str] | None = None,
    *,
    environ: Mapping[str, str] | None = None,
    reader_factory=SupabaseProviderReader.from_credentials,
) -> int:
    args = build_parser().parse_args(argv)
    env = os.environ if environ is None else environ
    try:
        url = _credential(env, args.url_env)
        key = _credential(env, args.key_env)
        reader = reader_factory(url, key)
        if args.command == "lane":
            result = reader.read_projection_lane(args.identity_id, args.branch)
        elif args.command == "messages":
            result = reader.read_identity_message_status(
                args.recipient_identity_id, limit=args.limit
            )
        else:
            result = reader.read_open_assignments(limit=args.limit)
    except ProviderReadbackError as exc:
        print(json.dumps(_error(exc.code, exc.detail), sort_keys=True), file=sys.stderr)
        return 2

    print(json.dumps(_payload(result), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
