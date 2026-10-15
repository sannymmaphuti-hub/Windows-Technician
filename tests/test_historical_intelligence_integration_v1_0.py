from engine.diagnostic_case import DiagnosticCase
from engine.diagnostic_history import DiagnosticHistory
from engine.historical_intelligence_integration import (
    HistoricalIntelligenceIntegration,
)
from engine.historical_problem_recurrence import (
    HistoricalProblemRecurrence,
)
from engine.historical_health_baseline import (
    HistoricalHealthBaseline,
)
from engine.historical_trend_intelligence import (
    HistoricalTrendIntelligence,
)
from engine.historical_deviation_detection import (
    HistoricalDeviationDetection,
)


def make_case(findings, machine_id="machine-1"):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.hostname = "TEST-PC"
    case.observations = []
    case.signals = []
    case.correlations = []
    case.findings = findings
    return case


def build_history():
    history = DiagnosticHistory()

    history.record_case(
        make_case([
            {"finding": "HIGH_MEMORY", "severity": "HIGH"},
        ])
    )

    history.record_case(
        make_case([
            {"finding": "HIGH_MEMORY", "severity": "HIGH"},
        ])
    )

    return history


def test_requires_diagnostic_history():
    try:
        HistoricalIntelligenceIntegration(None)
    except ValueError as exc:
        assert "DiagnosticHistory" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_creates_canonical_components():
    history = build_history()

    integration = HistoricalIntelligenceIntegration(history)

    assert isinstance(
        integration.trends,
        HistoricalTrendIntelligence,
    )
    assert isinstance(
        integration.recurrence,
        HistoricalProblemRecurrence,
    )
    assert isinstance(
        integration.baseline,
        HistoricalHealthBaseline,
    )
    assert isinstance(
        integration.deviation,
        HistoricalDeviationDetection,
    )


def test_accepts_existing_canonical_components():
    history = build_history()

    trends = HistoricalTrendIntelligence(history)
    recurrence = HistoricalProblemRecurrence(history)
    baseline = HistoricalHealthBaseline(history)
    deviation = HistoricalDeviationDetection(
        history,
        baseline=baseline,
    )

    integration = HistoricalIntelligenceIntegration(
        history,
        trends=trends,
        recurrence=recurrence,
        baseline=baseline,
        deviation=deviation,
    )

    assert integration.trends is trends
    assert integration.recurrence is recurrence
    assert integration.baseline is baseline
    assert integration.deviation is deviation


def test_machine_intelligence_contains_trend():
    history = build_history()
    integration = HistoricalIntelligenceIntegration(history)

    result = integration.machine_intelligence("machine-1")

    assert result["trend"]["record_count"] == 2
    assert result["trend_state"] == "STABLE"


def test_machine_intelligence_contains_recurrence():
    history = build_history()
    integration = HistoricalIntelligenceIntegration(history)

    result = integration.machine_intelligence("machine-1")

    assert result["recurrence"]["has_recurrence"] is True
    assert result["recurrence"]["recurrence_count"] == 1


def test_machine_intelligence_contains_baseline():
    history = build_history()
    integration = HistoricalIntelligenceIntegration(history)

    result = integration.machine_intelligence("machine-1")

    assert result["baseline"]["has_baseline"] is True
    assert result["baseline"]["baseline"]["record_count"] == 2


def test_current_deviation_uses_canonical_detector():
    history = build_history()
    integration = HistoricalIntelligenceIntegration(history)

    current = make_case([
        {"finding": "HIGH_MEMORY"},
        {"finding": "CPU_PRESSURE"},
    ])

    result = integration.current_deviation(current)

    assert result["is_deviation"] is True
    assert result["new_problems"] == ["CPU_PRESSURE"]


def test_projection_without_current_case():
    history = build_history()
    integration = HistoricalIntelligenceIntegration(history)

    result = integration.projection("machine-1")

    assert result["machine_id"] == "machine-1"
    assert "trend" in result
    assert "recurrence" in result
    assert "baseline" in result
    assert "deviation" not in result


def test_projection_with_current_case():
    history = build_history()
    integration = HistoricalIntelligenceIntegration(history)

    current = make_case([
        {"finding": "CPU_PRESSURE"},
    ])

    result = integration.projection(
        "machine-1",
        case=current,
    )

    assert result["deviation"]["is_deviation"] is True
    assert result["deviation"]["new_problems"] == [
        "CPU_PRESSURE"
    ]


def test_projection_rejects_mismatched_machine():
    history = build_history()
    integration = HistoricalIntelligenceIntegration(history)

    current = make_case(
        [{"finding": "CPU_PRESSURE"}],
        machine_id="machine-2",
    )

    try:
        integration.projection(
            "machine-1",
            case=current,
        )
    except ValueError as exc:
        assert "does not match" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_projection_is_defensive():
    history = build_history()
    integration = HistoricalIntelligenceIntegration(history)

    result = integration.projection("machine-1")

    result["trend"]["findings"].append(
        {"finding": "TAMPERED"}
    )

    fresh = integration.projection("machine-1")

    assert len(fresh["trend"]["findings"]) == 2


def test_does_not_mutate_current_case():
    history = build_history()
    integration = HistoricalIntelligenceIntegration(history)

    current = make_case([
        {"finding": "CPU_PRESSURE"},
    ])

    before = list(current.findings)

    integration.current_deviation(current)

    assert current.findings == before


def test_no_remediation_processing():
    history = build_history()
    integration = HistoricalIntelligenceIntegration(history)

    forbidden = {
        "authorize",
        "execute",
        "remediate",
        "verify",
        "resolve",
        "generate_recommendations",
    }

    assert forbidden.isdisjoint(set(dir(integration)))
