import pytest

from engine.application_bootstrap import ApplicationBootstrap


def test_bootstrap_starts_in_starting_state():
    bootstrap = ApplicationBootstrap()

    assert bootstrap.started is False
    assert bootstrap.state.status == "STARTING"


def test_start_transitions_to_ready():
    bootstrap = ApplicationBootstrap()

    state = bootstrap.start()

    assert bootstrap.started is True
    assert state.status == "READY"


def test_start_returns_application_state():
    bootstrap = ApplicationBootstrap()

    state = bootstrap.start()

    assert state is bootstrap.state


def test_start_is_idempotent():
    bootstrap = ApplicationBootstrap()

    first = bootstrap.start()
    second = bootstrap.start()

    assert first is second
    assert bootstrap.started is True
    assert bootstrap.state.status == "READY"


def test_stop_transitions_to_stopped():
    bootstrap = ApplicationBootstrap()

    bootstrap.start()
    state = bootstrap.stop()

    assert bootstrap.started is False
    assert state.status == "STOPPED"


def test_stop_before_start_is_safe():
    bootstrap = ApplicationBootstrap()

    state = bootstrap.stop()

    assert bootstrap.started is False
    assert state.status == "STOPPED"


def test_stop_is_idempotent():
    bootstrap = ApplicationBootstrap()

    bootstrap.start()
    bootstrap.stop()
    state = bootstrap.stop()

    assert bootstrap.started is False
    assert state.status == "STOPPED"


def test_fail_transitions_to_error():
    bootstrap = ApplicationBootstrap()

    state = bootstrap.fail()

    assert bootstrap.started is False
    assert state.status == "ERROR"


def test_failed_bootstrap_can_be_started_again():
    bootstrap = ApplicationBootstrap()

    bootstrap.fail()

    assert bootstrap.state.status == "ERROR"

    state = bootstrap.start()

    assert bootstrap.started is True
    assert state.status == "READY"


def test_configuration_reaches_application_state():
    bootstrap = ApplicationBootstrap(
        configuration={
            "theme": "dark",
            "diagnostics_enabled": True,
        }
    )

    assert bootstrap.state.configuration == {
        "theme": "dark",
        "diagnostics_enabled": True,
    }


def test_custom_application_identity():
    bootstrap = ApplicationBootstrap(
        application_name="Test Technician",
        version="9.9.9",
    )

    assert bootstrap.state.application_name == (
        "Test Technician"
    )
    assert bootstrap.state.version == "9.9.9"


def test_bootstrap_has_no_diagnostic_surface():
    bootstrap = ApplicationBootstrap()

    assert not hasattr(bootstrap, "diagnose")
    assert not hasattr(bootstrap, "analyze")
    assert not hasattr(bootstrap, "remediate")


def test_bootstrap_has_no_execution_surface():
    bootstrap = ApplicationBootstrap()

    assert not hasattr(bootstrap, "execute")


def test_start_does_not_create_active_case():
    bootstrap = ApplicationBootstrap()

    bootstrap.start()

    assert bootstrap.state.active_case_id is None


def test_start_does_not_create_active_machine():
    bootstrap = ApplicationBootstrap()

    bootstrap.start()

    assert bootstrap.state.active_machine_id is None


def test_bootstrap_state_is_serializable():
    bootstrap = ApplicationBootstrap()

    bootstrap.start()

    data = bootstrap.state.to_dict()

    assert data["application_name"] == "Windows Technician"
    assert data["version"] == "0.9.0"
    assert data["status"] == "READY"


@pytest.mark.parametrize(
    "method_name, expected_status",
    [
        ("start", "READY"),
        ("fail", "ERROR"),
    ],
)
def test_lifecycle_methods_set_expected_state(
    method_name,
    expected_status,
):
    bootstrap = ApplicationBootstrap()

    state = getattr(bootstrap, method_name)()

    assert state.status == expected_status


def test_restart_cycle():
    bootstrap = ApplicationBootstrap()

    bootstrap.start()
    bootstrap.stop()
    bootstrap.start()

    assert bootstrap.started is True
    assert bootstrap.state.status == "READY"
