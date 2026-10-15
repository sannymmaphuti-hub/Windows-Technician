from engine.diagnostic_case import DiagnosticCase
from engine.diagnostic_history import DiagnosticHistory
from engine.historical_trend_intelligence import HistoricalTrendIntelligence


def make_case(machine_id="machine-1", findings=None):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.hostname = "TEST-PC"
    case.observations = []
    case.signals = []
    case.correlations = []
    case.findings = findings or []
    return case


def build_history(findings_list):
    history = DiagnosticHistory()

    for findings in findings_list:
        history.record_case(
            make_case(findings=findings)
        )

    return history


def test_requires_diagnostic_history():
    try:
        HistoricalTrendIntelligence(None)
    except ValueError as exc:
        assert "DiagnosticHistory" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_machine_trend_counts_records():
    history = build_history([
        [{"finding": "HIGH_MEMORY", "severity": "HIGH"}],
        [{"finding": "HIGH_MEMORY", "severity": "HIGH"}],
    ])

    intelligence = HistoricalTrendIntelligence(history)

    trend = intelligence.machine_trend("machine-1")

    assert trend["record_count"] == 2


def test_machine_trend_counts_findings():
    history = build_history([
        [
            {"finding": "HIGH_MEMORY", "severity": "HIGH"},
            {"finding": "CPU_PRESSURE", "severity": "WARNING"},
        ],
    ])

    intelligence = HistoricalTrendIntelligence(history)

    trend = intelligence.machine_trend("machine-1")

    assert trend["finding_count"] == 2


def test_machine_trend_counts_severity():
    history = build_history([
        [
            {"finding": "HIGH_MEMORY", "severity": "HIGH"},
            {"finding": "CPU_PRESSURE", "severity": "WARNING"},
        ],
    ])

    intelligence = HistoricalTrendIntelligence(history)

    trend = intelligence.machine_trend("machine-1")

    assert trend["severity_counts"] == {
        "HIGH": 1,
        "WARNING": 1,
    }


def test_recurring_findings_detects_repetition():
    history = build_history([
        [{"finding": "HIGH_MEMORY", "severity": "HIGH"}],
        [{"finding": "HIGH_MEMORY", "severity": "HIGH"}],
        [{"finding": "CPU_PRESSURE", "severity": "WARNING"}],
    ])

    intelligence = HistoricalTrendIntelligence(history)

    recurring = intelligence.recurring_findings("machine-1")

    assert recurring == [
        {
            "finding": "HIGH_MEMORY",
            "occurrences": 2,
        }
    ]


def test_single_record_has_insufficient_history():
    history = build_history([
        [{"finding": "HIGH_MEMORY", "severity": "HIGH"}],
    ])

    intelligence = HistoricalTrendIntelligence(history)

    assert intelligence.trend_state("machine-1") == "INSUFFICIENT_HISTORY"


def test_missing_machine_has_no_history():
    history = build_history([])

    intelligence = HistoricalTrendIntelligence(history)

    assert intelligence.trend_state("missing") == "NO_HISTORY"


def test_more_findings_means_worsening():
    history = build_history([
        [{"finding": "HIGH_MEMORY", "severity": "HIGH"}],
        [
            {"finding": "HIGH_MEMORY", "severity": "HIGH"},
            {"finding": "CPU_PRESSURE", "severity": "WARNING"},
        ],
    ])

    intelligence = HistoricalTrendIntelligence(history)

    assert intelligence.trend_state("machine-1") == "WORSENING"


def test_fewer_findings_means_improving():
    history = build_history([
        [
            {"finding": "HIGH_MEMORY", "severity": "HIGH"},
            {"finding": "CPU_PRESSURE", "severity": "WARNING"},
        ],
        [{"finding": "HIGH_MEMORY", "severity": "HIGH"}],
    ])

    intelligence = HistoricalTrendIntelligence(history)

    assert intelligence.trend_state("machine-1") == "IMPROVING"


def test_same_finding_count_is_stable():
    history = build_history([
        [{"finding": "HIGH_MEMORY", "severity": "HIGH"}],
        [{"finding": "CPU_PRESSURE", "severity": "WARNING"}],
    ])

    intelligence = HistoricalTrendIntelligence(history)

    assert intelligence.trend_state("machine-1") == "STABLE"


def test_projection_contains_complete_trend_surface():
    history = build_history([
        [{"finding": "HIGH_MEMORY", "severity": "HIGH"}],
        [{"finding": "HIGH_MEMORY", "severity": "HIGH"}],
    ])

    intelligence = HistoricalTrendIntelligence(history)

    projection = intelligence.projection("machine-1")

    assert projection["machine_id"] == "machine-1"
    assert projection["trend_state"] == "STABLE"
    assert "trend" in projection
    assert "recurring_findings" in projection


def test_trend_intelligence_does_not_mutate_history():
    history = build_history([
        [{"finding": "HIGH_MEMORY", "severity": "HIGH"}],
        [{"finding": "HIGH_MEMORY", "severity": "HIGH"}],
    ])

    intelligence = HistoricalTrendIntelligence(history)

    trend = intelligence.machine_trend("machine-1")
    trend["findings"].append({"finding": "TAMPERED"})

    assert len(history.records[0].findings) == 1


def test_no_remediation_processing():
    history = build_history([])

    intelligence = HistoricalTrendIntelligence(history)

    forbidden = {
        "authorize",
        "execute",
        "remediate",
        "verify",
        "resolve",
        "generate_recommendations",
    }

    assert forbidden.isdisjoint(set(dir(intelligence)))
