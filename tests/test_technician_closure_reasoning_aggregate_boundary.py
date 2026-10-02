from engine.correlation import Correlation
from engine.diagnostic_case import DiagnosticCase
from engine.finding import Finding
from engine.recommendation import Recommendation
from engine.root_cause import RootCauseCandidate
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


def build_closure(workflow, technician="Test Technician"):
    return TechnicianCaseClosure(
        workflow=workflow,
        technician=technician,
        reason="Issue resolved and verified.",
    )


def build_finding():
    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="Memory usage is consistently high.",
    )


def build_correlation():
    return Correlation(
        correlation_type="MEMORY_PROCESS",
        findings=["MEMORY_PRESSURE", "HIGH_PROCESS_MEMORY"],
        strength="HIGH",
        explanation="Memory pressure correlates with elevated process memory usage.",
    )


def build_root_cause():
    return RootCauseCandidate(
        cause="Sustained memory pressure caused system instability.",
        category="MEMORY",
        confidence=0.90,
        evidence=["memory_usage"],
        reason="Memory usage remained consistently high.",
    )


def build_recommendation():
    return Recommendation(
        recommendation_type="MEMORY_REVIEW",
        category="MEMORY",
        priority="HIGH",
        description="Review applications using excessive memory.",
        rationale="Sustained memory pressure was detected.",
    )


def set_reasoning_data(workflow):
    workflow.case.set_findings([build_finding()])
    workflow.case.set_correlations([build_correlation()])
    workflow.case.set_root_causes([build_root_cause()])
    workflow.case.set_recommendations([build_recommendation()])


def finding_signature(finding):
    return (
        finding.finding_type,
        finding.category,
        finding.severity,
        finding.description,
    )


def correlation_signature(correlation):
    return (
        correlation.correlation_type,
        tuple(correlation.findings),
        correlation.strength,
        correlation.explanation,
    )


def root_cause_signature(root_cause):
    return (
        root_cause.cause,
        root_cause.category,
        root_cause.confidence,
        root_cause.reason,
    )


def recommendation_signature(recommendation):
    return (
        recommendation.recommendation_type,
        recommendation.category,
        recommendation.priority,
        recommendation.description,
        recommendation.rationale,
    )


def reasoning_snapshot(workflow):
    return {
        "findings": [
            finding_signature(finding)
            for finding in workflow.case.findings
        ],
        "correlations": [
            correlation_signature(correlation)
            for correlation in workflow.case.correlations
        ],
        "root_causes": [
            root_cause_signature(root_cause)
            for root_cause in workflow.case.root_causes
        ],
        "recommendations": [
            recommendation_signature(recommendation)
            for recommendation in workflow.case.recommendations
        ],
    }


def reasoning_counts(workflow):
    return {
        "findings": len(workflow.case.findings),
        "correlations": len(workflow.case.correlations),
        "root_causes": len(workflow.case.root_causes),
        "recommendations": len(workflow.case.recommendations),
    }


def test_closure_does_not_change_aggregate_reasoning():
    workflow = build_workflow()
    set_reasoning_data(workflow)

    resolve_workflow(workflow)
    reasoning_before = reasoning_snapshot(workflow)

    build_closure(workflow)

    assert reasoning_snapshot(workflow) == reasoning_before


def test_closure_does_not_change_aggregate_reasoning_counts():
    workflow = build_workflow()
    set_reasoning_data(workflow)

    resolve_workflow(workflow)
    counts_before = reasoning_counts(workflow)

    build_closure(workflow)

    assert reasoning_counts(workflow) == counts_before


def test_closure_does_not_change_reasoning_before_resolution():
    workflow = build_workflow()
    set_reasoning_data(workflow)

    reasoning_before = reasoning_snapshot(workflow)

    workflow.start_investigation()

    assert reasoning_snapshot(workflow) == reasoning_before


def test_closure_does_not_change_case_evidence():
    workflow = build_workflow()
    set_reasoning_data(workflow)

    resolve_workflow(workflow)
    evidence_before = dict(workflow.case.evidence)

    build_closure(workflow)

    assert workflow.case.evidence == evidence_before


def test_closure_does_not_change_case_identity():
    workflow = build_workflow()
    set_reasoning_data(workflow)

    case_id_before = workflow.case.case_id

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert workflow.case.case_id == case_id_before
    assert closure.workflow.case.case_id == case_id_before


def test_closure_does_not_change_case_status():
    workflow = build_workflow()
    set_reasoning_data(workflow)

    resolve_workflow(workflow)
    status_before = workflow.case.status

    build_closure(workflow)

    assert workflow.case.status == status_before


def test_closure_does_not_change_reasoning_after_reopen():
    workflow = build_workflow()
    set_reasoning_data(workflow)

    resolve_workflow(workflow)
    build_closure(workflow)

    workflow.reopen()

    assert reasoning_counts(workflow) == {
        "findings": 1,
        "correlations": 1,
        "root_causes": 1,
        "recommendations": 1,
    }


def test_closure_does_not_duplicate_any_reasoning_collection():
    workflow = build_workflow()
    set_reasoning_data(workflow)

    resolve_workflow(workflow)
    reasoning_before = reasoning_snapshot(workflow)

    build_closure(workflow)
    build_closure(workflow, technician="Second Technician")

    assert reasoning_snapshot(workflow) == reasoning_before


def test_multiple_closures_preserve_aggregate_reasoning():
    workflow = build_workflow()
    set_reasoning_data(workflow)

    resolve_workflow(workflow)
    reasoning_before = reasoning_snapshot(workflow)

    first_closure = build_closure(workflow)

    workflow.reopen()

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    second_closure = build_closure(
        workflow,
        technician="Second Technician",
    )

    assert first_closure is not second_closure
    assert reasoning_snapshot(workflow) == reasoning_before


def test_closure_is_not_present_in_any_reasoning_collection():
    workflow = build_workflow()
    set_reasoning_data(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert closure not in workflow.case.findings
    assert closure not in workflow.case.correlations
    assert closure not in workflow.case.root_causes
    assert closure not in workflow.case.recommendations


def test_reasoning_collections_remain_independent_of_closure_identity():
    workflow = build_workflow()
    set_reasoning_data(workflow)

    finding = workflow.case.findings[0]
    correlation = workflow.case.correlations[0]
    root_cause = workflow.case.root_causes[0]
    recommendation = workflow.case.recommendations[0]

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert closure is not finding
    assert closure is not correlation
    assert closure is not root_cause
    assert closure is not recommendation


def test_closure_does_not_change_reasoning_metadata():
    workflow = build_workflow()
    set_reasoning_data(workflow)

    reasoning_before = reasoning_snapshot(workflow)

    resolve_workflow(workflow)
    build_closure(workflow)

    assert reasoning_snapshot(workflow) == reasoning_before


def test_closure_does_not_create_missing_reasoning_data():
    workflow = build_workflow()

    resolve_workflow(workflow)

    assert reasoning_counts(workflow) == {
        "findings": 0,
        "correlations": 0,
        "root_causes": 0,
        "recommendations": 0,
    }

    build_closure(workflow)

    assert reasoning_counts(workflow) == {
        "findings": 0,
        "correlations": 0,
        "root_causes": 0,
        "recommendations": 0,
    }


def test_reasoning_data_does_not_create_closure():
    workflow = build_workflow()
    set_reasoning_data(workflow)

    assert workflow.state.value == "OPEN"


def test_reopening_does_not_change_reasoning_snapshot():
    workflow = build_workflow()
    set_reasoning_data(workflow)

    resolve_workflow(workflow)
    build_closure(workflow)

    snapshot_before_reopen = reasoning_snapshot(workflow)

    workflow.reopen()

    assert reasoning_snapshot(workflow) == snapshot_before_reopen


def test_closure_does_not_change_reasoning_when_case_resolves_again():
    workflow = build_workflow()
    set_reasoning_data(workflow)

    resolve_workflow(workflow)
    first_snapshot = reasoning_snapshot(workflow)

    build_closure(workflow)

    workflow.reopen()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    build_closure(workflow, technician="Second Technician")

    assert reasoning_snapshot(workflow) == first_snapshot