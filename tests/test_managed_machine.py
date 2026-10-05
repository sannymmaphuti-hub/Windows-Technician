import pytest

from engine.managed_machine import ManagedMachine


def test_managed_machine_requires_machine_id():
    with pytest.raises(ValueError):
        ManagedMachine(
            machine_id=None,
            hostname="PC-01",
            platform="Windows",
            operating_system="Windows 11",
        )


def test_managed_machine_requires_hostname():
    with pytest.raises(ValueError):
        ManagedMachine(
            machine_id="machine-1",
            hostname=None,
            platform="Windows",
            operating_system="Windows 11",
        )


def test_managed_machine_requires_platform():
    with pytest.raises(ValueError):
        ManagedMachine(
            machine_id="machine-1",
            hostname="PC-01",
            platform=None,
            operating_system="Windows 11",
        )


def test_managed_machine_requires_operating_system():
    with pytest.raises(ValueError):
        ManagedMachine(
            machine_id="machine-1",
            hostname="PC-01",
            platform="Windows",
            operating_system=None,
        )


def test_managed_machine_stores_identity():
    machine = ManagedMachine(
        machine_id="machine-1",
        hostname="PC-01",
        platform="Windows",
        operating_system="Windows 11",
    )

    assert machine.machine_id == "machine-1"
    assert machine.hostname == "PC-01"
    assert machine.platform == "Windows"
    assert machine.operating_system == "Windows 11"


def test_managed_machine_starts_with_unknown_connection_state():
    machine = ManagedMachine(
        machine_id="machine-1",
        hostname="PC-01",
        platform="Windows",
        operating_system="Windows 11",
    )

    assert machine.connection_state == "UNKNOWN"


def test_managed_machine_starts_with_unknown_health_state():
    machine = ManagedMachine(
        machine_id="machine-1",
        hostname="PC-01",
        platform="Windows",
        operating_system="Windows 11",
    )

    assert machine.health_state == "UNKNOWN"


def test_managed_machine_starts_without_last_seen():
    machine = ManagedMachine(
        machine_id="machine-1",
        hostname="PC-01",
        platform="Windows",
        operating_system="Windows 11",
    )

    assert machine.last_seen is None


def test_managed_machine_can_update_connection_state():
    machine = ManagedMachine(
        machine_id="machine-1",
        hostname="PC-01",
        platform="Windows",
        operating_system="Windows 11",
    )

    machine.connection_state = "CONNECTED"

    assert machine.connection_state == "CONNECTED"


def test_managed_machine_can_update_health_state():
    machine = ManagedMachine(
        machine_id="machine-1",
        hostname="PC-01",
        platform="Windows",
        operating_system="Windows 11",
    )

    machine.health_state = "HEALTHY"

    assert machine.health_state == "HEALTHY"


def test_managed_machine_can_update_last_seen():
    machine = ManagedMachine(
        machine_id="machine-1",
        hostname="PC-01",
        platform="Windows",
        operating_system="Windows 11",
    )

    timestamp = "2026-10-05T07:00:00+00:00"

    machine.last_seen = timestamp

    assert machine.last_seen == timestamp


def test_managed_machine_does_not_own_diagnostic_case():
    machine = ManagedMachine(
        machine_id="machine-1",
        hostname="PC-01",
        platform="Windows",
        operating_system="Windows 11",
    )

    assert not hasattr(machine, "case")
    assert not hasattr(machine, "diagnostic_case")


def test_managed_machine_does_not_own_workflow():
    machine = ManagedMachine(
        machine_id="machine-1",
        hostname="PC-01",
        platform="Windows",
        operating_system="Windows 11",
    )

    assert not hasattr(machine, "workflow")
    assert not hasattr(machine, "technician_workflow")

