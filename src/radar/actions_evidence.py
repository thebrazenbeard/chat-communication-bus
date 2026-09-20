"""Classify GitHub Actions execution evidence without conflating infrastructure and source failures."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable, Mapping, Any


class ActionsExecutionClass(StrEnum):
    SUCCESS = "SUCCESS"
    SOURCE_OR_RUNTIME_FAILURE = "SOURCE_OR_RUNTIME_FAILURE"
    INFRASTRUCTURE_NO_RUN = "INFRASTRUCTURE_NO_RUN"
    INCOMPLETE = "INCOMPLETE"
    UNQUALIFIED = "UNQUALIFIED"


@dataclass(frozen=True)
class ActionsExecutionEvidence:
    classification: ActionsExecutionClass
    job_count: int
    completed_jobs: int
    failed_jobs: int
    jobs_with_steps: int
    jobs_without_steps: int

    @property
    def source_failure_established(self) -> bool:
        return self.classification is ActionsExecutionClass.SOURCE_OR_RUNTIME_FAILURE

    @property
    def execution_established(self) -> bool:
        return self.jobs_with_steps > 0


def _steps_present(job: Mapping[str, Any]) -> bool:
    steps = job.get("steps")
    return isinstance(steps, list) and len(steps) > 0


def classify_actions_jobs(jobs: Iterable[Mapping[str, Any]]) -> ActionsExecutionEvidence:
    """Classify one workflow attempt from GitHub Jobs API-shaped records.

    A completed failed job with no exposed steps did not establish source execution.
    When every completed failed job lacks steps, classify the attempt as
    ``INFRASTRUCTURE_NO_RUN`` rather than a source/runtime failure.
    """

    records = tuple(jobs)
    if not records:
        return ActionsExecutionEvidence(
            classification=ActionsExecutionClass.UNQUALIFIED,
            job_count=0,
            completed_jobs=0,
            failed_jobs=0,
            jobs_with_steps=0,
            jobs_without_steps=0,
        )

    completed = tuple(job for job in records if job.get("status") == "completed")
    if len(completed) != len(records):
        classification = ActionsExecutionClass.INCOMPLETE
    else:
        failed = tuple(job for job in completed if job.get("conclusion") == "failure")
        successful = tuple(job for job in completed if job.get("conclusion") == "success")
        failed_with_steps = tuple(job for job in failed if _steps_present(job))

        if len(successful) == len(completed):
            classification = ActionsExecutionClass.SUCCESS
        elif failed_with_steps:
            classification = ActionsExecutionClass.SOURCE_OR_RUNTIME_FAILURE
        elif failed:
            classification = ActionsExecutionClass.INFRASTRUCTURE_NO_RUN
        else:
            classification = ActionsExecutionClass.UNQUALIFIED

    failed_jobs = sum(job.get("conclusion") == "failure" for job in completed)
    jobs_with_steps = sum(_steps_present(job) for job in completed)
    return ActionsExecutionEvidence(
        classification=classification,
        job_count=len(records),
        completed_jobs=len(completed),
        failed_jobs=failed_jobs,
        jobs_with_steps=jobs_with_steps,
        jobs_without_steps=len(completed) - jobs_with_steps,
    )
