# ==========================================
# Windows Technician v0.9
# WINDOWS SERVICES INTELLIGENCE TESTS
# ==========================================

from engine.finding import Finding
from engine.recommendation import Recommendation
from engine.signal import Signal
from engine.windows_services_evidence import (
    WindowsServicesEvidence,
)
from engine.windows_services_intelligence import (
    WindowsServicesIntelligence,
)


def make_evidence(services):
    return WindowsServicesEvidence(
        services=services
    )


def test_domain():
    intelligence = WindowsServicesIntelligence()

    assert intelligence.domain == "SERVICES"


def test_empty_evidence_produces_no_findings():
    intelligence = WindowsServicesIntelligence()

    result = intelligence.analyze(
        make_evidence([])
    )

    assert result["signals"] == []
    assert result["findings"] == []
    assert result["recommendations"] == []


def test_healthy_required_service_produces_no_problem():
    intelligence = WindowsServicesIntelligence()

    result = intelligence.analyze(
        make_evidence(
            [
                {
                    "name": "Spooler",
                    "status": "RUNNING",
                    "start_type": "AUTO",
                    "required": True,
                }
            ]
        )
    )

    assert result["signals"] == []
    assert result["findings"] == []
    assert result["recommendations"] == []


def test_stopped_required_service_creates_signal():
    intelligence = WindowsServicesIntelligence()

    result = intelligence.analyze(
        make_evidence(
            [
                {
                    "name": "Spooler",
                    "status": "STOPPED",
                    "start_type": "AUTO",
                    "required": True,
                }
            ]
        )
    )

    assert len(result["signals"]) == 1

    signal = result["signals"][0]

    assert isinstance(signal, Signal)
    assert signal.signal_type == "SERVICE_STOPPED"
    assert signal.source == "SERVICES"
    assert signal.subject == "Spooler"
    assert signal.attribute == "status"
    assert signal.value == "STOPPED"


def test_stopped_required_service_creates_finding():
    intelligence = WindowsServicesIntelligence()

    result = intelligence.analyze(
        make_evidence(
            [
                {
                    "name": "Spooler",
                    "status": "STOPPED",
                    "start_type": "AUTO",
                    "required": True,
                }
            ]
        )
    )

    assert len(result["findings"]) == 1

    finding = result["findings"][0]

    assert isinstance(finding, Finding)
    assert finding.finding_type == "SERVICE_UNAVAILABLE"
    assert finding.category == "SERVICES"
    assert finding.severity == "HIGH"


def test_finding_references_exact_signal():
    intelligence = WindowsServicesIntelligence()

    result = intelligence.analyze(
        make_evidence(
            [
                {
                    "name": "Spooler",
                    "status": "STOPPED",
                    "start_type": "AUTO",
                    "required": True,
                }
            ]
        )
    )

    assert (
        result["findings"][0].supporting_signals[0]
        is result["signals"][0]
    )


def test_stopped_required_service_creates_recommendation():
    intelligence = WindowsServicesIntelligence()

    result = intelligence.analyze(
        make_evidence(
            [
                {
                    "name": "Spooler",
                    "status": "STOPPED",
                    "start_type": "AUTO",
                    "required": True,
                }
            ]
        )
    )

    assert len(result["recommendations"]) == 1

    recommendation = result["recommendations"][0]

    assert isinstance(
        recommendation,
        Recommendation,
    )

    assert (
        recommendation.recommendation_type
        == "REVIEW_SERVICE_STATE"
    )
    assert recommendation.category == "SERVICES"
    assert recommendation.priority == "HIGH"


def test_disabled_required_service_creates_signal():
    intelligence = WindowsServicesIntelligence()

    result = intelligence.analyze(
        make_evidence(
            [
                {
                    "name": "Spooler",
                    "status": "STOPPED",
                    "start_type": "DISABLED",
                    "required": True,
                }
            ]
        )
    )

    assert len(result["signals"]) == 1

    signal = result["signals"][0]

    assert signal.signal_type == "SERVICE_DISABLED"
    assert signal.subject == "Spooler"
    assert signal.attribute == "start_type"
    assert signal.value == "DISABLED"


def test_disabled_required_service_creates_finding():
    intelligence = WindowsServicesIntelligence()

    result = intelligence.analyze(
        make_evidence(
            [
                {
                    "name": "Spooler",
                    "status": "STOPPED",
                    "start_type": "DISABLED",
                    "required": True,
                }
            ]
        )
    )

    finding = result["findings"][0]

    assert finding.finding_type == "SERVICE_DISABLED"
    assert finding.severity == "HIGH"


def test_non_required_stopped_service_is_not_problem():
    intelligence = WindowsServicesIntelligence()

    result = intelligence.analyze(
        make_evidence(
            [
                {
                    "name": "ExampleService",
                    "status": "STOPPED",
                    "start_type": "MANUAL",
                    "required": False,
                }
            ]
        )
    )

    assert result["signals"] == []
    assert result["findings"] == []
    assert result["recommendations"] == []


def test_multiple_services_are_evaluated_independently():
    intelligence = WindowsServicesIntelligence()

    result = intelligence.analyze(
        make_evidence(
            [
                {
                    "name": "HealthyService",
                    "status": "RUNNING",
                    "start_type": "AUTO",
                    "required": True,
                },
                {
                    "name": "BrokenService",
                    "status": "STOPPED",
                    "start_type": "AUTO",
                    "required": True,
                },
            ]
        )
    )

    assert len(result["signals"]) == 1
    assert len(result["findings"]) == 1
    assert len(result["recommendations"]) == 1

    assert (
        result["signals"][0].subject
        == "BrokenService"
    )


def test_none_evidence_is_rejected():
    intelligence = WindowsServicesIntelligence()

    try:
        intelligence.analyze(None)
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for None evidence."
    )


def test_invalid_evidence_is_rejected():
    intelligence = WindowsServicesIntelligence()

    try:
        intelligence.analyze({})
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for invalid evidence."
    )


def test_invalid_service_records_are_ignored():
    intelligence = WindowsServicesIntelligence()

    result = intelligence.analyze(
        make_evidence(
            [
                {},
                {
                    "name": "ValidService",
                    "status": "RUNNING",
                    "start_type": "AUTO",
                    "required": True,
                },
            ]
        )
    )

    assert result["signals"] == []
    assert result["findings"] == []
    assert result["recommendations"] == []


def test_results_are_fresh():
    intelligence = WindowsServicesIntelligence()

    evidence = make_evidence(
        [
            {
                "name": "Spooler",
                "status": "STOPPED",
                "start_type": "AUTO",
                "required": True,
            }
        ]
    )

    first = intelligence.analyze(evidence)
    second = intelligence.analyze(evidence)

    assert first is not second
    assert first["signals"] is not second["signals"]
    assert first["findings"] is not second["findings"]
    assert (
        first["recommendations"]
        is not second["recommendations"]
    )


def test_no_authorization_is_created():
    intelligence = WindowsServicesIntelligence()

    result = intelligence.analyze(
        make_evidence(
            [
                {
                    "name": "Spooler",
                    "status": "STOPPED",
                    "start_type": "AUTO",
                    "required": True,
                }
            ]
        )
    )

    assert "authorization" not in result
    assert "authorized" not in result


def test_no_remediation_is_created():
    intelligence = WindowsServicesIntelligence()

    result = intelligence.analyze(
        make_evidence(
            [
                {
                    "name": "Spooler",
                    "status": "STOPPED",
                    "start_type": "AUTO",
                    "required": True,
                }
            ]
        )
    )

    assert "execution_status" not in result
    assert "remediation_result" not in result