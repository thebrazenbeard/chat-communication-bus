from __future__ import annotations

import hashlib
import json

from radar.body_bound_oidc import (
    PROVIDER_AUDIENCE_PREFIX,
    canonical_json_bytes,
    post_body_bound_json,
)


class FakeResponse:
    def __init__(self, body: bytes):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self._body


class CapturingOpener:
    def __init__(self):
        self.requests = []

    def __call__(self, request, timeout):
        self.requests.append((request, timeout))
        return FakeResponse(b'{"ok":true}')


def test_body_bound_request_hashes_and_sends_exact_same_bytes() -> None:
    payload = {"operation": "cursor", "lane_identity": "yin", "repository": "thebrazenbeard/chat-communication-bus"}
    expected_body = canonical_json_bytes(payload)
    expected_digest = hashlib.sha256(expected_body).hexdigest()
    audiences = []
    opener = CapturingOpener()

    def token_provider(audience: str) -> str:
        audiences.append(audience)
        return "token-1"

    result = post_body_bound_json(
        "https://provider.invalid/github-bus-ingest",
        payload,
        token_provider=token_provider,
        opener=opener,
    )

    assert result == {"ok": True}
    assert audiences == [f"{PROVIDER_AUDIENCE_PREFIX}{expected_digest}"]
    request, timeout = opener.requests[0]
    assert request.data == expected_body
    assert request.get_header("Authorization") == "Bearer token-1"
    assert request.get_header("X-radar-body-sha256") == expected_digest
    assert timeout == 45


def test_each_bound_request_mints_a_fresh_digest_specific_token() -> None:
    audiences = []
    opener = CapturingOpener()

    def token_provider(audience: str) -> str:
        audiences.append(audience)
        return f"token-{len(audiences)}"

    first = {"operation": "cursor", "lane_identity": "yin"}
    second = {"operation": "cursor", "lane_identity": "yang"}
    post_body_bound_json("https://provider.invalid", first, token_provider=token_provider, opener=opener)
    post_body_bound_json("https://provider.invalid", second, token_provider=token_provider, opener=opener)

    assert len(audiences) == 2
    assert audiences[0] != audiences[1]
    assert opener.requests[0][0].get_header("Authorization") == "Bearer token-1"
    assert opener.requests[1][0].get_header("Authorization") == "Bearer token-2"


def test_canonical_json_bytes_are_stable_and_not_reserialized_after_hashing() -> None:
    payload = {"z": "é", "a": [3, 2, 1]}
    expected = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    assert canonical_json_bytes(payload) == expected
