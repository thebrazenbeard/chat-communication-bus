from radar.actions_evidence import ActionsExecutionClass, classify_actions_jobs


def test_zero_step_failures_are_infrastructure_no_run():
    evidence = classify_actions_jobs([
        {"status": "completed", "conclusion": "failure", "steps": None},
        {"status": "completed", "conclusion": "failure", "steps": []},
    ])
    assert evidence.classification is ActionsExecutionClass.INFRASTRUCTURE_NO_RUN
    assert evidence.execution_established is False
    assert evidence.source_failure_established is False
    assert evidence.failed_jobs == 2
    assert evidence.jobs_without_steps == 2


def test_failed_job_with_steps_is_source_or_runtime_failure():
    evidence = classify_actions_jobs([
        {"status": "completed", "conclusion": "failure", "steps": [{"name": "pytest"}]},
    ])
    assert evidence.classification is ActionsExecutionClass.SOURCE_OR_RUNTIME_FAILURE
    assert evidence.execution_established is True
    assert evidence.source_failure_established is True


def test_all_success_is_success():
    evidence = classify_actions_jobs([
        {"status": "completed", "conclusion": "success", "steps": [{"name": "pytest"}]},
        {"status": "completed", "conclusion": "success", "steps": [{"name": "pytest"}]},
    ])
    assert evidence.classification is ActionsExecutionClass.SUCCESS
    assert evidence.execution_established is True


def test_non_completed_job_is_incomplete():
    evidence = classify_actions_jobs([
        {"status": "queued", "conclusion": None, "steps": None},
    ])
    assert evidence.classification is ActionsExecutionClass.INCOMPLETE


def test_empty_job_set_is_unqualified():
    evidence = classify_actions_jobs([])
    assert evidence.classification is ActionsExecutionClass.UNQUALIFIED
    assert evidence.job_count == 0


def test_successful_job_does_not_turn_zero_step_failure_into_source_failure():
    evidence = classify_actions_jobs([
        {"status": "completed", "conclusion": "success", "steps": [{"name": "pytest"}]},
        {"status": "completed", "conclusion": "failure", "steps": None},
    ])
    assert evidence.classification is ActionsExecutionClass.INFRASTRUCTURE_NO_RUN
    assert evidence.execution_established is True
    assert evidence.source_failure_established is False
