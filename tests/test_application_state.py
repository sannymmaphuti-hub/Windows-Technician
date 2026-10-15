from copy import deepcopy

import pytest

from engine.application_state import ApplicationState


def test_default_application_state():
    state = ApplicationState()

    assert state.application_name == "Windows Technician"
    assert state.version == "1.0.0"
    assert state.status == "STARTING"
    assert state.configuration == {}
    assert state.active_case_id is None
    assert state.active_machine_id is None


def test_custom_application_state():
    state = ApplicationState(
        application_name="Test Technician",
        version="1.2.3",
        status="READY",
        configuration={
            "theme": "dark",
        },
        active_case_id="case-01",
        active_machine_id="machine-01",
    )

    assert state.application_name == "Test Technician"
    assert state.version == "1.2.3"
    assert state.status == "READY"
    assert state.configuration == {
        "theme": "dark",
    }
    assert state.active_case_id == "CASE-01"
    assert state.active_machine_id == "MACHINE-01"


def test_status_is_normalized():
    state = ApplicationState(status=" ready ")

    assert state.status == "READY"


@pytest.mark.parametrize(
    "status",
    [
        "STARTING",
        "READY",
        "BUSY",
        "ERROR",
        "STOPPING",
        "STOPPED",
    ],
)
def test_supported_statuses(status):
    state = ApplicationState(status=status)

    assert state.status == status


def test_invalid_status_is_rejected():
    with pytest.raises(ValueError):
        ApplicationState(status="INVALID")


def test_non_string_status_is_rejected():
    with pytest.raises(ValueError):
        ApplicationState(status=123)


def test_application_name_is_required():
    with pytest.raises(ValueError):
        ApplicationState(application_name="")


def test_version_is_required():
    with pytest.raises(ValueError):
        ApplicationState(version="")


def test_case_identifier_is_normalized():
    state = ApplicationState(
        active_case_id=" case-123 "
    )

    assert state.active_case_id == "CASE-123"


def test_machine_identifier_is_normalized():
    state = ApplicationState(
        active_machine_id=" machine-123 "
    )

    assert state.active_machine_id == "MACHINE-123"


def test_empty_optional_identifier_is_rejected():
    with pytest.raises(ValueError):
        ApplicationState(active_case_id="")


def test_non_string_optional_identifier_is_rejected():
    with pytest.raises(ValueError):
        ApplicationState(active_machine_id=123)


def test_set_status():
    state = ApplicationState()

    state.set_status("READY")

    assert state.status == "READY"


def test_set_active_case():
    state = ApplicationState()

    state.set_active_case("case-10")

    assert state.active_case_id == "CASE-10"


def test_set_active_machine():
    state = ApplicationState()

    state.set_active_machine("machine-10")

    assert state.active_machine_id == "MACHINE-10"


def test_clear_active_context():
    state = ApplicationState(
        active_case_id="case-10",
        active_machine_id="machine-10",
    )

    state.clear_active_context()

    assert state.active_case_id is None
    assert state.active_machine_id is None


def test_configuration_is_defensively_copied():
    configuration = {
        "diagnostics": {
            "enabled": True,
        }
    }

    state = ApplicationState(
        configuration=configuration
    )

    configuration["diagnostics"]["enabled"] = False

    assert (
        state.configuration["diagnostics"]["enabled"]
        is True
    )


def test_to_dict_contains_canonical_fields():
    state = ApplicationState(
        status="READY",
        configuration={
            "theme": "dark",
        },
        active_case_id="case-01",
        active_machine_id="machine-01",
    )

    data = state.to_dict()

    assert data == {
        "application_name": "Windows Technician",
        "version": "1.0.0",
        "status": "READY",
        "configuration": {
            "theme": "dark",
        },
        "active_case_id": "CASE-01",
        "active_machine_id": "MACHINE-01",
    }


def test_to_dict_returns_defensive_configuration_copy():
    state = ApplicationState(
        configuration={
            "theme": "dark",
        }
    )

    data = state.to_dict()

    data["configuration"]["theme"] = "light"

    assert state.configuration["theme"] == "dark"


def test_application_state_has_no_execution_surface():
    state = ApplicationState()

    assert not hasattr(state, "execute")
    assert not hasattr(state, "remediate")
    assert not hasattr(state, "diagnose")
    assert not hasattr(state, "recommend")


def test_application_state_is_not_diagnostic_state():
    state = ApplicationState()

    data = state.to_dict()

    assert "findings" not in data
    assert "root_causes" not in data
    assert "recommendations" not in data
    assert "remediation" not in data
