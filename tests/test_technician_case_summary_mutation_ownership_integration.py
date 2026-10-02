from engine.diagnostic_case import DiagnosticCase
from engine.finding import Finding
from engine.root_cause import RootCauseCandidate
from engine.recommendation import Recommendation
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_decision import (
    TechnicianDecision,
    TechnicianDecisionType,
)
from engine.technician_reasoning_summary import TechnicianReasoningSummary
from engine.technician_recovery_cycle_history import TechnicianRecoveryCycleHistory
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def add_finding(workflow):
    finding = Finding(
        "MEMORY_PRESSURE",
        "MEMORY",
        "HIGH",
        "High memory usage detected.",
    )
    workflow.case.findings.append(finding)
    return finding


def add_root_cause(workflow):
    root_cause = RootCauseCandidate(
        cause="Insufficient available memory",
        category="MEMORY",
        confidence=0.90,
        evidence=[],
        reason="Memory pressure is supported by diagnostic evidence.",
    )
    workflow.case.root_causes.append(root_cause)
    return root_cause


def add_recommendation(workflow):
    recommendation = Recommendation(
        "memory-review",
        "Review memory usage",
        "MEDIUM",
        "Review applications consuming significant memory.",
        "Reducing unnecessary memory pressure may improve responsiveness.",
    )
    workflow.case.recommendations.append(recommendation)
    return recommendation


def add_reasoning(workflow):
    recovery_history = TechnicianRecoveryCycleHistory(workflow)

    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        recovery_history,
    )

    return recovery_history, reasoning_summary


def add_decision(workflow, recommendation):
    return TechnicianDecision(
        workflow,
        recommendation,
        TechnicianDecisionType.ACCEPT,
        "Proceed with the recommendation.",
    )


def test_mutating_summary_findings_does_not_mutate_case():
    workflow = build_workflow()
    finding = add_finding(workflow)

    summary = TechnicianCaseSummary(workflow)

    returned_findings = summary.findings
    returned_findings.clear()

    assert workflow.case.findings == [finding]
    assert len(summary.findings) == 1
    assert summary.findings[0] is finding


def test_mutating_summary_root_causes_does_not_mutate_case():
    workflow = build_workflow()
    root_cause = add_root_cause(workflow)

    summary = TechnicianCaseSummary(workflow)

    returned_root_causes = summary.root_causes
    returned_root_causes.clear()

    assert workflow.case.root_causes == [root_cause]
    assert len(summary.root_causes) == 1
    assert summary.root_causes[0] is root_cause


def test_mutating_summary_recommendations_does_not_mutate_case():
    workflow = build_workflow()
    recommendation = add_recommendation(workflow)

    summary = TechnicianCaseSummary(workflow)

    returned_recommendations = summary.recommendations
    returned_recommendations.clear()

    assert workflow.case.recommendations == [recommendation]
    assert len(summary.recommendations) == 1
    assert summary.recommendations[0] is recommendation


def test_appending_to_returned_findings_does_not_add_case_finding():
    workflow = build_workflow()
    finding = add_finding(workflow)

    summary = TechnicianCaseSummary(workflow)

    returned_findings = summary.findings

    returned_findings.append(
        Finding(
            "FAKE_FINDING",
            "TEST",
            "LOW",
            "This must not enter the case.",
        )
    )

    assert workflow.case.findings == [finding]
    assert len(summary.findings) == 1


def test_appending_to_returned_root_causes_does_not_add_case_root_cause():
    workflow = build_workflow()
    root_cause = add_root_cause(workflow)

    summary = TechnicianCaseSummary(workflow)

    returned_root_causes = summary.root_causes

    returned_root_causes.append(
        RootCauseCandidate(
            cause="Fake cause",
            category="TEST",
            confidence=0.10,
            evidence=[],
            reason="This must not enter the case.",
        )
    )

    assert workflow.case.root_causes == [root_cause]
    assert len(summary.root_causes) == 1


def test_appending_to_returned_recommendations_does_not_add_case_recommendation():
    workflow = build_workflow()
    recommendation = add_recommendation(workflow)

    summary = TechnicianCaseSummary(workflow)

    returned_recommendations = summary.recommendations

    returned_recommendations.append(
        Recommendation(
            "fake-recommendation",
            "Fake recommendation",
            "LOW",
            "This must not enter the case.",
            "This must not enter the case.",
        )
    )

    assert workflow.case.recommendations == [recommendation]
    assert len(summary.recommendations) == 1


def test_summary_collection_is_not_the_case_collection():
    workflow = build_workflow()
    add_finding(workflow)
    add_root_cause(workflow)
    add_recommendation(workflow)

    summary = TechnicianCaseSummary(workflow)

    assert summary.findings is not workflow.case.findings
    assert summary.root_causes is not workflow.case.root_causes
    assert summary.recommendations is not workflow.case.recommendations


def test_summary_domain_objects_preserve_identity():
    workflow = build_workflow()

    finding = add_finding(workflow)
    root_cause = add_root_cause(workflow)
    recommendation = add_recommendation(workflow)

    summary = TechnicianCaseSummary(workflow)

    assert summary.findings[0] is finding
    assert summary.root_causes[0] is root_cause
    assert summary.recommendations[0] is recommendation


def test_two_summaries_have_independent_collection_objects():
    workflow = build_workflow()

    finding = add_finding(workflow)
    root_cause = add_root_cause(workflow)
    recommendation = add_recommendation(workflow)

    first_summary = TechnicianCaseSummary(workflow)
    second_summary = TechnicianCaseSummary(workflow)

    assert first_summary.findings is not second_summary.findings
    assert first_summary.root_causes is not second_summary.root_causes
    assert first_summary.recommendations is not second_summary.recommendations

    assert first_summary.findings[0] is finding
    assert second_summary.findings[0] is finding

    assert first_summary.root_causes[0] is root_cause
    assert second_summary.root_causes[0] is root_cause

    assert first_summary.recommendations[0] is recommendation
    assert second_summary.recommendations[0] is recommendation


def test_mutating_one_summary_does_not_affect_second_summary():
    workflow = build_workflow()
    add_finding(workflow)
    add_root_cause(workflow)
    add_recommendation(workflow)

    first_summary = TechnicianCaseSummary(workflow)
    second_summary = TechnicianCaseSummary(workflow)

    first_summary.findings.clear()
    first_summary.root_causes.clear()
    first_summary.recommendations.clear()

    assert len(first_summary.findings) == 1
    assert len(first_summary.root_causes) == 1
    assert len(first_summary.recommendations) == 1

    assert len(second_summary.findings) == 1
    assert len(second_summary.root_causes) == 1
    assert len(second_summary.recommendations) == 1

    assert len(workflow.case.findings) == 1
    assert len(workflow.case.root_causes) == 1
    assert len(workflow.case.recommendations) == 1


def test_second_summary_reflects_new_case_records_without_sharing_collection():
    workflow = build_workflow()

    first_finding = add_finding(workflow)

    first_summary = TechnicianCaseSummary(workflow)

    second_finding = add_finding(workflow)

    second_summary = TechnicianCaseSummary(workflow)

    assert len(first_summary.findings) == 2
    assert len(second_summary.findings) == 2

    assert first_summary.findings[0] is first_finding
    assert first_summary.findings[1] is second_finding

    assert second_summary.findings[0] is first_finding
    assert second_summary.findings[1] is second_finding

    assert first_summary.findings is not second_summary.findings


def test_reasoning_summary_is_owned_by_summary_reference_not_collection_snapshot():
    workflow = build_workflow()

    recovery_history, reasoning_summary = add_reasoning(workflow)

    summary = TechnicianCaseSummary(workflow)
    summary.set_reasoning_summary(reasoning_summary)

    assert summary.reasoning_summary is reasoning_summary
    assert summary.reasoning_summary.cycle_history is recovery_history
    assert summary.reasoning_summary.workflow is workflow


def test_two_summaries_can_reference_same_reasoning_without_mutating_each_other():
    workflow = build_workflow()

    recovery_history, reasoning_summary = add_reasoning(workflow)

    first_summary = TechnicianCaseSummary(workflow)
    second_summary = TechnicianCaseSummary(workflow)

    first_summary.set_reasoning_summary(reasoning_summary)
    second_summary.set_reasoning_summary(reasoning_summary)

    assert first_summary.reasoning_summary is reasoning_summary
    assert second_summary.reasoning_summary is reasoning_summary

    assert first_summary.reasoning_summary is second_summary.reasoning_summary
    assert first_summary.reasoning_summary.cycle_history is recovery_history
    assert second_summary.reasoning_summary.cycle_history is recovery_history


def test_decision_reference_preserves_identity():
    workflow = build_workflow()
    recommendation = add_recommendation(workflow)

    decision = add_decision(workflow, recommendation)

    summary = TechnicianCaseSummary(workflow)
    summary._decision = decision

    assert summary.decision is decision
    assert summary.decision.workflow is workflow
    assert summary.decision.recommendation is recommendation


def test_two_summaries_can_reference_same_decision_without_collection_sharing():
    workflow = build_workflow()
    recommendation = add_recommendation(workflow)

    decision = add_decision(workflow, recommendation)

    first_summary = TechnicianCaseSummary(workflow)
    second_summary = TechnicianCaseSummary(workflow)

    first_summary._decision = decision
    second_summary._decision = decision

    assert first_summary.decision is decision
    assert second_summary.decision is decision
    assert first_summary.decision is second_summary.decision


def test_repeated_summary_construction_does_not_duplicate_case_records():
    workflow = build_workflow()

    finding = add_finding(workflow)
    root_cause = add_root_cause(workflow)
    recommendation = add_recommendation(workflow)

    summaries = [
        TechnicianCaseSummary(workflow)
        for _ in range(20)
    ]

    assert len(workflow.case.findings) == 1
    assert len(workflow.case.root_causes) == 1
    assert len(workflow.case.recommendations) == 1

    for summary in summaries:
        assert len(summary.findings) == 1
        assert len(summary.root_causes) == 1
        assert len(summary.recommendations) == 1

        assert summary.findings[0] is finding
        assert summary.root_causes[0] is root_cause
        assert summary.recommendations[0] is recommendation


def test_summary_ownership_boundary_remains_stable_after_multiple_mutations():
    workflow = build_workflow()

    finding = add_finding(workflow)
    root_cause = add_root_cause(workflow)
    recommendation = add_recommendation(workflow)

    summary = TechnicianCaseSummary(workflow)

    findings = summary.findings
    root_causes = summary.root_causes
    recommendations = summary.recommendations

    findings.clear()
    root_causes.clear()
    recommendations.clear()

    findings.append(finding)
    root_causes.append(root_cause)
    recommendations.append(recommendation)

    assert workflow.case.findings == [finding]
    assert workflow.case.root_causes == [root_cause]
    assert workflow.case.recommendations == [recommendation]

    assert summary.findings == [finding]
    assert summary.root_causes == [root_cause]
    assert summary.recommendations == [recommendation]

    assert summary.findings is not findings
    assert summary.root_causes is not root_causes
    assert summary.recommendations is not recommendations


