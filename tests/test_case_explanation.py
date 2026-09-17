import pytest

from engine.network_diagnostic_case_synthesis import (
    NetworkDiagnosticCase,
)


def create_case(
    observations=None,
    signals=None,
    findings=None,
    correlations=None,
    candidates=None,
    evaluations=None,
    primary_cause=None,
    confidences=None,
    explanations=None,
    recommendations=None,
):
    return NetworkDiagnosticCase(
        observations=observations or [],
        signals=signals or [],
        findings=findings or [],
        correlations=correlations or [],
        candidates=candidates or [],
        evaluations=evaluations or [],
        primary_cause=primary_cause,
        confidences=confidences or [],
        explanations=explanations or [],
        recommendations=recommendations or [],
    )


def test_case_explanation_layer_can_be_created():
    from engine.case_explanation import CaseExplanation

    explanation = CaseExplanation()

    assert explanation is not None


def test_case_explanation_supports_user_audience():
    from engine.case_explanation import CaseExplanation

    explanation = CaseExplanation()

    assert explanation.is_supported_audience("USER")


def test_case_explanation_supports_technician_audience():
    from engine.case_explanation import CaseExplanation

    explanation = CaseExplanation()

    assert explanation.is_supported_audience(
        "TECHNICIAN"
    )


def test_case_explanation_rejects_unknown_audience():
    from engine.case_explanation import CaseExplanation

    explanation = CaseExplanation()

    assert not explanation.is_supported_audience(
        "UNKNOWN"
    )


def test_case_explanation_rejects_invalid_case():
    from engine.case_explanation import CaseExplanation

    explanation = CaseExplanation()

    with pytest.raises(ValueError):
        explanation.explain(
            None,
            "USER",
        )


def test_case_explanation_rejects_invalid_audience():
    from engine.case_explanation import CaseExplanation

    explanation = CaseExplanation()

    case = create_case()

    with pytest.raises(ValueError):
        explanation.explain(
            case,
            "UNKNOWN",
        )


def test_case_explanation_accepts_network_diagnostic_case():
    from engine.case_explanation import CaseExplanation

    explanation = CaseExplanation()

    case = create_case()

    result = explanation.explain(
        case,
        "USER",
    )

    assert result is not None


def test_user_and_technician_explanations_are_distinct():
    from engine.case_explanation import CaseExplanation

    explanation = CaseExplanation()

    case = create_case()

    user_result = explanation.explain(
        case,
        "USER",
    )

    technician_result = explanation.explain(
        case,
        "TECHNICIAN",
    )

    assert user_result != technician_result


def test_case_explanation_does_not_mutate_case():
    from engine.case_explanation import CaseExplanation

    explanation = CaseExplanation()

    case = create_case()

    original_observations = list(
        case.observations
    )
    original_findings = list(
        case.findings
    )
    original_candidates = list(
        case.candidates
    )
    original_recommendations = list(
        case.recommendations
    )

    explanation.explain(
        case,
        "USER",
    )

    assert case.observations == (
        original_observations
    )

    assert case.findings == (
        original_findings
    )

    assert case.candidates == (
        original_candidates
    )

    assert case.recommendations == (
        original_recommendations
    )

def test_user_explanation_reflects_primary_cause():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution is failing.",
    )

    case = create_case(
        candidates=[candidate],
        primary_cause=candidate,
    )

    explanation = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
       explanation.summary
        + " "
        + explanation.details
    ).lower()

    assert "dns" in text


def test_technician_explanation_reflects_primary_cause():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution is failing.",
    )

    case = create_case(
        candidates=[candidate],
        primary_cause=candidate,
    )

    explanation = CaseExplanation().explain(
        case,
        "TECHNICIAN",
    )

    text = (
       explanation.summary
        + " "
        + explanation.details
    ).lower()

    assert "dns_failure" in text


def test_user_explanation_reflects_recommendations():
    from engine.case_explanation import CaseExplanation

    recommendation = {
        "recommendation_type": "CHECK_DNS",
        "description": "Check DNS configuration.",
    }

    case = create_case(
        recommendations=[recommendation],
    )

    explanation = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
       explanation.summary
        + " "
        + explanation.details
    ).lower()

    assert "dns" in text


def test_technician_explanation_reports_case_structure():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        observations=["observation"],
        signals=["signal"],
        findings=["finding"],
        correlations=["correlation"],
        candidates=["candidate"],
        evaluations=["evaluation"],
        confidences=["confidence"],
        recommendations=["recommendation"],
    )

    explanation = CaseExplanation().explain(
        case,
        "TECHNICIAN",
    )

    details = explanation.details.lower()

    assert "observations" in details
    assert "signals" in details
    assert "findings" in details
    assert "correlations" in details
    assert "evaluations" in details
    assert "confidence" in details
    assert "recommendations" in details

def test_case_explanation_returns_explanation_object():
    from engine.case_explanation import CaseExplanation
    from engine.explanation import Explanation

    case = create_case()

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    assert isinstance(
        result,
        Explanation,
    )


def test_case_explanation_sets_user_subject():
    from engine.case_explanation import CaseExplanation
    from engine.explanation import Explanation

    case = create_case()

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    assert isinstance(result, Explanation)
    assert result.subject == "DIAGNOSTIC_CASE"


def test_case_explanation_sets_technician_subject():
    from engine.case_explanation import CaseExplanation
    from engine.explanation import Explanation

    case = create_case()

    result = CaseExplanation().explain(
        case,
        "TECHNICIAN",
    )

    assert isinstance(result, Explanation)
    assert result.subject == "DIAGNOSTIC_CASE"


def test_case_explanation_preserves_audience_difference():
    from engine.case_explanation import CaseExplanation
    from engine.explanation import Explanation

    case = create_case()

    user_result = CaseExplanation().explain(
        case,
        "USER",
    )

    technician_result = CaseExplanation().explain(
        case,
        "TECHNICIAN",
    )

    assert isinstance(user_result, Explanation)
    assert isinstance(technician_result, Explanation)

    assert (
        user_result.summary
        != technician_result.summary
    )

    assert (
        user_result.details
        != technician_result.details
    )


def test_case_explanation_can_be_serialized_as_evidence():
    from engine.case_explanation import CaseExplanation

    case = create_case()

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    evidence = result.to_evidence()

    assert evidence["subject"] == (
        "DIAGNOSTIC_CASE"
    )

    assert "summary" in evidence
    assert "details" in evidence

def test_case_explanation_propagates_confidence_level():
    from engine.case_explanation import CaseExplanation
    from engine.confidence import Confidence

    confidence = Confidence(
        subject="DNS_FAILURE",
        level="HIGH",
        explanation="Multiple signals support the diagnosis.",
    )

    case = create_case(
        confidences=[confidence],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    assert result.confidence == "HIGH"


def test_case_explanation_preserves_medium_confidence():
    from engine.case_explanation import CaseExplanation
    from engine.confidence import Confidence

    confidence = Confidence(
        subject="DNS_FAILURE",
        level="MEDIUM",
        explanation="Some evidence supports the diagnosis.",
    )

    case = create_case(
        confidences=[confidence],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    assert result.confidence == "MEDIUM"


def test_case_explanation_preserves_low_confidence():
    from engine.case_explanation import CaseExplanation
    from engine.confidence import Confidence

    confidence = Confidence(
        subject="DNS_FAILURE",
        level="LOW",
        explanation="Limited evidence supports the diagnosis.",
    )

    case = create_case(
        confidences=[confidence],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    assert result.confidence == "LOW"


def test_case_explanation_has_no_confidence_without_confidence_result():
    from engine.case_explanation import CaseExplanation

    case = create_case()

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    assert result.confidence is None

def test_user_explanation_does_not_dump_technical_case_structure():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        observations=["gateway observation"],
        signals=["dns signal"],
        findings=["network finding"],
        correlations=["network correlation"],
        candidates=["technical candidate"],
        evaluations=["technical evaluation"],
        recommendations=[
            {
                "recommendation_type": "CHECK_DNS",
                "description": "Check your DNS settings.",
            }
        ],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "gateway observation" not in text
    assert "dns signal" not in text
    assert "network finding" not in text
    assert "network correlation" not in text
    assert "technical candidate" not in text
    assert "technical evaluation" not in text


def test_technician_explanation_exposes_reasoning_categories():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        observations=["observation"],
        signals=["signal"],
        findings=["finding"],
        correlations=["correlation"],
        candidates=["candidate"],
        evaluations=["evaluation"],
        confidences=["confidence"],
        recommendations=["recommendation"],
    )

    result = CaseExplanation().explain(
        case,
        "TECHNICIAN",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "observations" in text
    assert "signals" in text
    assert "findings" in text
    assert "correlations" in text
    assert "root-cause candidates" in text
    assert "evaluations" in text
    assert "confidence" in text
    assert "recommendations" in text


def test_audience_does_not_change_case_confidence():
    from engine.case_explanation import CaseExplanation
    from engine.confidence import Confidence

    confidence = Confidence(
        subject="DNS_FAILURE",
        level="HIGH",
        explanation="Strong supporting evidence.",
    )

    case = create_case(
        confidences=[confidence],
    )

    explanation = CaseExplanation()

    user_result = explanation.explain(
        case,
        "USER",
    )

    technician_result = explanation.explain(
        case,
        "TECHNICIAN",
    )

    assert user_result.confidence == "HIGH"
    assert technician_result.confidence == "HIGH"

def test_user_explanation_contains_action_and_meaning():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution is failing.",
    )

    case = create_case(
        primary_cause=candidate,
        recommendations=[
            {
                "recommendation_type": "CHECK_DNS",
                "description": "Check your DNS settings.",
            }
        ],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "dns failure" in text
    assert "check your dns settings" in text
    assert "may" in text or "could" in text


def test_user_explanation_does_not_require_technical_knowledge():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution is failing.",
    )

    case = create_case(
        primary_cause=candidate,
        recommendations=[
            {
                "recommendation_type": "CHECK_DNS",
                "description": "Check your DNS settings.",
            }
        ],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "root-cause" not in text
    assert "correlation" not in text
    assert "evaluation" not in text
    assert "observation" not in text
    assert "signal" not in text


def test_technician_explanation_contains_case_reasoning_context():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution is failing.",
    )

    case = create_case(
        primary_cause=candidate,
        observations=["gateway reachable"],
        signals=["dns failure signal"],
        findings=["dns finding"],
        correlations=["dns correlation"],
        candidates=[candidate],
        evaluations=["dns evaluation"],
        confidences=["confidence"],
        recommendations=[
            {
                "recommendation_type": "CHECK_DNS",
                "description": "Check DNS configuration.",
            }
        ],
    )

    result = CaseExplanation().explain(
        case,
        "TECHNICIAN",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "dns_failure" in text
    assert "observations" in text
    assert "signals" in text
    assert "findings" in text
    assert "correlations" in text
    assert "root-cause candidates" in text
    assert "evaluations" in text
    assert "confidence" in text
    assert "recommendations" in text


def test_user_and_technician_explanations_preserve_same_primary_cause():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution is failing.",
    )

    case = create_case(
        primary_cause=candidate,
        candidates=[candidate],
    )

    explanation = CaseExplanation()

    user_result = explanation.explain(
        case,
        "USER",
    )

    technician_result = explanation.explain(
        case,
        "TECHNICIAN",
    )

    assert "dns failure" in (
        user_result.summary.lower()
        + " "
        + user_result.details.lower()
    )

    assert "dns_failure" in (
        technician_result.summary.lower()
        + " "
        + technician_result.details.lower()
    )

def test_user_explanation_preserves_multiple_recommendations():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        recommendations=[
            {
                "recommendation_type": "CHECK_DNS",
                "description": "Check your DNS settings.",
            },
            {
                "recommendation_type": "RESTART_ROUTER",
                "description": "Restart your router.",
            },
        ],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "check your dns settings" in text
    assert "restart your router" in text


def test_technician_explanation_preserves_multiple_recommendations():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        recommendations=[
            {
                "recommendation_type": "CHECK_DNS",
                "description": "Check DNS configuration.",
            },
            {
                "recommendation_type": "RESTART_ROUTER",
                "description": "Restart the network router.",
            },
        ],
    )

    result = CaseExplanation().explain(
        case,
        "TECHNICIAN",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "check dns configuration" in text
    assert "restart the network router" in text


def test_empty_recommendations_do_not_create_recommendation_text():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        recommendations=[],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "recommended action:" not in text

def test_user_explanation_supports_recommendation_objects():
    from engine.case_explanation import CaseExplanation
    from engine.recommendation import Recommendation

    first = Recommendation(
        recommendation_type="CHECK_DNS",
        category="NETWORK",
        priority="HIGH",
        description="Check your DNS settings.",
        rationale="DNS configuration should be verified.",
    )

    second = Recommendation(
        recommendation_type="RESTART_ROUTER",
        category="NETWORK",
        priority="MEDIUM",
        description="Restart your router.",
        rationale="The router may need to refresh its network state.",
    )

    case = create_case(
        recommendations=[
            first,
            second,
        ],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "check your dns settings" in text
    assert "restart your router" in text


def test_technician_explanation_supports_recommendation_objects():
    from engine.case_explanation import CaseExplanation
    from engine.recommendation import Recommendation

    recommendation = Recommendation(
        recommendation_type="CHECK_DNS",
        category="NETWORK",
        priority="HIGH",
        description="Check DNS configuration.",
        rationale="DNS configuration should be verified.",
    )

    case = create_case(
        recommendations=[recommendation],
    )

    result = CaseExplanation().explain(
        case,
        "TECHNICIAN",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "check dns configuration" in text


def test_user_explanation_preserves_recommendation_order():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        recommendations=[
            {
                "recommendation_type": "FIRST_ACTION",
                "description": "First diagnostic action.",
            },
            {
                "recommendation_type": "SECOND_ACTION",
                "description": "Second diagnostic action.",
            },
            {
                "recommendation_type": "THIRD_ACTION",
                "description": "Third diagnostic action.",
            },
        ],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    first_position = text.index(
        "first diagnostic action"
    )
    second_position = text.index(
        "second diagnostic action"
    )
    third_position = text.index(
        "third diagnostic action"
    )

    assert first_position < second_position
    assert second_position < third_position

def test_empty_case_produces_safe_user_explanation():
    from engine.case_explanation import CaseExplanation

    case = create_case()

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    assert result.subject == "DIAGNOSTIC_CASE"
    assert result.summary
    assert result.details
    assert result.confidence is None


def test_empty_case_produces_safe_technician_explanation():
    from engine.case_explanation import CaseExplanation

    case = create_case()

    result = CaseExplanation().explain(
        case,
        "TECHNICIAN",
    )

    assert result.subject == "DIAGNOSTIC_CASE"
    assert result.summary
    assert result.details
    assert "none identified" in result.details.lower()


def test_partial_case_without_primary_cause_does_not_invent_cause():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        observations=["gateway reachable"],
        signals=["dns signal"],
        findings=["network finding"],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "dns failure" not in text
    assert "primary cause" not in text


def test_primary_cause_without_recommendation_remains_uncertain():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution is failing.",
    )

    case = create_case(
        primary_cause=candidate,
        candidates=[candidate],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "dns failure" in text
    assert "may" in text or "could" in text
    assert "recommended action:" not in text


def test_recommendation_without_primary_cause_does_not_invent_cause():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        recommendations=[
            {
                "recommendation_type": "CHECK_DNS",
                "description": "Check your DNS settings.",
            }
        ],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "check your dns settings" in text
    assert "dns failure" not in text
    assert "primary cause" not in text


def test_partial_case_remains_valid_for_technician():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        observations=["gateway reachable"],
        findings=["network finding"],
    )

    result = CaseExplanation().explain(
        case,
        "TECHNICIAN",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert result.subject == "DIAGNOSTIC_CASE"
    assert "none identified" in text
    assert "observations" in text
    assert "findings" in text

def test_user_and_technician_preserve_same_primary_cause():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution is failing.",
    )

    case = create_case(
        primary_cause=candidate,
        candidates=[candidate],
    )

    layer = CaseExplanation()

    user_result = layer.explain(
        case,
        "USER",
    )

    technician_result = layer.explain(
        case,
        "TECHNICIAN",
    )

    assert "dns failure" in (
        user_result.summary.lower()
        + " "
        + user_result.details.lower()
    )

    assert "dns_failure" in (
        technician_result.details.lower()
    )


def test_user_and_technician_preserve_same_confidence():
    from engine.case_explanation import CaseExplanation
    from engine.confidence import Confidence

    case = create_case(
        confidences=[
            Confidence(
                subject="DNS_FAILURE",
                level="HIGH",
                explanation="Strong supporting evidence.",
            )
        ],
    )

    layer = CaseExplanation()

    user_result = layer.explain(
        case,
        "USER",
    )

    technician_result = layer.explain(
        case,
        "TECHNICIAN",
    )

    assert user_result.confidence == "HIGH"
    assert technician_result.confidence == "HIGH"


def test_user_and_technician_preserve_all_recommendations():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        recommendations=[
            {
                "recommendation_type": "CHECK_DNS",
                "description": "Check your DNS settings.",
            },
            {
                "recommendation_type": "RESTART_ROUTER",
                "description": "Restart your router.",
            },
        ],
    )

    layer = CaseExplanation()

    user_result = layer.explain(
        case,
        "USER",
    )

    technician_result = layer.explain(
        case,
        "TECHNICIAN",
    )

    user_text = (
        user_result.summary.lower()
        + " "
        + user_result.details.lower()
    )

    technician_text = (
        technician_result.summary.lower()
        + " "
        + technician_result.details.lower()
    )

    assert "check your dns settings" in user_text
    assert "restart your router" in user_text

    assert "check your dns settings" in technician_text
    assert "restart your router" in technician_text


def test_user_explanation_does_not_invent_primary_cause():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        observations=["gateway reachable"],
        signals=["network signal"],
        findings=["network finding"],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "dns failure" not in text
    assert "hardware failure" not in text
    assert "memory failure" not in text


def test_user_explanation_does_not_turn_uncertainty_into_certainty():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution may be failing.",
    )

    case = create_case(
        primary_cause=candidate,
        candidates=[candidate],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "may" in text or "could" in text
    assert "definitely" not in text
    assert "confirmed" not in result.summary.lower()

def test_explanation_does_not_mutate_underlying_case():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        observations=["gateway reachable"],
        signals=["dns signal"],
        findings=["network finding"],
        recommendations=[
            {
                "recommendation_type": "CHECK_DNS",
                "description": "Check your DNS settings.",
            }
        ],
    )

    original_observations = list(case.observations)
    original_signals = list(case.signals)
    original_findings = list(case.findings)
    original_recommendations = list(case.recommendations)

    layer = CaseExplanation()

    layer.explain(case, "USER")
    layer.explain(case, "TECHNICIAN")

    assert case.observations == original_observations
    assert case.signals == original_signals
    assert case.findings == original_findings
    assert case.recommendations == original_recommendations

def test_user_explanation_serializes_to_evidence():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        recommendations=[
            {
                "recommendation_type": "CHECK_DNS",
                "description": "Check your DNS settings.",
            }
        ],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    evidence = result.to_evidence()

    assert isinstance(evidence, dict)
    assert evidence["subject"] == "DIAGNOSTIC_CASE"
    assert evidence["summary"]
    assert evidence["details"]


def test_technician_explanation_serializes_to_evidence():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        observations=["gateway reachable"],
        findings=["network finding"],
    )

    result = CaseExplanation().explain(
        case,
        "TECHNICIAN",
    )

    evidence = result.to_evidence()

    assert isinstance(evidence, dict)
    assert evidence["subject"] == "DIAGNOSTIC_CASE"
    assert evidence["summary"]
    assert evidence["details"]


def test_explanation_serialization_preserves_confidence():
    from engine.case_explanation import CaseExplanation
    from engine.confidence import Confidence

    case = create_case(
        confidences=[
            Confidence(
                subject="DNS_FAILURE",
                level="HIGH",
                explanation="Strong supporting evidence.",
            )
        ],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    evidence = result.to_evidence()

    assert evidence["confidence"] == "HIGH"


def test_explanation_serialization_does_not_expose_case_structure():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        observations=["gateway reachable"],
        signals=["dns signal"],
        findings=["network finding"],
    )

    result = CaseExplanation().explain(
        case,
        "TECHNICIAN",
    )

    evidence = result.to_evidence()

    assert "observations" not in evidence
    assert "signals" not in evidence
    assert "findings" not in evidence
    assert "correlations" not in evidence
    assert "candidates" not in evidence
    assert "evaluations" not in evidence


def test_explanation_serialization_does_not_mutate_explanation():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        recommendations=[
            {
                "recommendation_type": "CHECK_DNS",
                "description": "Check your DNS settings.",
            }
        ],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    before = (
        result.subject,
        result.summary,
        result.details,
        result.confidence,
    )

    evidence = result.to_evidence()

    after = (
        result.subject,
        result.summary,
        result.details,
        result.confidence,
    )

    assert evidence
    assert before == after


def test_explanation_serialization_does_not_mutate_case():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        observations=["gateway reachable"],
        signals=["dns signal"],
        findings=["network finding"],
        recommendations=[
            {
                "recommendation_type": "CHECK_DNS",
                "description": "Check your DNS settings.",
            }
        ],
    )

    before = (
        list(case.observations),
        list(case.signals),
        list(case.findings),
        list(case.recommendations),
    )

    result = CaseExplanation().explain(
        case,
        "TECHNICIAN",
    )

    result.to_evidence()

    after = (
        list(case.observations),
        list(case.signals),
        list(case.findings),
        list(case.recommendations),
    )

    assert before == after

def test_same_case_produces_same_user_explanation():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution is failing.",
    )

    case = create_case(
        primary_cause=candidate,
        candidates=[candidate],
        recommendations=[
            {
                "recommendation_type": "CHECK_DNS",
                "description": "Check your DNS settings.",
            }
        ],
    )

    layer = CaseExplanation()

    first = layer.explain(case, "USER")
    second = layer.explain(case, "USER")

    assert first.to_evidence() == second.to_evidence()


def test_same_case_produces_same_technician_explanation():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution is failing.",
    )

    case = create_case(
        primary_cause=candidate,
        candidates=[candidate],
        recommendations=[
            {
                "recommendation_type": "CHECK_DNS",
                "description": "Check your DNS settings.",
            }
        ],
    )

    layer = CaseExplanation()

    first = layer.explain(case, "TECHNICIAN")
    second = layer.explain(case, "TECHNICIAN")

    assert first.to_evidence() == second.to_evidence()


def test_user_explanation_is_not_affected_by_previous_technician_explanation():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution is failing.",
    )

    case = create_case(
        primary_cause=candidate,
        candidates=[candidate],
    )

    layer = CaseExplanation()

    direct_user = layer.explain(
        case,
        "USER",
    )

    layer.explain(
        case,
        "TECHNICIAN",
    )

    after_technician = layer.explain(
        case,
        "USER",
    )

    assert (
        direct_user.to_evidence()
        == after_technician.to_evidence()
    )


def test_technician_explanation_is_not_affected_by_previous_user_explanation():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution is failing.",
    )

    case = create_case(
        primary_cause=candidate,
        candidates=[candidate],
    )

    layer = CaseExplanation()

    direct_technician = layer.explain(
        case,
        "TECHNICIAN",
    )

    layer.explain(
        case,
        "USER",
    )

    after_user = layer.explain(
        case,
        "TECHNICIAN",
    )

    assert (
        direct_technician.to_evidence()
        == after_user.to_evidence()
    )


def test_repeated_explanation_does_not_change_case():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution is failing.",
    )

    case = create_case(
        primary_cause=candidate,
        candidates=[candidate],
    )

    before = (
        list(case.observations),
        list(case.signals),
        list(case.findings),
        list(case.correlations),
        list(case.candidates),
        list(case.evaluations),
        case.primary_cause,
        list(case.confidences),
        list(case.explanations),
        list(case.recommendations),
    )

    layer = CaseExplanation()

    layer.explain(case, "USER")
    layer.explain(case, "TECHNICIAN")
    layer.explain(case, "USER")
    layer.explain(case, "TECHNICIAN")

    after = (
        list(case.observations),
        list(case.signals),
        list(case.findings),
        list(case.correlations),
        list(case.candidates),
        list(case.evaluations),
        case.primary_cause,
        list(case.confidences),
        list(case.explanations),
        list(case.recommendations),
    )

    assert before == after

def test_case_explanation_consumes_existing_case_without_requiring_pipeline():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        observations=["gateway reachable"],
        findings=["network finding"],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    assert result.subject == "DIAGNOSTIC_CASE"


def test_case_explanation_does_not_replace_primary_cause():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution is failing.",
    )

    case = create_case(
        primary_cause=candidate,
        candidates=[candidate],
    )

    original = case.primary_cause

    CaseExplanation().explain(
        case,
        "USER",
    )

    assert case.primary_cause is original


def test_case_explanation_does_not_replace_confidence():
    from engine.case_explanation import CaseExplanation
    from engine.confidence import Confidence

    confidence = Confidence(
        subject="DNS_FAILURE",
        level="HIGH",
        explanation="Strong supporting evidence.",
    )

    case = create_case(
        confidences=[confidence],
    )

    original = case.confidences[0]

    CaseExplanation().explain(
        case,
        "TECHNICIAN",
    )

    assert case.confidences[0] is original


def test_case_explanation_does_not_replace_recommendations():
    from engine.case_explanation import CaseExplanation

    recommendation = {
        "recommendation_type": "CHECK_DNS",
        "description": "Check your DNS settings.",
    }

    case = create_case(
        recommendations=[recommendation],
    )

    original = case.recommendations[0]

    CaseExplanation().explain(
        case,
        "USER",
    )

    assert case.recommendations[0] is original


def test_case_explanation_does_not_add_findings():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        findings=["existing finding"],
    )

    original = list(case.findings)

    CaseExplanation().explain(
        case,
        "TECHNICIAN",
    )

    assert case.findings == original


def test_case_explanation_does_not_add_recommendations():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        findings=["existing finding"],
    )

    original = list(case.recommendations)

    CaseExplanation().explain(
        case,
        "USER",
    )

    assert case.recommendations == original

def test_user_then_technician_preserves_case_contents():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution is failing.",
    )

    case = create_case(
        observations=["gateway reachable"],
        signals=["dns signal"],
        findings=["network finding"],
        candidates=[candidate],
        primary_cause=candidate,
        recommendations=[
            {
                "recommendation_type": "CHECK_DNS",
                "description": "Check your DNS settings.",
            }
        ],
    )

    before = (
        list(case.observations),
        list(case.signals),
        list(case.findings),
        list(case.candidates),
        case.primary_cause,
        list(case.recommendations),
    )

    layer = CaseExplanation()

    layer.explain(case, "USER")
    layer.explain(case, "TECHNICIAN")

    after = (
        list(case.observations),
        list(case.signals),
        list(case.findings),
        list(case.candidates),
        case.primary_cause,
        list(case.recommendations),
    )

    assert before == after


def test_technician_then_user_preserves_case_contents():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution is failing.",
    )

    case = create_case(
        observations=["gateway reachable"],
        signals=["dns signal"],
        findings=["network finding"],
        candidates=[candidate],
        primary_cause=candidate,
        recommendations=[
            {
                "recommendation_type": "CHECK_DNS",
                "description": "Check your DNS settings.",
            }
        ],
    )

    before = (
        list(case.observations),
        list(case.signals),
        list(case.findings),
        list(case.candidates),
        case.primary_cause,
        list(case.recommendations),
    )

    layer = CaseExplanation()

    layer.explain(case, "TECHNICIAN")
    layer.explain(case, "USER")

    after = (
        list(case.observations),
        list(case.signals),
        list(case.findings),
        list(case.candidates),
        case.primary_cause,
        list(case.recommendations),
    )

    assert before == after


def test_audience_selection_does_not_change_primary_cause_identity():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution is failing.",
    )

    case = create_case(
        primary_cause=candidate,
        candidates=[candidate],
    )

    layer = CaseExplanation()

    layer.explain(case, "USER")
    user_primary_cause = case.primary_cause

    layer.explain(case, "TECHNICIAN")
    technician_primary_cause = case.primary_cause

    assert user_primary_cause is candidate
    assert technician_primary_cause is candidate


def test_audience_selection_does_not_change_recommendation_identity():
    from engine.case_explanation import CaseExplanation

    recommendation = {
        "recommendation_type": "CHECK_DNS",
        "description": "Check your DNS settings.",
    }

    case = create_case(
        recommendations=[recommendation],
    )

    layer = CaseExplanation()

    layer.explain(case, "USER")
    user_recommendation = case.recommendations[0]

    layer.explain(case, "TECHNICIAN")
    technician_recommendation = case.recommendations[0]

    assert user_recommendation is recommendation
    assert technician_recommendation is recommendation

def test_user_explanation_does_not_expose_raw_observations():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        observations=[
            "gateway_reachable=True",
            "dns_resolution=False",
        ],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "gateway_reachable=true" not in text
    assert "dns_resolution=false" not in text


def test_user_explanation_does_not_expose_raw_signals():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        signals=[
            "dns_failure_signal",
            "internet_unreachable_signal",
        ],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "dns_failure_signal" not in text
    assert "internet_unreachable_signal" not in text


def test_user_explanation_does_not_expose_candidate_structure():
    from engine.case_explanation import CaseExplanation
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution is failing.",
    )

    case = create_case(
        candidates=[candidate],
        primary_cause=candidate,
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "rootcausecandidate" not in text
    assert "category=" not in text
    assert "cause_type=" not in text


def test_technician_explanation_retains_technical_reasoning_context():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        observations=["gateway reachable"],
        signals=["dns signal"],
        findings=["network finding"],
        correlations=["network correlation"],
        candidates=["dns candidate"],
        evaluations=["dns evaluation"],
    )

    result = CaseExplanation().explain(
        case,
        "TECHNICIAN",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "observations" in text
    assert "signals" in text
    assert "findings" in text
    assert "correlations" in text
    assert "root-cause candidates" in text
    assert "evaluations" in text

def test_user_explanation_does_not_claim_technician_required_from_low_confidence():
    from engine.case_explanation import CaseExplanation
    from engine.confidence import Confidence
    from engine.root_cause_candidate import RootCauseCandidate

    candidate = RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation="DNS resolution may be failing.",
    )

    confidence = Confidence(
        subject="DNS_FAILURE",
        level="LOW",
        explanation="Limited evidence supports the diagnosis.",
    )

    case = create_case(
        candidates=[candidate],
        primary_cause=candidate,
        confidences=[confidence],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "technician is required" not in text
    assert "technician required" not in text


def test_user_explanation_describes_uncertainty_when_no_primary_cause_exists():
    from engine.case_explanation import CaseExplanation
    from engine.confidence import Confidence

    confidence = Confidence(
        subject="DNS_FAILURE",
        level="LOW",
        explanation="Limited evidence supports the diagnosis.",
    )

    case = create_case(
        confidences=[confidence],
        recommendations=[
            {
                "recommendation_type": "CHECK_DNS",
                "description": "Check your DNS settings.",
            }
        ],
    )

    result = CaseExplanation().explain(
        case,
        "USER",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "check your dns settings" in text
    assert "technician is required" not in text
    assert "technician required" not in text


def test_technician_explanation_identifies_unresolved_case_without_inventing_escalation():
    from engine.case_explanation import CaseExplanation

    case = create_case(
        observations=["gateway observation"],
        signals=["dns signal"],
        findings=["network finding"],
        correlations=["network correlation"],
        candidates=["technical candidate"],
        evaluations=["technical evaluation"],
    )

    result = CaseExplanation().explain(
        case,
        "TECHNICIAN",
    )

    text = (
        result.summary.lower()
        + " "
        + result.details.lower()
    )

    assert "none identified" in text
    assert "technician required" not in text
    assert "technician is required" not in text