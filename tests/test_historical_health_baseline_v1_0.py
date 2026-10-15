from engine.diagnostic_case import DiagnosticCase
from engine.diagnostic_history import DiagnosticHistory
from engine.historical_health_baseline import HistoricalHealthBaseline


def make_case(findings, machine_id="machine-1"):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.hostname = "TEST-PC"
    case.observations = []
    case.signals = []
    case.correlations = []
    case.findings = findings
    return case


def build_history(findings_list):
    history = DiagnosticHistory()

    for findings in findings_list:
        history.record_case(make_case(findings))

    return history


def test_requires_diagnostic_history():
    try:
        HistoricalHealthBaseline(None)
    except ValueError as exc:
        assert "DiagnosticHistory" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_machine_baseline_counts_records():
    history = build_history([
        [{"finding": "HIGH_MEMORY"}],
        [{"finding": "CPU_PRESSURE"}],
    ])

    baseline = HistoricalHealthBaseline(history)

    result = baseline.machine_baseline("machine-1")

    assert result["record_count"] == 2


def test_machine_baseline_counts_findings():
    history = build_history([
        [{"finding": "HIGH_MEMORY"}],
        [{"finding": "HIGH_MEMORY"}],
        [{"finding": "CPU_PRESSURE"}],
    ])

    baseline = HistoricalHealthBaseline(history)

    result = baseline.machine_baseline("machine-1")

    assert result["finding_counts"] == {
        "HIGH_MEMORY": 2,
        "CPU_PRESSURE": 1,
    }


def test_machine_baseline_counts_severities():
    history = build_history([
        [
            {"finding": "HIGH_MEMORY", "severity": "HIGH"},
            {"finding": "CPU_PRESSURE", "severity": "WARNING"},
        ],
        [
            {"finding": "HIGH_MEMORY", "severity": "HIGH"},
        ],
    ])

    baseline = HistoricalHealthBaseline(history)

    result = baseline.machine_baseline("machine-1")

    assert result["severity_counts"] == {
        "HIGH": 2,
        "WARNING": 1,
    }


def test_known_problems_returns_historical_problems():
    history = build_history([
        [{"finding": "HIGH_MEMORY"}],
        [{"finding": "CPU_PRESSURE"}],
    ])

    baseline = HistoricalHealthBaseline(history)

    assert baseline.known_problems("machine-1") == [
        "HIGH_MEMORY",
        "CPU_PRESSURE",
    ]


def test_common_problems_use_occurrence_threshold():
    history = build_history([
        [{"finding": "HIGH_MEMORY"}],
        [{"finding": "HIGH_MEMORY"}],
        [{"finding": "CPU_PRESSURE"}],
    ])

    baseline = HistoricalHealthBaseline(history)

    assert baseline.common_problems("machine-1") == {
        "HIGH_MEMORY": 2,
    }


def test_custom_occurrence_threshold():
    history = build_history([
        [{"finding": "HIGH_MEMORY"}],
        [{"finding": "HIGH_MEMORY"}],
        [{"finding": "HIGH_MEMORY"}],
    ])

    baseline = HistoricalHealthBaseline(history)

    assert baseline.common_problems(
        "machine-1",
        minimum_occurrences=3,
    ) == {
        "HIGH_MEMORY": 3,
    }


def test_machine_with_history_has_baseline():
    history = build_history([
        [{"finding": "HIGH_MEMORY"}],
    ])

    baseline = HistoricalHealthBaseline(history)

    assert baseline.has_baseline("machine-1") is True


def test_machine_without_history_has_no_baseline():
    history = build_history([])

    baseline = HistoricalHealthBaseline(history)

    assert baseline.has_baseline("machine-1") is False


def test_projection_contains_baseline():
    history = build_history([
        [{"finding": "HIGH_MEMORY"}],
        [{"finding": "HIGH_MEMORY"}],
    ])

    baseline = HistoricalHealthBaseline(history)

    projection = baseline.projection("machine-1")

    assert projection["machine_id"] == "machine-1"
    assert projection["has_baseline"] is True
    assert projection["baseline"]["record_count"] == 2
    assert projection["known_problems"] == ["HIGH_MEMORY"]


def test_projection_is_defensive():
    history = build_history([
        [{"finding": "HIGH_MEMORY"}],
    ])

    baseline = HistoricalHealthBaseline(history)

    projection = baseline.projection("machine-1")
    projection["baseline"]["finding_counts"]["TAMPERED"] = 99

    fresh = baseline.machine_baseline("machine-1")

    assert "TAMPERED" not in fresh["finding_counts"]


def test_invalid_threshold_is_rejected():
    history = build_history([])
    baseline = HistoricalHealthBaseline(history)

    try:
        baseline.common_problems(
            "machine-1",
            minimum_occurrences=0,
        )
    except ValueError as exc:
        assert "at least 1" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_no_remediation_processing():
    history = build_history([])
    baseline = HistoricalHealthBaseline(history)

    forbidden = {
        "authorize",
        "execute",
        "remediate",
        "verify",
        "resolve",
        "generate_recommendations",
    }

    assert forbidden.isdisjoint(set(dir(baseline)))
