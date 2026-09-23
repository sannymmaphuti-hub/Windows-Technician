# ==========================================
# Windows Technician v0.6
# CASE DECISION TESTS
# ==========================================

from engine.case_decision import CaseDecision
from engine.diagnostic_case import DiagnosticCase
from copy import deepcopy


def test_case_decision_can_be_created_from_diagnostic_case():

    case = DiagnosticCase()

    decision = CaseDecision(case)

    assert decision.case is case


def test_case_decision_starts_with_empty_result():

    case = DiagnosticCase()

    decision = CaseDecision(case)

    assert hasattr(decision, "result")
    assert decision.result == {}


def test_case_decision_identifies_primary_root_cause():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.9
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["primary_root_cause"] == {
        "cause": "Memory pressure",
        "severity": "HIGH",
        "confidence": 0.9
    }


def test_case_decision_preserves_primary_root_cause_severity():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.9
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["severity"] == "HIGH"


def test_case_decision_preserves_primary_root_cause_confidence():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.9
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["confidence"] == 0.9


def test_case_decision_identifies_critical_action_for_high_severity():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.9
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["action"] == "IMMEDIATE_ATTENTION"


def test_case_decision_recommends_review_for_medium_severity():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Elevated memory usage",
            "severity": "MEDIUM",
            "confidence": 0.8
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["action"] == "REVIEW_RECOMMENDED"


def test_case_decision_recommends_monitoring_for_low_severity():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Minor memory fluctuation",
            "severity": "LOW",
            "confidence": 0.7
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["action"] == "MONITOR"


def test_case_decision_returns_empty_result_without_primary_root_cause():

    case = DiagnosticCase()

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result == {}

def test_case_decision_returns_no_action_for_unknown_severity():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Unknown condition",
            "severity": "UNKNOWN",
            "confidence": 0.5
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["action"] is None


def test_case_decision_returns_no_action_when_severity_is_missing():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Unclassified condition",
            "confidence": 0.5
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["action"] is None

def test_case_decision_downgrades_high_severity_with_low_confidence():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.6
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["action"] == "REVIEW_RECOMMENDED"


def test_case_decision_keeps_high_severity_with_high_confidence():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.9
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["action"] == "IMMEDIATE_ATTENTION"

def test_case_decision_provides_recommendation_for_memory_pressure():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.9
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["recommendation"] == \
        "Investigate memory-consuming processes"


def test_case_decision_provides_generic_recommendation_for_unknown_cause():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Unknown condition",
            "severity": "MEDIUM",
            "confidence": 0.7
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["recommendation"] == \
        "Investigate the primary root cause"

def test_case_decision_preserves_existing_case_recommendation():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.9
        }
    )

    case.set_recommendations(
        [
            "Close unnecessary applications"
        ]
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["recommendation"] == \
        "Close unnecessary applications"


def test_case_decision_preserves_multiple_case_recommendations():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.9
        }
    )

    case.set_recommendations(
        [
            "Close unnecessary applications",
            "Investigate memory-consuming processes"
        ]
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["recommendation"] == [
        "Close unnecessary applications",
        "Investigate memory-consuming processes"
    ]

def test_case_decision_produces_complete_diagnostic_decision():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.9
        }
    )

    case.set_recommendations(
        [
            "Close unnecessary applications",
            "Investigate high memory usage"
        ]
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["primary_root_cause"] == {
        "cause": "Memory pressure",
        "severity": "HIGH",
        "confidence": 0.9
    }

    assert result["severity"] == "HIGH"

    assert result["confidence"] == 0.9

    assert result["action"] == "IMMEDIATE_ATTENTION"

    assert result["recommendation"] == [
        "Close unnecessary applications",
        "Investigate high memory usage"
    ]

def test_case_decision_can_be_evaluated_multiple_times():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.9
        }
    )

    decision = CaseDecision(case)

    first_result = decision.evaluate()
    second_result = decision.evaluate()
    assert first_result == second_result
def test_case_decision_does_not_modify_diagnostic_case():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.9
        }
    )

    case.set_recommendations(
        [
            "Close unnecessary applications"
        ]
    )

    original_root_cause = deepcopy(
        case.primary_root_cause
    )

    original_recommendations = deepcopy(
        case.recommendations
    )

    decision = CaseDecision(case)

    decision.evaluate()

    assert case.primary_root_cause == original_root_cause
    assert case.recommendations == original_recommendations

def test_case_decision_keeps_high_severity_at_confidence_boundary():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.8
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["action"] == "IMMEDIATE_ATTENTION"

def test_case_decision_downgrades_high_severity_just_below_confidence_boundary():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.79
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["action"] == "REVIEW_RECOMMENDED"

def test_case_decision_assigns_critical_priority_to_critical_action():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.9
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["priority"] == "CRITICAL"


def test_case_decision_assigns_review_priority_to_medium_severity():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "MEDIUM",
            "confidence": 0.9
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["priority"] == "REVIEW"

def test_case_decision_provides_explanation_for_critical_decision():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.9
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["explanation"] == (
        "Memory pressure was identified with HIGH severity "
        "and 90% confidence. Immediate attention is required."
    )


def test_case_decision_provides_explanation_for_review_decision():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "CPU overload",
            "severity": "MEDIUM",
            "confidence": 0.7
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["explanation"] == (
        "CPU overload was identified with MEDIUM severity "
        "and 70% confidence. Review is recommended."
    )


def test_case_decision_provides_explanation_for_monitoring_decision():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Disk usage",
            "severity": "LOW",
            "confidence": 0.6
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["explanation"] == (
        "Disk usage was identified with LOW severity "
        "and 60% confidence. Monitoring is recommended."
    )
def test_case_decision_provides_explanation_for_critical_decision():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "HIGH",
            "confidence": 0.9
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["explanation"] == (
        "Memory pressure was identified with HIGH severity "
        "and 90% confidence. Immediate attention is required."
    )


def test_case_decision_provides_explanation_for_review_decision():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "CPU overload",
            "severity": "MEDIUM",
            "confidence": 0.7
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["explanation"] == (
        "CPU overload was identified with MEDIUM severity "
        "and 70% confidence. Review is recommended."
    )


def test_case_decision_provides_explanation_for_monitoring_decision():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Disk usage",
            "severity": "LOW",
            "confidence": 0.6
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["explanation"] == (
        "Disk usage was identified with LOW severity "
        "and 60% confidence. Monitoring is recommended."
    )

def test_case_decision_handles_missing_confidence():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "Memory pressure",
            "severity": "HIGH"
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["confidence"] is None
    assert result["action"] == "REVIEW_RECOMMENDED"
    assert result["explanation"] == (
        "Memory pressure was identified with HIGH severity "
        "and unknown confidence. Review is recommended."
    )


def test_case_decision_handles_zero_confidence():

    case = DiagnosticCase()

    case.set_primary_root_cause(
        {
            "cause": "CPU overload",
            "severity": "HIGH",
            "confidence": 0.0
        }
    )

    decision = CaseDecision(case)

    result = decision.evaluate()

    assert result["confidence"] == 0.0
    assert result["action"] == "REVIEW_RECOMMENDED"
    assert result["explanation"] == (
        "CPU overload was identified with HIGH severity "
        "and 0% confidence. Review is recommended."
    )
