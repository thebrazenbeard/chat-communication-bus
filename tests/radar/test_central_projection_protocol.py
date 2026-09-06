from __future__ import annotations

from radar.central_projection import (
    ProviderProjectionClient,
    chunk_projection_files,
)


def test_provider_client_uses_explicit_journal_operations() -> None:
    calls = []

    def transport(endpoint, payload, *, token_provider):
        calls.append((endpoint, payload, token_provider))
        op = payload["operation"]
        if op == "cursor":
            return {"ok": True, "lane": {"projected_head_sha": "a" * 40}}
        if op == "set_control_cut":
            return {"ok": True}
        if op == "claim_batch":
            return {"ok": True, "batch": {"batch_id": "batch-1", "claim_token": "token-1"}}
        if op == "project_batch":
            return {"ok": True, "results": []}
        if op == "finalize_batch":
            return {"ok": True, "lane": {"projected_head_sha": "b" * 40}}
        raise AssertionError(op)

    token_provider = lambda audience: "oidc"
    client = ProviderProjectionClient(
        "https://provider.invalid/ingest",
        token_provider=token_provider,
        transport=transport,
    )

    assert client.get_lane("yin", "bus/yin-v2")["projected_head_sha"] == "a" * 40
    client.set_control_cut("yin", "bus/yin-v2", "c" * 40, "d" * 40)
    claim = client.claim_batch(
        identity="yin",
        branch="bus/yin-v2",
        expected_projected_head="a" * 40,
        target_head="b" * 40,
        control_sha="c" * 40,
        topology_sha="d" * 40,
        files=("messages/yin-0001.md",),
        owner="run-1",
    )
    client.project_batch(
        identity="yin",
        branch="bus/yin-v2",
        branch_head="b" * 40,
        batch_id=claim["batch_id"],
        claim_token=claim["claim_token"],
        files=(),
    )
    assert client.finalize_batch(claim["batch_id"], claim["claim_token"])["projected_head_sha"] == "b" * 40

    assert [payload["operation"] for _, payload, _ in calls] == [
        "cursor",
        "set_control_cut",
        "claim_batch",
        "project_batch",
        "finalize_batch",
    ]
    assert all(provider is token_provider for _, _, provider in calls)

    project_payload = calls[3][1]
    assert project_payload["identity"] == "yin"
    assert project_payload["lane_identity"] == "yin"
    assert project_payload["branch"] == "bus/yin-v2"
    assert project_payload["ref"] == "refs/heads/bus/yin-v2"


def test_projection_chunking_is_deterministic_and_never_drops_files() -> None:
    files = tuple(
        {"path": f"messages/yin-{i:04d}.md", "content_base64": "YQ==", "content_bytes": 1}
        for i in range(1, 6)
    )
    chunks = chunk_projection_files(files, max_files=2, max_total_bytes=2)
    assert [len(chunk) for chunk in chunks] == [2, 2, 1]
    assert [item["path"] for chunk in chunks for item in chunk] == [item["path"] for item in files]
