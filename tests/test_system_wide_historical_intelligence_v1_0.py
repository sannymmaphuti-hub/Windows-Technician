from engine.diagnostic_case import DiagnosticCase
from engine.diagnostic_history import DiagnosticHistory
from engine.historical_intelligence_integration import (
    HistoricalIntelligenceIntegration,
)
from engine.system_wide_intelligence_integration import (
    SystemWideIntelligenceIntegration,
)


def make_case(
    machine_id="machine-1",
    findings=None,
):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.hostname = "TEST-PC"
    case.observations = []
    case.signals = []
    case.correlations = []
    case.findings = findings or []
    return case


def make_history():
    history = DiagnosticHistory()

    history.record_case(
        make_case(
            findings=[
                {
                    "finding": "HIGH_MEMORY",
                    "severity": "HIGH",
                }
            ]
        )
    )

    history.record_case(
        make_case(
            findings=[
                {
                    "finding": "HIGH_MEMORY",
                    "severity": "HIGH",
                }
            ]
        )
    )

    return history


def test_existing_system_intelligence_still_works_without_history():
    case = make_case()

    integration = SystemWideIntelligenceIntegration(case)

    projection = integration.intelligence_projection()

    assert "investigation" in projection
    assert "relationships" in projection
    assert "root_cause_reasoning" in projection
    assert "recommendations" in projection
    assert "historical" not in projection


def test_accepts_historical_intelligence():
    case = make_case()

    historical = HistoricalIntelligenceIntegration(
        make_history()
    )

    integration = SystemWideIntelligenceIntegration(
        case,
        historical=historical,
    )

    assert integration.historical is historical


def test_rejects_invalid_historical_component():
    case = make_case()

    try:
        SystemWideIntelligenceIntegration(
            case,
            historical=object(),
        )
    except ValueError as exc:
        assert "HistoricalIntelligenceIntegration" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_historical_projection_is_available():
    case = make_case(
        findings=[
            {
                "finding": "CPU_PRESSURE",
                "severity": "WARNING",
            }
        ]
    )

    historical = HistoricalIntelligenceIntegration(
        make_history()
    )

    integration = SystemWideIntelligenceIntegration(
        case,
        historical=historical,
    )

    projection = integration.historical_projection()

    assert projection["machine_id"] == "machine-1"
    assert "trend" in projection
    assert "recurrence" in projection
    assert "baseline" in projection
    assert "deviation" in projection


def test_historical_projection_detects_new_problem():
    case = make_case(
        findings=[
            {
                "finding": "CPU_PRESSURE",
                "severity": "WARNING",
            }
        ]
    )

    historical = HistoricalIntelligenceIntegration(
        make_history()
    )

    integration = SystemWideIntelligenceIntegration(
        case,
        historical=historical,
    )

    projection = integration.intelligence_projection()

    historical_projection = projection["historical"]

    assert historical_projection["deviation"]["is_deviation"] is True
    assert historical_projection["deviation"]["new_problems"] == [
        "CPU_PRESSURE"
    ]


def test_historical_projection_is_part_of_system_intelligence():
    case = make_case()

    historical = HistoricalIntelligenceIntegration(
        make_history()
    )

    integration = SystemWideIntelligenceIntegration(
        case,
        historical=historical,
    )

    projection = integration.projection()

    assert "historical" in projection["intelligence"]


def test_case_projection_contract_is_unchanged():
    case = make_case()

    historical = HistoricalIntelligenceIntegration(
        make_history()
    )

    integration = SystemWideIntelligenceIntegration(
        case,
        historical=historical,
    )

    projection = integration.case_projection()

    assert set(projection.keys()) == {
        "case_id",
        "observations",
        "signals",
        "correlations",
        "findings",
        "root_causes",
        "recommendations",
    }


def test_historical_data_does_not_mutate_case():
    case = make_case(
        findings=[
            {
                "finding": "CPU_PRESSURE",
                "severity": "WARNING",
            }
        ]
    )

    before = list(case.findings)

    historical = HistoricalIntelligenceIntegration(
        make_history()
    )

    integration = SystemWideIntelligenceIntegration(
        case,
        historical=historical,
    )

    integration.projection()

    assert case.findings == before


def test_historical_projection_is_defensive():
    case = make_case()

    historical = HistoricalIntelligenceIntegration(
        make_history()
    )

    integration = SystemWideIntelligenceIntegration(
        case,
        historical=historical,
    )

    projection = integration.intelligence_projection()

    projection["historical"]["trend"]["findings"].append(
        {"finding": "TAMPERED"}
    )

    fresh = integration.intelligence_projection()

    assert len(fresh["historical"]["trend"]["findings"]) == 2


def test_no_remediation_processing_added():
    case = make_case()

    historical = HistoricalIntelligenceIntegration(
        make_history()
    )

    integration = SystemWideIntelligenceIntegration(
        case,
        historical=historical,
    )

    forbidden = {
        "authorize",
        "execute",
        "remediate",
        "verify",
    }

    assert forbidden.isdisjoint(set(dir(integration)))
