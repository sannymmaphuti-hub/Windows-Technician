from engine.diagnostic_case import DiagnosticCase
from engine.recommendation import Recommendation
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


def build_recommendation():
    return Recommendation(
        recommendation_type="MEMORY_REVIEW",
        category="MEMORY",
        priority="HIGH",
        description="Review applications using excessive memory.",
        rationale="Sustained memory pressure was detected.",
    )


def set_recommendation(workflow, recommendation):
    workflow.case.set_recommendations([recommendation])


def recommendation_signature(recommendation):
    return (
        recommendation.recommendation_type,
        recommendation.category,
        recommendation.priority,
        recommendation.description,
        recommendation.rationale,
    )


def case_recommendation_signatures(workflow):
    return [
        recommendation_signature(recommendation)
        for recommendation in workflow.case.recommendations
    ]


def test_closure_does_not_create_recommendation():
    workflow = build_workflow()

    resolve_workflow(workflow)
    recommendations_before = case_recommendation_signatures(workflow)

    build_closure(workflow)

    assert case_recommendation_signatures(workflow) == recommendations_before


def test_closure_does_not_remove_existing_recommendation():
    workflow = build_workflow()

    recommendation = build_recommendation()
    expected_signature = recommendation_signature(recommendation)

    set_recommendation(workflow, recommendation)

    resolve_workflow(workflow)
    recommendations_before = case_recommendation_signatures(workflow)

    build_closure(workflow)

    assert case_recommendation_signatures(workflow) == recommendations_before
    assert expected_signature in case_recommendation_signatures(workflow)


def test_closure_does_not_replace_existing_recommendation():
    workflow = build_workflow()

    recommendation = build_recommendation()
    expected_signature = recommendation_signature(recommendation)

    set_recommendation(workflow, recommendation)

    resolve_workflow(workflow)
    build_closure(workflow)

    assert case_recommendation_signatures(workflow) == [expected_signature]


def test_closure_does_not_change_recommendation_count():
    workflow = build_workflow()

    set_recommendation(workflow, build_recommendation())

    resolve_workflow(workflow)
    count_before = len(workflow.case.recommendations)

    build_closure(workflow)

    assert len(workflow.case.recommendations) == count_before


def test_closure_does_not_change_case_evidence():
    workflow = build_workflow()

    set_recommendation(workflow, build_recommendation())

    resolve_workflow(workflow)

    evidence_before = dict(workflow.case.evidence)

    build_closure(workflow)

    assert workflow.case.evidence == evidence_before


def test_closure_does_not_appear_as_case_recommendation():
    workflow = build_workflow()

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert all(
        value is not closure
        for value in workflow.case.recommendations
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


def test_closure_does_not_change_recommendations_after_reopen():
    workflow = build_workflow()

    recommendation = build_recommendation()
    expected_signature = recommendation_signature(recommendation)

    set_recommendation(workflow, recommendation)

    resolve_workflow(workflow)
    build_closure(workflow)

    workflow.reopen()

    assert expected_signature in case_recommendation_signatures(workflow)
    assert len(workflow.case.recommendations) == 1


def test_closure_remains_separate_from_recommendation_identity():
    workflow = build_workflow()

    recommendation = build_recommendation()
    expected_signature = recommendation_signature(recommendation)

    set_recommendation(workflow, recommendation)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert closure is not recommendation
    assert expected_signature in case_recommendation_signatures(workflow)


def test_multiple_closures_do_not_duplicate_recommendations():
    workflow = build_workflow()

    recommendation = build_recommendation()
    expected_signature = recommendation_signature(recommendation)

    set_recommendation(workflow, recommendation)

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
    assert case_recommendation_signatures(workflow) == [expected_signature]
    assert len(workflow.case.recommendations) == 1


def test_closure_does_not_become_recommendation_description():
    workflow = build_workflow()

    recommendation = build_recommendation()
    set_recommendation(workflow, recommendation)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert workflow.case.recommendations[0].description != closure.reason


def test_closure_does_not_mutate_recommendation_metadata():
    workflow = build_workflow()

    recommendation = build_recommendation()
    expected_signature = recommendation_signature(recommendation)

    set_recommendation(workflow, recommendation)

    resolve_workflow(workflow)

    build_closure(workflow)

    assert case_recommendation_signatures(workflow) == [expected_signature]


def test_closure_does_not_change_case_recommendation_count_after_reopen():
    workflow = build_workflow()

    set_recommendation(workflow, build_recommendation())

    resolve_workflow(workflow)

    build_closure(workflow)
    workflow.reopen()

    assert len(workflow.case.recommendations) == 1


def test_closure_is_not_required_for_recommendation_to_exist():
    workflow = build_workflow()

    recommendation = build_recommendation()
    expected_signature = recommendation_signature(recommendation)

    set_recommendation(workflow, recommendation)

    resolve_workflow(workflow)

    assert expected_signature in case_recommendation_signatures(workflow)
    assert workflow.case.recommendations


def test_case_recommendation_does_not_create_closure():
    workflow = build_workflow()

    recommendation = build_recommendation()
    set_recommendation(workflow, recommendation)

    assert workflow.state.value == "OPEN"
    assert workflow.case.recommendations