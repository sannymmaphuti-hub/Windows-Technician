# ==========================================
# Windows Technician v0.9
# WINDOWS SERVICES COLLECTOR TESTS
# ==========================================

from engine.windows_services_collector import (
    WindowsServicesCollector,
)
from engine.windows_services_evidence import (
    WindowsServicesEvidence,
)


def test_collector_domain():
    collector = WindowsServicesCollector()

    assert collector.domain == "SERVICES"


def test_collect_returns_services_evidence():
    collector = WindowsServicesCollector()

    evidence = collector.collect()

    assert isinstance(
        evidence,
        WindowsServicesEvidence,
    )


def test_collect_returns_service_records():
    collector = WindowsServicesCollector()

    evidence = collector.collect()

    assert isinstance(
        evidence.services,
        list,
    )


def test_service_records_have_expected_fields():
    collector = WindowsServicesCollector()

    evidence = collector.collect()

    for service in evidence.services:
        assert isinstance(service, dict)

        assert "name" in service
        assert "display_name" in service
        assert "status" in service
        assert "start_type" in service


def test_service_names_are_strings():
    collector = WindowsServicesCollector()

    evidence = collector.collect()

    for service in evidence.services:
        assert isinstance(
            service["name"],
            str,
        )


def test_service_status_is_normalized():
    collector = WindowsServicesCollector()

    evidence = collector.collect()

    valid_states = {
        "RUNNING",
        "STOPPED",
        "UNKNOWN",
    }

    for service in evidence.services:
        assert service["status"] in valid_states


def test_service_start_type_is_normalized():
    collector = WindowsServicesCollector()

    evidence = collector.collect()

    valid_start_types = {
        "AUTO",
        "MANUAL",
        "DISABLED",
        "UNKNOWN",
    }

    for service in evidence.services:
        assert (
            service["start_type"]
            in valid_start_types
        )


def test_collection_does_not_modify_services():
    collector = WindowsServicesCollector()

    first = collector.collect()
    second = collector.collect()

    assert first is not second
    assert first.services is not second.services


def test_collector_does_not_create_case():
    collector = WindowsServicesCollector()

    evidence = collector.collect()

    assert not hasattr(
        evidence,
        "case_id",
    )


def test_collector_does_not_authorize():
    collector = WindowsServicesCollector()

    evidence = collector.collect()

    assert not hasattr(
        evidence,
        "authorization",
    )
    assert not hasattr(
        evidence,
        "authorized",
    )


def test_collector_does_not_execute_remediation():
    collector = WindowsServicesCollector()

    evidence = collector.collect()

    assert not hasattr(
        evidence,
        "execution_status",
    )
    assert not hasattr(
        evidence,
        "remediation_result",
    )