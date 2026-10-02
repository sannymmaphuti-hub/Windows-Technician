import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.recommendation import Recommendation
from engine.technician_recommendation_detail import (
    TechnicianRecommendationDetail,
)
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_workflow import TechnicianWorkflow


def create_detail():
    case = DiagnosticCase()

    recommendation = Recommendation(
        "MEMORY_REVIEW",
        "MEMORY",
        "HIGH",
        "Review memory usage and reduce unnecessary processes.",
        "Memory pressure indicates that available memory "
        "is consistently low.",
    )

    case.recommendations.append(recommendation)

    workflow = TechnicianWorkflow(case)

    history = TechnicianRecoveryCycleHistory(
        workflow
    )

    detail = TechnicianRecommendationDetail(
        workflow,
        history,
        recommendation,
    )

    return detail, workflow, history, recommendation


def test_requires_workflow():
    _, _, history, recommendation = create_detail()

    with pytest.raises(ValueError):
        TechnicianRecommendationDetail(
            None,
            history,
            recommendation,
        )


def test_requires_cycle_history():
    _, workflow, _, recommendation = create_detail()

    with pytest.raises(ValueError):
        TechnicianRecommendationDetail(
            workflow,
            None,
            recommendation,
        )


def test_requires_matching_cycle_history():
    _, workflow, _, recommendation = create_detail()

    other_case = DiagnosticCase()
    other_workflow = TechnicianWorkflow(other_case)
    other_history = TechnicianRecoveryCycleHistory(
        other_workflow
    )

    with pytest.raises(ValueError):
        TechnicianRecommendationDetail(
            workflow,
            other_history,
            recommendation,
        )


def test_requires_recommendation():
    _, workflow, history, _ = create_detail()

    with pytest.raises(ValueError):
        TechnicianRecommendationDetail(
            workflow,
            history,
            None,
        )


def test_recommendation_must_belong_to_workflow_case():
    _, workflow, history, _ = create_detail()

    other_recommendation = Recommendation(
        "CPU_REVIEW",
        "CPU",
        "MEDIUM",
        "Review sustained CPU usage.",
        "CPU activity is consistently elevated.",
    )

    with pytest.raises(ValueError):
        TechnicianRecommendationDetail(
            workflow,
            history,
            other_recommendation,
        )


def test_exposes_workflow():
    detail, workflow, _, _ = create_detail()

    assert detail.workflow is workflow


def test_exposes_cycle_history():
    detail, _, history, _ = create_detail()

    assert detail.cycle_history is history


def test_exposes_recommendation():
    detail, _, _, recommendation = create_detail()

    assert detail.recommendation is recommendation


def test_exposes_recommendation_type():
    detail, _, _, recommendation = create_detail()

    assert (
        detail.recommendation_type
        == recommendation.recommendation_type
    )


def test_exposes_category():
    detail, _, _, recommendation = create_detail()

    assert detail.category == recommendation.category


def test_exposes_priority():
    detail, _, _, recommendation = create_detail()

    assert detail.priority == recommendation.priority


def test_exposes_description():
    detail, _, _, recommendation = create_detail()

    assert detail.description == recommendation.description


def test_exposes_rationale():
    detail, _, _, recommendation = create_detail()

    assert detail.rationale == recommendation.rationale


def test_recommendation_reference_is_preserved():
    detail, _, _, recommendation = create_detail()

    assert detail.recommendation is recommendation