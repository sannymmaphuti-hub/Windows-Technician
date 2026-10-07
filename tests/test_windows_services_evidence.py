# ==========================================
# Windows Technician v0.9
# WINDOWS SERVICES EVIDENCE TESTS
# ==========================================

from engine.windows_services_evidence import (
    WindowsServicesEvidence,
)


def test_empty_evidence_is_valid():
    evidence = WindowsServicesEvidence()

    assert evidence.services == []
    assert evidence.service_count == 0


def test_services_are_stored():
    services = [
        {
            "name": "Spooler",
            "display_name": "Print Spooler",
            "status": "RUNNING",
            "start_type": "AUTO",
        }
    ]

    evidence = WindowsServicesEvidence(
        services=services
    )

    assert evidence.services == services
    assert evidence.service_count == 1


def test_input_services_are_copied():
    services = [
        {
            "name": "Spooler",
            "status": "RUNNING",
        }
    ]

    evidence = WindowsServicesEvidence(
        services=services
    )

    services[0]["status"] = "STOPPED"

    assert (
        evidence.services[0]["status"]
        == "RUNNING"
    )


def test_get_service_is_case_insensitive():
    evidence = WindowsServicesEvidence(
        services=[
            {
                "name": "Spooler",
                "status": "RUNNING",
            }
        ]
    )

    service = evidence.get_service("spooler")

    assert service is not None
    assert service["name"] == "Spooler"


def test_get_service_trims_name():
    evidence = WindowsServicesEvidence(
        services=[
            {
                "name": "Spooler",
                "status": "RUNNING",
            }
        ]
    )

    service = evidence.get_service("  Spooler  ")

    assert service is not None


def test_missing_service_returns_none():
    evidence = WindowsServicesEvidence(
        services=[
            {
                "name": "Spooler",
                "status": "RUNNING",
            }
        ]
    )

    assert evidence.get_service("W32Time") is None


def test_invalid_service_name_returns_none():
    evidence = WindowsServicesEvidence(
        services=[
            {
                "name": "Spooler",
                "status": "RUNNING",
            }
        ]
    )

    assert evidence.get_service(None) is None
    assert evidence.get_service("") is None


def test_get_service_returns_copy():
    evidence = WindowsServicesEvidence(
        services=[
            {
                "name": "Spooler",
                "status": "RUNNING",
            }
        ]
    )

    service = evidence.get_service("Spooler")

    service["status"] = "STOPPED"

    assert (
        evidence.get_service("Spooler")["status"]
        == "RUNNING"
    )


def test_invalid_services_argument_is_rejected():
    try:
        WindowsServicesEvidence(
            services="invalid"
        )
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for invalid services."
    )


def test_none_services_defaults_to_empty():
    evidence = WindowsServicesEvidence(
        services=None
    )

    assert evidence.services == []


def test_invalid_entries_do_not_break_lookup():
    evidence = WindowsServicesEvidence(
        services=[
            "invalid",
            {
                "name": "Spooler",
                "status": "RUNNING",
            },
        ]
    )

    service = evidence.get_service("Spooler")

    assert service is not None