import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_recovery_cycle import (
    TechnicianRecoveryCycle,
)
from engine.technician_workflow import TechnicianWorkflow


@pytest.fixture
def workflow():
    return TechnicianWorkflow(
        DiagnosticCase()
    )


def test_cycle_has_started_at(workflow):
    cycle = TechnicianRecoveryCycle(workflow)

    assert cycle.started_at is not None


def test_started_at_is_datetime(workflow):
    from datetime import datetime

    cycle = TechnicianRecoveryCycle(workflow)

    assert isinstance(cycle.started_at, datetime)


def test_original_cycle_is_identified(workflow):
    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=0,
    )

    assert cycle.is_original is True
    assert cycle.is_recovery is False


def test_recovery_cycle_is_identified(workflow):
    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    assert cycle.is_original is False
    assert cycle.is_recovery is True


def test_recovery_cycle_has_unique_start_time(workflow):
    first = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    second = TechnicianRecoveryCycle(
        workflow,
        cycle_number=2,
    )

    assert first.started_at != second.started_at


def test_started_at_is_read_only(workflow):
    cycle = TechnicianRecoveryCycle(workflow)

    with pytest.raises(AttributeError):
        cycle.started_at = None


def test_cycle_number_is_read_only(workflow):
    cycle = TechnicianRecoveryCycle(workflow)

    with pytest.raises(AttributeError):
        cycle.cycle_number = 5


def test_workflow_is_read_only(workflow):
    cycle = TechnicianRecoveryCycle(workflow)

    with pytest.raises(AttributeError):
        cycle.workflow = None