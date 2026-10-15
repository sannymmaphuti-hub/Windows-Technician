from engine.diagnostic_case import DiagnosticCase
from engine.diagnostic_history import DiagnosticHistory
from engine.historical_evidence import HistoricalEvidence


def make_case(machine_id="machine-1", hostname="TEST-PC"):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.hostname = hostname
    case.observations = [{"type": "MEMORY", "value": 90}]
    case.signals = [{"type": "MEMORY_PRESSURE", "severity": "HIGH"}]
    case.correlations = [{"type": "MEMORY_PROCESS"}]
    case.findings = [{"finding": "HIGH_MEMORY", "severity": "HIGH"}]
    return case


def test_history_starts_empty():
    history = DiagnosticHistory()

    assert history.count == 0
    assert history.records == []


def test_record_case_creates_historical_evidence():
    history = DiagnosticHistory()
    case = make_case()

    record = history.record_case(case)

    assert isinstance(record, HistoricalEvidence)
    assert history.count == 1


def test_record_case_captures_snapshot():
    history = DiagnosticHistory()
    case = make_case()

    history.record_case(case)

    case.observations.append({"type": "CPU", "value": 99})

    record = history.latest_for_machine("machine-1")

    assert record.observations == [
        {"type": "MEMORY", "value": 90}
    ]


def test_can_add_existing_historical_evidence():
    history = DiagnosticHistory()
    record = HistoricalEvidence(make_case())

    history.add(record)

    assert history.count == 1
    assert history.records[0] is record


def test_rejects_invalid_case():
    history = DiagnosticHistory()

    try:
        history.record_case(None)
    except ValueError as exc:
        assert "DiagnosticCase" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_rejects_invalid_historical_record():
    history = DiagnosticHistory()

    try:
        history.add(None)
    except ValueError as exc:
        assert "HistoricalEvidence" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_filters_history_by_machine():
    history = DiagnosticHistory()

    history.record_case(make_case("machine-1", "PC-1"))
    history.record_case(make_case("machine-2", "PC-2"))
    history.record_case(make_case("machine-1", "PC-1"))

    records = history.for_machine("machine-1")

    assert len(records) == 2
    assert all(
        record.machine_id == "machine-1"
        for record in records
    )


def test_latest_history_record_is_returned():
    history = DiagnosticHistory()

    first = history.record_case(make_case())
    second = history.record_case(make_case())

    assert history.latest_for_machine("machine-1") is second
    assert history.latest_for_machine("machine-1") is not first


def test_missing_machine_returns_none():
    history = DiagnosticHistory()

    assert history.latest_for_machine("missing") is None


def test_projection_contains_all_history():
    history = DiagnosticHistory()

    history.record_case(make_case("machine-1"))
    history.record_case(make_case("machine-2"))

    projection = history.projection()

    assert projection["count"] == 2
    assert len(projection["records"]) == 2


def test_projection_is_defensive():
    history = DiagnosticHistory()
    history.record_case(make_case())

    projection = history.projection()
    projection["records"][0]["observations"].append(
        {"type": "TAMPERED"}
    )

    assert len(history.records[0].observations) == 1


def test_history_does_not_own_remediation_processing():
    history = DiagnosticHistory()

    forbidden = {
        "authorize",
        "execute",
        "remediate",
        "verify",
        "resolve",
        "generate_recommendations",
    }

    assert forbidden.isdisjoint(set(dir(history)))
