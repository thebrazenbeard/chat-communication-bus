from radar.actions_evidence import ActionsExecutionClass, classify_actions_jobs


def test_zero_step_failures_are_infrastructure_no_run():
    evidence = classify_actions_jobs([
        {"status": "completed", "conclusion": "failure", "steps": None},
        {"status": "completed", "conclusion": "failure", "steps": []},
    ])
    assert evidence.classification is ActionsExecutionClass.INFRASTRUCTURE_NO_RUN
    assert evidence.execution_established is False
    assert evidence.failed_jobs == 2
    assert evidence.jobs_without_steps == 2


def test_failed_job_with_steps_is_workflow_execution_failure():
    evidence = classify_actions_jobs([
        {"status": "completed", "conclusion": "failure", "steps": [{"name": "pytest", "status": "completed", "conclusion": "failure"}]},
    ])
    assert evidence.classification is ActionsExecutionClass.WORKFLOW_EXECUTION_FAILURE
    assert evidence.execution_established is True


def test_all_success_is_success():
    evidence = classify_actions_jobs([
        {"status": "completed", "conclusion": "success", "steps": [{"name": "pytest", "status": "completed", "conclusion": "success"}]},
        {"status": "completed", "conclusion": "success", "steps": [{"name": "pytest", "status": "completed", "conclusion": "success"}]},
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
        {"status": "completed", "conclusion": "success", "steps": [{"name": "pytest", "status": "completed", "conclusion": "success"}]},
        {"status": "completed", "conclusion": "failure", "steps": None},
    ])
    assert evidence.classification is ActionsExecutionClass.INFRASTRUCTURE_NO_RUN
    assert evidence.execution_established is True


def test_failed_job_with_only_queued_step_metadata_is_not_execution():
    evidence = classify_actions_jobs([
        {
            "status": "completed",
            "conclusion": "failure",
            "steps": [{"name": "pytest", "status": "queued", "conclusion": None}],
        },
    ])
    assert evidence.classification is ActionsExecutionClass.INFRASTRUCTURE_NO_RUN
    assert evidence.execution_established is False
    assert evidence.jobs_with_exposed_steps == 1
    assert evidence.jobs_with_steps == 0


def test_in_progress_step_is_execution_evidence():
    evidence = classify_actions_jobs([
        {
            "status": "completed",
            "conclusion": "failure",
            "steps": [{"name": "pytest", "status": "in_progress", "conclusion": None}],
        },
    ])
    assert evidence.classification is ActionsExecutionClass.WORKFLOW_EXECUTION_FAILURE
    assert evidence.execution_established is True
    assert evidence.jobs_with_exposed_steps == 1
    assert evidence.jobs_with_steps == 1
