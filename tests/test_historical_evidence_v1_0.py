from engine.diagnostic_case import DiagnosticCase
from engine.historical_evidence import HistoricalEvidence
from engine.technician_workflow import TechnicianWorkflow


def make_case():
    case = DiagnosticCase()
    case.machine_id = "machine-1"
    case.hostname = "TEST-PC"
    case.observations = [{"type": "MEMORY", "value": 90}]
    case.signals = [{"type": "MEMORY_PRESSURE", "severity": "HIGH"}]
    case.correlations = [{"type": "MEMORY_PROCESS"}]
    case.findings = [{"finding": "HIGH_MEMORY", "severity": "HIGH"}]
    return case


def test_creates_historical_evidence_from_canonical_case():
    record = HistoricalEvidence(make_case())

    assert record.machine_id == "machine-1"
    assert record.hostname == "TEST-PC"


def test_captures_canonical_evidence():
    record = HistoricalEvidence(make_case())

    assert record.observations == [
        {"type": "MEMORY", "value": 90}
    ]
    assert record.signals == [
        {"type": "MEMORY_PRESSURE", "severity": "HIGH"}
    ]
    assert record.correlations == [
        {"type": "MEMORY_PROCESS"}
    ]
    assert record.findings == [
        {"finding": "HIGH_MEMORY", "severity": "HIGH"}
    ]


def test_historical_evidence_is_defensive():
    record = HistoricalEvidence(make_case())

    observations = record.observations
    observations.append({"type": "TAMPERED"})

    assert len(record.observations) == 1


def test_projection_contains_historical_identity():
    record = HistoricalEvidence(make_case())

    projection = record.projection()

    assert projection["machine_id"] == "machine-1"
    assert projection["hostname"] == "TEST-PC"
    assert "timestamp" in projection


def test_projection_contains_evidence():
    record = HistoricalEvidence(make_case())

    projection = record.projection()

    assert projection["observations"] == [
        {"type": "MEMORY", "value": 90}
    ]
    assert projection["signals"] == [
        {"type": "MEMORY_PRESSURE", "severity": "HIGH"}
    ]
    assert projection["correlations"] == [
        {"type": "MEMORY_PROCESS"}
    ]
    assert projection["findings"] == [
        {"finding": "HIGH_MEMORY", "severity": "HIGH"}
    ]


def test_requires_diagnostic_case():
    try:
        HistoricalEvidence(None)
    except ValueError as exc:
        assert "DiagnosticCase" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_does_not_own_workflow():
    record = HistoricalEvidence(make_case())

    assert not hasattr(record, "workflow")


def test_does_not_expose_remediation_processing():
    record = HistoricalEvidence(make_case())

    forbidden = {
        "authorize",
        "execute",
        "remediate",
        "verify",
        "resolve",
        "generate_recommendations",
    }

    assert forbidden.isdisjoint(set(dir(record)))
