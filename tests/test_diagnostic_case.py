# ==========================================
# Windows Technician v0.6
# DIAGNOSTIC CASE TESTS
# ==========================================

from engine.diagnostic_case import DiagnosticCase


def test_diagnostic_case_can_be_created():

    case = DiagnosticCase()

    assert case is not None


def test_diagnostic_case_starts_empty():

    case = DiagnosticCase()

    assert case.evidence == {}
    assert case.findings == []
    assert case.correlations == []
    assert case.root_causes == []
    assert case.recommendations == []


def test_diagnostic_case_starts_with_normal_status():

    case = DiagnosticCase()

    assert case.status == "NORMAL"


def test_diagnostic_case_can_store_evidence():

    case = DiagnosticCase()

    evidence = {
        "CPU": {
            "usage_percent": 90
        }
    }

    case.set_evidence(evidence)

    assert case.evidence == evidence


def test_diagnostic_case_can_store_findings():

    case = DiagnosticCase()

    findings = [
        {
            "category": "CPU",
            "severity": "WARNING",
            "message": "High CPU usage."
        }
    ]

    case.set_findings(findings)

    assert case.findings == findings


def test_diagnostic_case_can_store_correlations():

    case = DiagnosticCase()

    correlations = [
        {
            "relationship": "CPU + MEMORY"
        }
    ]

    case.set_correlations(correlations)

    assert case.correlations == correlations


def test_diagnostic_case_can_store_root_causes():

    case = DiagnosticCase()

    root_causes = [
        {
            "cause": "Process consuming excessive resources.",
            "confidence": 0.85
        }
    ]

    case.set_root_causes(root_causes)

    assert case.root_causes == root_causes


def test_diagnostic_case_can_store_recommendations():

    case = DiagnosticCase()

    recommendations = [
        {
            "category": "CPU",
            "recommendation": "Investigate high CPU process."
        }
    ]

    case.set_recommendations(recommendations)

    assert case.recommendations == recommendations


def test_diagnostic_case_can_store_process_intelligence():

    case = DiagnosticCase()

    intelligence = {
        "name": "chrome.exe",
        "behavior": "HIGH_CPU",
        "severity": "WARNING"
    }

    case.set_process_intelligence(intelligence)

    assert case.process_intelligence == intelligence


def test_diagnostic_case_can_store_memory_intelligence():

    case = DiagnosticCase()

    intelligence = {
        "process": "chrome.exe",
        "severity": "WARNING"
    }

    case.set_memory_intelligence(intelligence)

    assert case.memory_intelligence == intelligence


def test_diagnostic_case_can_store_memory_history():

    case = DiagnosticCase()

    history = [
        61.2,
        68.4,
        74.8,
        81.3
    ]

    case.set_memory_history(history)

    assert case.memory_history == history


def test_diagnostic_case_can_store_memory_trend_intelligence():

    case = DiagnosticCase()

    intelligence = {
        "trend": "RISING",
        "severity": "WARNING"
    }

    case.set_memory_trend_intelligence(intelligence)

    assert case.memory_trend_intelligence == intelligence


def test_diagnostic_case_can_store_memory_temporal_intelligence():

    case = DiagnosticCase()

    intelligence = {
        "behavior": "PERSISTENT",
        "severity": "WARNING"
    }

    case.set_memory_temporal_intelligence(intelligence)

    assert case.memory_temporal_intelligence == intelligence


def test_diagnostic_case_can_store_memory_diagnostic_intelligence():

    case = DiagnosticCase()

    intelligence = {
        "diagnosis": "POSSIBLE_MEMORY_PRESSURE",
        "severity": "WARNING"
    }

    case.set_memory_diagnostic_intelligence(intelligence)

    assert case.memory_diagnostic_intelligence == intelligence


def test_diagnostic_case_can_store_root_cause_candidates():

    case = DiagnosticCase()

    candidates = [
        {
            "cause": "High memory consuming process",
            "confidence": 0.85
        }
    ]

    case.set_root_cause_candidates(candidates)

    assert case.root_cause_candidates == candidates


def test_diagnostic_case_can_store_primary_root_cause():

    case = DiagnosticCase()

    primary = {
        "cause": "High memory consuming process",
        "confidence": 0.85
    }

    case.set_primary_root_cause(primary)

    assert case.primary_root_cause == primary

def test_diagnostic_case_can_store_status():

    case = DiagnosticCase()

    case.set_status("WARNING")

    assert case.status == "WARNING"


def test_diagnostic_case_can_store_critical_status():

    case = DiagnosticCase()

    case.set_status("CRITICAL")

    assert case.status == "CRITICAL"


def test_diagnostic_case_status_defaults_to_normal():

    case = DiagnosticCase()

    assert case.status == "NORMAL"

# ==========================================
# v0.6 CASE FOUNDATION
# ==========================================

def test_diagnostic_case_has_unique_case_id():

    case_a = DiagnosticCase()
    case_b = DiagnosticCase()

    assert case_a.case_id is not None
    assert case_b.case_id is not None
    assert case_a.case_id != case_b.case_id


def test_diagnostic_case_has_initial_lifecycle_state():

    case = DiagnosticCase()

    assert case.lifecycle_state == "OPEN"


def test_diagnostic_case_has_initial_completeness_state():

    case = DiagnosticCase()

    assert case.diagnostic_completeness == "INCOMPLETE"


def test_diagnostic_case_lifecycle_and_completeness_are_independent():

    case = DiagnosticCase()

    case.lifecycle_state = "ANALYZING"
    case.diagnostic_completeness = "PARTIAL"

    assert case.lifecycle_state == "ANALYZING"
    assert case.diagnostic_completeness == "PARTIAL"


def test_diagnostic_case_v05_status_remains_independent():

    case = DiagnosticCase()

    assert case.status == "NORMAL"

    case.lifecycle_state = "ANALYZING"
    case.diagnostic_completeness = "PARTIAL"

    assert case.status == "NORMAL"

from engine.observation import Observation
from engine.signal import Signal


def test_diagnostic_case_starts_with_empty_observations_and_signals():
    case = DiagnosticCase()

    assert case.observations == []
    assert case.signals == []


def test_diagnostic_case_can_store_observation_objects():
    case = DiagnosticCase()

    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    case.set_observations([observation])

    assert len(case.observations) == 1
    assert case.observations[0] is not observation
    assert case.observations[0].source == "memory"
    assert case.observations[0].subject == "system_memory"
    assert case.observations[0].attribute == "usage_percent"
    assert case.observations[0].value == 88


def test_diagnostic_case_can_store_signal_objects():
    case = DiagnosticCase()

    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    case.set_signals([signal])

    assert len(case.signals) == 1
    assert case.signals[0] is not signal
    assert case.signals[0].signal_type == "HIGH_MEMORY_USAGE"
    assert case.signals[0].source == "memory"
    assert case.signals[0].subject == "system_memory"
    assert case.signals[0].attribute == "usage_percent"
    assert case.signals[0].value == 88

def test_diagnostic_case_observations_are_independent_of_input_collection():
    case = DiagnosticCase()

    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    observations = [observation]

    case.set_observations(observations)
    observations.clear()

    assert len(case.observations) == 1
    assert case.observations[0].value == 88


def test_diagnostic_case_signals_are_independent_of_input_collection():
    case = DiagnosticCase()

    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    signals = [signal]

    case.set_signals(signals)
    signals.clear()

    assert len(case.signals) == 1
    assert case.signals[0].value == 88

from engine.finding import Finding


def test_diagnostic_case_can_store_finding_objects():
    case = DiagnosticCase()

    finding = Finding(
        finding_type="MEMORY_PRESSURE",
        category="memory",
        severity="HIGH",
        description="System memory usage is high.",
    )

    case.set_findings([finding])

    assert len(case.findings) == 1
    assert case.findings[0] is not finding
    assert case.findings[0].finding_type == "MEMORY_PRESSURE"
    assert case.findings[0].category == "memory"
    assert case.findings[0].severity == "HIGH"
    assert case.findings[0].description == "System memory usage is high."

from engine.root_cause_candidate import RootCauseCandidate


def test_diagnostic_case_can_store_root_cause_candidate_objects():
    case = DiagnosticCase()

    candidate = RootCauseCandidate(
        cause_type="MEMORY_PRESSURE",
        category="memory",
        explanation="High memory usage is contributing to system pressure.",
    )

    case.set_root_cause_candidates([candidate])

    assert len(case.root_cause_candidates) == 1
    assert case.root_cause_candidates[0] is not candidate
    assert case.root_cause_candidates[0].cause_type == "MEMORY_PRESSURE"
    assert case.root_cause_candidates[0].category == "memory"
    assert (
        case.root_cause_candidates[0].explanation
        == "High memory usage is contributing to system pressure."
    )

from engine.root_cause_candidate import RootCauseCandidate


def test_diagnostic_case_can_store_primary_root_cause_object():
    case = DiagnosticCase()

    root_cause = RootCauseCandidate(
        cause_type="MEMORY_PRESSURE",
        category="memory",
        explanation="High memory usage is contributing to system pressure.",
    )

    case.set_primary_root_cause(root_cause)

    assert case.primary_root_cause is not root_cause
    assert case.primary_root_cause.cause_type == "MEMORY_PRESSURE"
    assert case.primary_root_cause.category == "memory"
    assert (
        case.primary_root_cause.explanation
        == "High memory usage is contributing to system pressure."
    )

from engine.recommendation import Recommendation


def test_diagnostic_case_can_store_recommendation_objects():
    case = DiagnosticCase()

    recommendation = Recommendation(
        recommendation_type="MEMORY_REVIEW",
        category="memory",
        priority="HIGH",
        description="Review memory-intensive processes.",
        rationale="High memory usage may be contributing to system pressure.",
    )

    case.set_recommendations([recommendation])

    assert len(case.recommendations) == 1
    assert case.recommendations[0] is not recommendation
    assert (
        case.recommendations[0].recommendation_type
        == "MEMORY_REVIEW"
    )
    assert case.recommendations[0].category == "memory"
    assert case.recommendations[0].priority == "HIGH"
    assert (
        case.recommendations[0].description
        == "Review memory-intensive processes."
    )
    assert (
        case.recommendations[0].rationale
        == "High memory usage may be contributing to system pressure."
    )

from engine.correlation import Correlation


def test_diagnostic_case_can_store_correlation_objects():
    case = DiagnosticCase()

    correlation = Correlation(
        correlation_type="MEMORY_PROCESS_CORRELATION",
        findings=[
            {
                "finding_type": "MEMORY_PRESSURE",
                "severity": "HIGH",
            }
        ],
        strength="HIGH",
        explanation="High memory usage correlates with memory-intensive processes.",
    )

    case.set_correlations([correlation])

    assert len(case.correlations) == 1
    assert case.correlations[0] is not correlation
    assert (
        case.correlations[0].correlation_type
        == "MEMORY_PROCESS_CORRELATION"
    )
    assert case.correlations[0].strength == "HIGH"
    assert (
        case.correlations[0].explanation
        == "High memory usage correlates with memory-intensive processes."
    )
    assert case.correlations[0].findings == [
        {
            "finding_type": "MEMORY_PRESSURE",
            "severity": "HIGH",
        }
    ]

def test_diagnostic_case_evidence_is_independent_of_input():
    case = DiagnosticCase()

    evidence = {
        "memory": {
            "usage_percent": 88,
            "process": "chrome.exe",
        }
    }

    case.set_evidence(evidence)

    evidence["memory"]["usage_percent"] = 42
    evidence["memory"]["process"] = "notepad.exe"

    assert case.evidence["memory"]["usage_percent"] == 88
    assert case.evidence["memory"]["process"] == "chrome.exe"
