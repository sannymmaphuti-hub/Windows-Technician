from engine.diagnostic_case import DiagnosticCase
from engine.diagnostic_history import DiagnosticHistory
from engine.historical_problem_recurrence import HistoricalProblemRecurrence


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
        HistoricalProblemRecurrence(None)
    except ValueError as exc:
        assert "DiagnosticHistory" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_machine_problems_counts_problem_across_records():
    history = build_history([
        [{"finding": "HIGH_MEMORY", "severity": "HIGH"}],
        [{"finding": "HIGH_MEMORY", "severity": "HIGH"}],
        [{"finding": "CPU_PRESSURE", "severity": "WARNING"}],
    ])

    recurrence = HistoricalProblemRecurrence(history)

    assert recurrence.machine_problems("machine-1") == [
        {
            "problem": "HIGH_MEMORY",
            "occurrences": 2,
        },
        {
            "problem": "CPU_PRESSURE",
            "occurrences": 1,
        },
    ]


def test_same_problem_twice_in_one_record_counts_once():
    history = build_history([
        [
            {"finding": "HIGH_MEMORY", "severity": "HIGH"},
            {"finding": "HIGH_MEMORY", "severity": "WARNING"},
        ],
    ])

    recurrence = HistoricalProblemRecurrence(history)

    assert recurrence.machine_problems("machine-1") == [
        {
            "problem": "HIGH_MEMORY",
            "occurrences": 1,
        }
    ]


def test_recurring_problems_use_default_threshold():
    history = build_history([
        [{"finding": "HIGH_MEMORY"}],
        [{"finding": "HIGH_MEMORY"}],
        [{"finding": "CPU_PRESSURE"}],
    ])

    recurrence = HistoricalProblemRecurrence(history)

    assert recurrence.recurring_problems("machine-1") == [
        {
            "problem": "HIGH_MEMORY",
            "occurrences": 2,
        }
    ]


def test_custom_recurrence_threshold():
    history = build_history([
        [{"finding": "HIGH_MEMORY"}],
        [{"finding": "HIGH_MEMORY"}],
        [{"finding": "HIGH_MEMORY"}],
    ])

    recurrence = HistoricalProblemRecurrence(history)

    assert recurrence.recurring_problems(
        "machine-1",
        minimum_occurrences=3,
    ) == [
        {
            "problem": "HIGH_MEMORY",
            "occurrences": 3,
        }
    ]


def test_recurrence_can_be_detected():
    history = build_history([
        [{"finding": "HIGH_MEMORY"}],
        [{"finding": "HIGH_MEMORY"}],
    ])

    recurrence = HistoricalProblemRecurrence(history)

    assert recurrence.has_recurrence("machine-1") is True


def test_no_recurrence_is_detected():
    history = build_history([
        [{"finding": "HIGH_MEMORY"}],
        [{"finding": "CPU_PRESSURE"}],
    ])

    recurrence = HistoricalProblemRecurrence(history)

    assert recurrence.has_recurrence("machine-1") is False


def test_recurrence_count_returns_number_of_recurring_problems():
    history = build_history([
        [
            {"finding": "HIGH_MEMORY"},
            {"finding": "CPU_PRESSURE"},
        ],
        [
            {"finding": "HIGH_MEMORY"},
            {"finding": "CPU_PRESSURE"},
        ],
    ])

    recurrence = HistoricalProblemRecurrence(history)

    assert recurrence.recurrence_count("machine-1") == 2


def test_missing_machine_has_no_recurrence():
    history = build_history([
        [{"finding": "HIGH_MEMORY"}],
    ])

    recurrence = HistoricalProblemRecurrence(history)

    assert recurrence.machine_problems("missing") == []
    assert recurrence.has_recurrence("missing") is False


def test_projection_contains_recurrence_surface():
    history = build_history([
        [{"finding": "HIGH_MEMORY"}],
        [{"finding": "HIGH_MEMORY"}],
    ])

    recurrence = HistoricalProblemRecurrence(history)

    projection = recurrence.projection("machine-1")

    assert projection["machine_id"] == "machine-1"
    assert projection["problem_count"] == 1
    assert projection["recurrence_count"] == 1
    assert projection["has_recurrence"] is True
    assert projection["recurring_problems"] == [
        {
            "problem": "HIGH_MEMORY",
            "occurrences": 2,
        }
    ]


def test_projection_is_defensive():
    history = build_history([
        [{"finding": "HIGH_MEMORY"}],
        [{"finding": "HIGH_MEMORY"}],
    ])

    recurrence = HistoricalProblemRecurrence(history)

    projection = recurrence.projection("machine-1")
    projection["recurring_problems"].append(
        {"problem": "TAMPERED", "occurrences": 99}
    )

    assert recurrence.recurrence_count("machine-1") == 1


def test_invalid_threshold_is_rejected():
    history = build_history([])
    recurrence = HistoricalProblemRecurrence(history)

    try:
        recurrence.recurring_problems(
            "machine-1",
            minimum_occurrences=0,
        )
    except ValueError as exc:
        assert "at least 1" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_no_remediation_processing():
    history = build_history([])
    recurrence = HistoricalProblemRecurrence(history)

    forbidden = {
        "authorize",
        "execute",
        "remediate",
        "verify",
        "resolve",
        "generate_recommendations",
    }

    assert forbidden.isdisjoint(set(dir(recurrence)))
