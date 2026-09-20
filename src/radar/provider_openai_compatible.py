"""Construct local OpenAI-compatible Chat Completions requests.

This module does not perform network I/O. It only converts an already-prepared
Freedom execution into a deterministic loopback-only HTTP request description.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from urllib.parse import urlparse

from .provider_execution_binding import PreparedAdapterExecution


_LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}
_CHAT_COMPLETIONS_PATH = "/v1/chat/completions"


def _canonical_json(payload: object) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


@dataclass(frozen=True)
class LocalOpenAICompatibleProfile:
    provider_id: str
    adapter_version: str
    base_url: str

    def __post_init__(self) -> None:
        for value, label in (
            (self.provider_id, "provider_id"),
            (self.adapter_version, "adapter_version"),
            (self.base_url, "base_url"),
        ):
            if type(value) is not str or not value.strip():
                raise ValueError(f"{label} must be a non-empty exact string")

        parsed = urlparse(self.base_url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("base_url must use http or https")
        if parsed.hostname not in _LOOPBACK_HOSTS:
            raise ValueError("base_url must target loopback only")
        if parsed.username is not None or parsed.password is not None:
            raise ValueError("base_url must not contain userinfo")
        if parsed.query or parsed.fragment:
            raise ValueError("base_url must not contain query or fragment")
        if parsed.path not in ("", "/"):
            raise ValueError("base_url must be an origin, not an API path")
        try:
            port = parsed.port
        except ValueError:
            raise ValueError("base_url contains invalid port") from None
        if port is None:
            raise ValueError("base_url must include explicit port")
        if not 1 <= port <= 65535:
            raise ValueError("base_url port out of range")

    @property
    def request_url(self) -> str:
        return self.base_url.rstrip("/") + _CHAT_COMPLETIONS_PATH


def _validate_loopback_request_url(url: str) -> None:
    if type(url) is not str or not url.strip():
        raise ValueError("request_url must be a non-empty exact string")
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("request_url must use http or https")
    if parsed.hostname not in _LOOPBACK_HOSTS:
        raise ValueError("request_url must target loopback only")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("request_url must not contain userinfo")
    if parsed.query or parsed.fragment:
        raise ValueError("request_url must not contain query or fragment")
    if parsed.path != _CHAT_COMPLETIONS_PATH:
        raise ValueError("request_url must target exact chat completions path")
    try:
        port = parsed.port
    except ValueError:
        raise ValueError("request_url contains invalid port") from None
    if port is None or not 1 <= port <= 65535:
        raise ValueError("request_url must include valid explicit port")


@dataclass(frozen=True)
class LocalOpenAICompatibleRequest:
    provider_id: str
    model_id: str
    adapter_version: str
    request_url: str
    payload_json: str
    payload_sha256: str
    request_claim: str = "LOCAL_LOOPBACK_REQUEST_CONSTRUCTION_ONLY"

    def __post_init__(self) -> None:
        if self.request_claim != "LOCAL_LOOPBACK_REQUEST_CONSTRUCTION_ONLY":
            raise ValueError("unsupported local request claim")
        for value, label in (
            (self.provider_id, "provider_id"),
            (self.model_id, "model_id"),
            (self.adapter_version, "adapter_version"),
        ):
            if type(value) is not str or not value.strip():
                raise ValueError(f"{label} must be a non-empty exact string")
        _validate_loopback_request_url(self.request_url)
        if type(self.payload_json) is not str or not self.payload_json:
            raise ValueError("payload_json must be non-empty exact string")
        try:
            payload = json.loads(self.payload_json)
        except json.JSONDecodeError:
            raise ValueError("payload_json must be valid JSON") from None
        if type(payload) is not dict:
            raise ValueError("payload_json must encode an object")
        if payload.get("model") != self.model_id:
            raise ValueError("payload model mismatch")
        if payload.get("stream") is not False:
            raise ValueError("payload must be non-streaming")
        messages = payload.get("messages")
        if type(messages) is not list or len(messages) != 2:
            raise ValueError("payload must contain exactly two messages")
        if (
            type(messages[0]) is not dict
            or messages[0].get("role") != "system"
            or type(messages[0].get("content")) is not str
        ):
            raise ValueError("payload system message invalid")
        if (
            type(messages[1]) is not dict
            or messages[1].get("role") != "user"
            or type(messages[1].get("content")) is not str
        ):
            raise ValueError("payload user message invalid")
        if _canonical_json(payload) != self.payload_json:
            raise ValueError("payload_json must use canonical serialization")
        if (
            type(self.payload_sha256) is not str
            or len(self.payload_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in self.payload_sha256)
        ):
            raise ValueError("payload_sha256 must be lowercase SHA-256")
        if sha256(self.payload_json.encode("utf-8")).hexdigest() != self.payload_sha256:
            raise ValueError("payload digest mismatch")

    @property
    def payload(self) -> dict[str, object]:
        return json.loads(self.payload_json)


def _decode_utf8(data: bytes, label: str) -> str:
    if type(data) is not bytes:
        raise ValueError(f"{label} must be exact bytes")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError(f"{label} is not UTF-8 text") from None


def build_local_openai_compatible_request(
    *,
    prepared: PreparedAdapterExecution,
    profile: LocalOpenAICompatibleProfile,
) -> LocalOpenAICompatibleRequest:
    if type(prepared) is not PreparedAdapterExecution:
        raise ValueError("prepared must be exact PreparedAdapterExecution")
    if type(profile) is not LocalOpenAICompatibleProfile:
        raise ValueError("profile must be exact LocalOpenAICompatibleProfile")

    plan = prepared.plan
    materialized = prepared.materialized

    if profile.provider_id != plan.provider_id:
        raise ValueError("local profile provider mismatch")
    if profile.adapter_version != plan.adapter_version:
        raise ValueError("local profile adapter mismatch")

    task_input = _decode_utf8(materialized.input_bytes, "task input")

    receipt_by_subject = {
        (
            receipt.repository,
            receipt.commit_sha,
            receipt.path,
            receipt.git_blob,
        ): receipt
        for receipt in materialized.provenance_receipts
    }
    if len(receipt_by_subject) != len(materialized.provenance_receipts):
        raise ValueError("duplicate provenance receipt subject")

    state_rows: list[dict[str, object]] = []
    for item in materialized.state_objects:
        subject = (item.repository, item.commit_sha, item.path, item.git_blob)
        receipt = receipt_by_subject.get(subject)
        if receipt is None:
            raise ValueError("state object missing matching provenance receipt")
        state_rows.append(
            {
                "repository": item.repository,
                "repository_id": receipt.repository_id,
                "commit_sha": item.commit_sha,
                "path": item.path,
                "git_blob": item.git_blob,
                "content": _decode_utf8(
                    item.content,
                    f"state object {item.repository}:{item.path}",
                ),
            }
        )

    reference_context = {
        "schema": "VERA_OPENAI_COMPAT_REFERENCE_CONTEXT_V1",
        "claim": "REFERENCE_CONTEXT_NOT_SYSTEM_AUTHORITY",
        "state_objects": state_rows,
        "task_input": task_input,
    }

    payload: dict[str, object] = {
        "model": plan.model_id,
        "messages": [
            {
                "role": "system",
                "content": materialized.instruction_text,
            },
            {
                "role": "user",
                "content": _canonical_json(reference_context),
            },
        ],
        "stream": False,
    }

    payload_json = _canonical_json(payload)
    payload_sha256 = sha256(payload_json.encode("utf-8")).hexdigest()
    return LocalOpenAICompatibleRequest(
        provider_id=plan.provider_id,
        model_id=plan.model_id,
        adapter_version=plan.adapter_version,
        request_url=profile.request_url,
        payload_json=payload_json,
        payload_sha256=payload_sha256,
    )


__all__ = [
    "LocalOpenAICompatibleProfile",
    "LocalOpenAICompatibleRequest",
    "build_local_openai_compatible_request",
]
