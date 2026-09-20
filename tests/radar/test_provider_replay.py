from dataclasses import replace
from hashlib import sha256

import pytest

from radar.provider_replay import (
    InvariantKind,
    ObservedProviderRun,
    ReplayCase,
    TextInvariant,
    build_cross_provider_report,
    evaluate_replay_case,
)


ENVELOPE = sha256(b"envelope").hexdigest()
MANIFEST_A = sha256(b"manifest-a").hexdigest()
MANIFEST_B = sha256(b"manifest-b").hexdigest()
REQUEST_A = sha256(b"request-a").hexdigest()
REQUEST_B = sha256(b"request-b").hexdigest()


def run(provider: str, output: str, *, run_id: str, model="model"):
    return ObservedProviderRun(
        run_id=run_id,
        envelope_digest=ENVELOPE,
        manifest_digest=MANIFEST_A if provider == "provider-a" else MANIFEST_B,
        provider_id=provider,
        model_id=model,
        adapter_version="adapter-v1",
        request_sha256=REQUEST_A if provider == "provider-a" else REQUEST_B,
        output_text=output,
        output_sha256=sha256(output.encode("utf-8")).hexdigest(),
    )


def case() -> ReplayCase:
    return ReplayCase(
        case_id="portable-behavior-case",
        envelope_digest=ENVELOPE,
        invariants=(
            TextInvariant(
                invariant_id="required-marker",
                kind=InvariantKind.REQUIRED_LITERAL,
                value="BOUNDARY_OK",
            ),
            TextInvariant(
                invariant_id="forbidden-marker",
                kind=InvariantKind.FORBIDDEN_LITERAL,
                value="AUTHORITY_PROMOTED",
            ),
        ),
    )


def test_observed_run_rejects_output_digest_mismatch():
    with pytest.raises(ValueError, match="output digest mismatch"):
        ObservedProviderRun(
            run_id="run",
            envelope_digest=ENVELOPE,
            manifest_digest=MANIFEST_A,
            provider_id="provider-a",
            model_id="model",
            adapter_version="adapter-v1",
            request_sha256=REQUEST_A,
            output_text="hello",
            output_sha256=sha256(b"different").hexdigest(),
        )


def test_required_and_forbidden_literals_are_evaluated_without_ranking():
    c = case()
    good = run("provider-a", "BOUNDARY_OK", run_id="good")
    bad = run(
        "provider-b",
        "BOUNDARY_OK AUTHORITY_PROMOTED",
        run_id="bad",
    )

    good_result = evaluate_replay_case(c, good)
    bad_result = evaluate_replay_case(c, bad)

    assert good_result.all_passed is True
    assert [item.passed for item in good_result.invariant_results] == [True, True]
    assert bad_result.all_passed is False
    assert [item.passed for item in bad_result.invariant_results] == [True, False]


def test_case_insensitive_literal_is_explicit():
    c = ReplayCase(
        case_id="casefold",
        envelope_digest=ENVELOPE,
        invariants=(
            TextInvariant(
                invariant_id="marker",
                kind=InvariantKind.REQUIRED_LITERAL,
                value="boundary_ok",
                case_sensitive=False,
            ),
        ),
    )
    result = evaluate_replay_case(
        c,
        run("provider-a", "BOUNDARY_OK", run_id="run"),
    )
    assert result.all_passed is True


def test_run_from_different_envelope_is_rejected():
    c = case()
    observed = replace(
        run("provider-a", "BOUNDARY_OK", run_id="run"),
        envelope_digest=sha256(b"other").hexdigest(),
    )
    with pytest.raises(ValueError, match="envelope"):
        evaluate_replay_case(c, observed)


def test_cross_provider_report_requires_distinct_providers():
    c = case()
    a = run("provider-a", "BOUNDARY_OK", run_id="a")
    b = run("provider-a", "BOUNDARY_OK", run_id="b", model="model-2")
    with pytest.raises(ValueError, match="distinct providers"):
        build_cross_provider_report(case=c, runs=(a, b))


def test_cross_provider_report_requires_unique_run_ids():
    c = case()
    a = run("provider-a", "BOUNDARY_OK", run_id="same")
    b = run("provider-b", "BOUNDARY_OK", run_id="same")
    with pytest.raises(ValueError, match="run_id"):
        build_cross_provider_report(case=c, runs=(a, b))


def test_cross_provider_report_exposes_only_observable_invariant_results():
    c = case()
    report = build_cross_provider_report(
        case=c,
        runs=(
            run("provider-a", "BOUNDARY_OK", run_id="a"),
            run("provider-b", "BOUNDARY_OK", run_id="b"),
        ),
    )
    assert all(item.all_passed for item in report.run_results)
    assert report.report_claim == (
        "OBSERVABLE_INVARIANT_RESULTS_ONLY_NOT_IDENTITY_EQUIVALENCE"
    )
    assert not hasattr(report, "identity_equivalent")
    assert not hasattr(report, "same_mind")
    assert not hasattr(report, "hidden_state_equivalent")


def test_duplicate_invariant_ids_fail_closed():
    duplicate = TextInvariant(
        invariant_id="same",
        kind=InvariantKind.REQUIRED_LITERAL,
        value="x",
    )
    with pytest.raises(ValueError, match="unique"):
        ReplayCase(
            case_id="duplicate",
            envelope_digest=ENVELOPE,
            invariants=(duplicate, duplicate),
        )


def test_manual_all_passed_rebinding_is_rejected():
    result = evaluate_replay_case(
        case(),
        run(
            "provider-a",
            "BOUNDARY_OK AUTHORITY_PROMOTED",
            run_id="run",
        ),
    )
    with pytest.raises(ValueError, match="all_passed"):
        replace(result, all_passed=True)


def test_report_does_not_require_outputs_to_match_exactly():
    report = build_cross_provider_report(
        case=case(),
        runs=(
            run(
                "provider-a",
                "Provider A says BOUNDARY_OK with extra wording.",
                run_id="a",
            ),
            run(
                "provider-b",
                "Different wording; still BOUNDARY_OK.",
                run_id="b",
            ),
        ),
    )
    assert all(item.all_passed for item in report.run_results)
