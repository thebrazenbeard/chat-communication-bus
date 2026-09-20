# GitHub Actions Execution Evidence V1

Status: SOURCE CANDIDATE / ISSUE #155 SUPPORTING REPAIR / NO PROVIDER EFFECT.

## Purpose

GitHub Actions can fail before a hosted runner executes any workflow step. Radar must not treat that shape as evidence that repository source or tests failed.

`src/radar/actions_evidence.py` classifies Jobs API-shaped evidence without guessing the upstream root cause.

## Classes

- `SUCCESS`: every completed job succeeded.
- `WORKFLOW_EXECUTION_FAILURE`: at least one failed job exposed one or more executed steps. This proves execution began, not why it failed.
- `INFRASTRUCTURE_NO_RUN`: at least one job failed, and no failed job exposed any executed steps.
- `INCOMPLETE`: at least one job is not complete.
- `UNQUALIFIED`: no usable completed success/failure evidence exists.

`INFRASTRUCTURE_NO_RUN` does not identify billing, runner capacity, policy, provider outage, or any other specific root cause. It establishes only that the failed job did not expose workflow execution evidence.

## Claim discipline

A red GitHub check is not by itself a source failure.

A job recorded as `completed/failure` with `steps: null` or `steps: []` remains infrastructure-unqualified. A failed job with steps establishes only that workflow execution began. Source/test failure still requires step- or log-specific evidence showing that repository code or tests actually failed.

Mixed attempts remain conservative: a successful job may establish that some execution happened, but a separate zero-step failed job does not become a source failure merely because another matrix leg ran.

## Current incident binding

Issue #155 records repeated private-repository GitHub-hosted jobs that complete as failures with no exposed steps. A manual re-run of run `35507205686` on 2026-09-20 recreated both Python matrix jobs and reproduced the same zero-step failure shape. Draft PR #179's own run `35526994410` reproduced it again on both matrix legs.

This source candidate improves evidence classification only. It does not alter GitHub Actions settings, billing, runners, credentials, workflows, providers, or deployment state.
