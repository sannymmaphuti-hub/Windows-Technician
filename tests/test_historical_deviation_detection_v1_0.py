from engine.diagnostic_case import DiagnosticCase
from engine.diagnostic_history import DiagnosticHistory
from engine.historical_deviation_detection import HistoricalDeviationDetection


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


def test_requires_history():
    try:
        HistoricalDeviationDetection(None)
    except ValueError as exc:
        assert "DiagnosticHistory" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_requires_valid_baseline():
    history = build_history()

    try:
        HistoricalDeviationDetection(history, baseline=None)
    except Exception:
        raise AssertionError(
            "A missing baseline should be created automatically."
        )


def test_known_problem_is_not_a_deviation():
    history = build_history()
    detector = HistoricalDeviationDetection(history)

    current = make_case([
        {"finding": "HIGH_MEMORY", "severity": "HIGH"},
    ])

    result = detector.detect(current)

    assert result["is_deviation"] is False
    assert result["new_problems"] == []


def test_new_problem_is_deviation():
    history = build_history()
    detector = HistoricalDeviationDetection(history)

    current = make_case([
        {"finding": "HIGH_MEMORY", "severity": "HIGH"},
        {"finding": "CPU_PRESSURE", "severity": "WARNING"},
    ])

    result = detector.detect(current)

    assert result["is_deviation"] is True
    assert result["new_problems"] == ["CPU_PRESSURE"]


def test_multiple_new_problems_are_detected():
    history = build_history()
    detector = HistoricalDeviationDetection(history)

    current = make_case([
        {"finding": "NETWORK_FAILURE"},
        {"finding": "DISK_PRESSURE"},
    ])

    result = detector.detect(current)

    assert result["new_problems"] == [
        "DISK_PRESSURE",
        "NETWORK_FAILURE",
    ]
    assert result["new_problem_count"] == 2


def test_machine_without_history_is_deviation_when_findings_exist():
    history = build_history()
    detector = HistoricalDeviationDetection(history)

    current = make_case(
        [{"finding": "CPU_PRESSURE"}],
        machine_id="machine-2",
    )

    result = detector.detect(current)

    assert result["has_baseline"] is False
    assert result["is_deviation"] is True
    assert result["new_problems"] == ["CPU_PRESSURE"]


def test_machine_without_findings_is_not_deviation():
    history = build_history()
    detector = HistoricalDeviationDetection(history)

    current = make_case([])

    result = detector.detect(current)

    assert result["is_deviation"] is False
    assert result["new_problems"] == []


def test_is_deviation_helper():
    history = build_history()
    detector = HistoricalDeviationDetection(history)

    current = make_case([
        {"finding": "CPU_PRESSURE"},
    ])

    assert detector.is_deviation(current) is True


def test_new_problems_helper_is_defensive():
    history = build_history()
    detector = HistoricalDeviationDetection(history)

    current = make_case([
        {"finding": "CPU_PRESSURE"},
    ])

    problems = detector.new_problems(current)
    problems.append("TAMPERED")

    assert detector.new_problems(current) == [
        "CPU_PRESSURE"
    ]


def test_detection_does_not_mutate_case():
    history = build_history()
    detector = HistoricalDeviationDetection(history)

    current = make_case([
        {"finding": "CPU_PRESSURE"},
    ])

    before = list(current.findings)

    detector.detect(current)

    assert current.findings == before


def test_requires_diagnostic_case():
    history = build_history()
    detector = HistoricalDeviationDetection(history)

    try:
        detector.detect(None)
    except ValueError as exc:
        assert "DiagnosticCase" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_no_remediation_processing():
    history = build_history()
    detector = HistoricalDeviationDetection(history)

    forbidden = {
        "authorize",
        "execute",
        "remediate",
        "verify",
        "resolve",
        "generate_recommendations",
    }

    assert forbidden.isdisjoint(set(dir(detector)))
