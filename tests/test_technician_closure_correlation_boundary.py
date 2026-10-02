from engine.correlation import Correlation
from engine.diagnostic_case import DiagnosticCase
from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def resolve_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def build_closure(workflow):
    return TechnicianCaseClosure(
        workflow=workflow,
        technician="Test Technician",
        reason="Issue resolved and verified.",
    )


def build_correlation():
    return Correlation(
        correlation_type="MEMORY_PROCESS",
        findings=["MEMORY_PRESSURE", "HIGH_PROCESS_MEMORY"],
        strength="HIGH",
        explanation="Memory pressure correlates with elevated process memory usage.",
    )


def set_correlation(workflow, correlation):
    workflow.case.set_correlations([correlation])


def correlation_signature(correlation):
    return (
        correlation.correlation_type,
        tuple(correlation.findings),
        correlation.strength,
        correlation.explanation,
    )


def case_correlation_signatures(workflow):
    return [
        correlation_signature(correlation)
        for correlation in workflow.case.correlations
    ]


def test_closure_does_not_create_correlation():
    workflow = build_workflow()

    resolve_workflow(workflow)
    correlations_before = case_correlation_signatures(workflow)

    build_closure(workflow)

    assert case_correlation_signatures(workflow) == correlations_before


def test_closure_does_not_remove_existing_correlation():
    workflow = build_workflow()

    correlation = build_correlation()
    expected_signature = correlation_signature(correlation)

    set_correlation(workflow, correlation)

    resolve_workflow(workflow)
    correlations_before = case_correlation_signatures(workflow)

    build_closure(workflow)

    assert case_correlation_signatures(workflow) == correlations_before
    assert expected_signature in case_correlation_signatures(workflow)


def test_closure_does_not_replace_existing_correlation():
    workflow = build_workflow()

    correlation = build_correlation()
    expected_signature = correlation_signature(correlation)

    set_correlation(workflow, correlation)

    resolve_workflow(workflow)
    build_closure(workflow)

    assert case_correlation_signatures(workflow) == [expected_signature]


def test_closure_does_not_change_correlation_count():
    workflow = build_workflow()

    set_correlation(workflow, build_correlation())

    resolve_workflow(workflow)
    count_before = len(workflow.case.correlations)

    build_closure(workflow)

    assert len(workflow.case.correlations) == count_before


def test_closure_does_not_change_case_evidence():
    workflow = build_workflow()

    set_correlation(workflow, build_correlation())

    resolve_workflow(workflow)

    evidence_before = dict(workflow.case.evidence)

    build_closure(workflow)

    assert workflow.case.evidence == evidence_before


def test_closure_does_not_appear_as_correlation():
    workflow = build_workflow()

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert all(
        value is not closure
        for value in workflow.case.correlations
    )


def test_closure_does_not_change_case_identity():
    workflow = build_workflow()

    case_id_before = workflow.case.case_id

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert workflow.case.case_id == case_id_before
    assert closure.workflow.case.case_id == case_id_before


def test_closure_does_not_change_case_status():
    workflow = build_workflow()

    resolve_workflow(workflow)

    status_before = workflow.case.status

    build_closure(workflow)

    assert workflow.case.status == status_before


def test_closure_does_not_change_correlations_after_reopen():
    workflow = build_workflow()

    correlation = build_correlation()
    expected_signature = correlation_signature(correlation)

    set_correlation(workflow, correlation)

    resolve_workflow(workflow)
    build_closure(workflow)

    workflow.reopen()

    assert expected_signature in case_correlation_signatures(workflow)
    assert len(workflow.case.correlations) == 1


def test_closure_remains_separate_from_correlation_identity():
    workflow = build_workflow()

    correlation = build_correlation()
    expected_signature = correlation_signature(correlation)

    set_correlation(workflow, correlation)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert closure is not correlation
    assert expected_signature in case_correlation_signatures(workflow)


def test_multiple_closures_do_not_duplicate_correlations():
    workflow = build_workflow()

    correlation = build_correlation()
    expected_signature = correlation_signature(correlation)

    set_correlation(workflow, correlation)

    resolve_workflow(workflow)
    first_closure = build_closure(workflow)

    workflow.reopen()

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    second_closure = TechnicianCaseClosure(
        workflow=workflow,
        technician="Second Technician",
        reason="Issue resolved after another recovery cycle.",
    )

    assert first_closure is not second_closure
    assert case_correlation_signatures(workflow) == [expected_signature]
    assert len(workflow.case.correlations) == 1


def test_closure_does_not_become_correlation():
    workflow = build_workflow()

    correlation = build_correlation()
    set_correlation(workflow, correlation)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert closure not in workflow.case.correlations


def test_closure_does_not_mutate_correlation_metadata():
    workflow = build_workflow()

    correlation = build_correlation()
    expected_signature = correlation_signature(correlation)

    set_correlation(workflow, correlation)

    resolve_workflow(workflow)

    build_closure(workflow)

    assert case_correlation_signatures(workflow) == [expected_signature]


def test_closure_does_not_change_case_correlation_count_after_reopen():
    workflow = build_workflow()

    set_correlation(workflow, build_correlation())

    resolve_workflow(workflow)

    build_closure(workflow)
    workflow.reopen()

    assert len(workflow.case.correlations) == 1


def test_closure_is_not_required_for_correlation_to_exist():
    workflow = build_workflow()

    correlation = build_correlation()
    expected_signature = correlation_signature(correlation)

    set_correlation(workflow, correlation)

    resolve_workflow(workflow)

    assert expected_signature in case_correlation_signatures(workflow)
    assert workflow.case.correlations


def test_case_correlation_does_not_create_closure():
    workflow = build_workflow()

    correlation = build_correlation()
    set_correlation(workflow, correlation)

    assert workflow.state.value == "OPEN"
    assert workflow.case.correlations