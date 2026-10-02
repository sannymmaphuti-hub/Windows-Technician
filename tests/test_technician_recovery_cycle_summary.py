import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_recovery_cycle import (
    TechnicianRecoveryCycle,
)
from engine.technician_recovery_cycle_history import (
    TechnicianRecoveryCycleHistory,
)
from engine.technician_workflow import TechnicianWorkflow


@pytest.fixture
def workflow():
    workflow = TechnicianWorkflow(
        DiagnosticCase()
    )
    workflow.start_investigation()
    return workflow


@pytest.fixture
def history(workflow):
    return TechnicianRecoveryCycleHistory(
        workflow
    )


def test_summary_requires_history():
    from engine.technician_recovery_cycle_summary import (
        TechnicianRecoveryCycleSummary,
    )

    with pytest.raises(ValueError):
        TechnicianRecoveryCycleSummary(None)


def test_summary_exposes_cycle_count(
    history,
):
    from engine.technician_recovery_cycle_summary import (
        TechnicianRecoveryCycleSummary,
    )

    summary = TechnicianRecoveryCycleSummary(
        history
    )

    assert summary.cycle_count == 1


def test_summary_exposes_current_cycle(
    history,
):
    from engine.technician_recovery_cycle_summary import (
        TechnicianRecoveryCycleSummary,
    )

    summary = TechnicianRecoveryCycleSummary(
        history
    )

    assert summary.current_cycle is (
        history.latest_cycle
    )


def test_summary_identifies_original_cycle(
    history,
):
    from engine.technician_recovery_cycle_summary import (
        TechnicianRecoveryCycleSummary,
    )

    summary = TechnicianRecoveryCycleSummary(
        history
    )

    assert summary.current_cycle_number == 0
    assert summary.is_recovery is False


def test_summary_updates_after_recovery(
    history,
    workflow,
):
    from engine.technician_recovery_cycle_summary import (
        TechnicianRecoveryCycleSummary,
    )

    summary = TechnicianRecoveryCycleSummary(
        history
    )

    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=1,
    )

    history.record_cycle(cycle)

    assert summary.cycle_count == 2
    assert summary.current_cycle_number == 1
    assert summary.is_recovery is True


def test_summary_exposes_start_time(
    history,
):
    from engine.technician_recovery_cycle_summary import (
        TechnicianRecoveryCycleSummary,
    )

    summary = TechnicianRecoveryCycleSummary(
        history
    )

    assert summary.started_at is (
        history.latest_cycle.started_at
    )


def test_summary_exposes_outcome(
    history,
):
    from engine.technician_recovery_cycle_summary import (
        TechnicianRecoveryCycleSummary,
    )

    summary = TechnicianRecoveryCycleSummary(
        history
    )

    assert summary.outcome == "ACTIVE"


def test_summary_is_read_only(
    history,
):
    from engine.technician_recovery_cycle_summary import (
        TechnicianRecoveryCycleSummary,
    )

    summary = TechnicianRecoveryCycleSummary(
        history
    )

    with pytest.raises(AttributeError):
        summary.cycle_count = 99


def test_summary_tracks_resolution(
    history,
    workflow,
):
    from engine.technician_recovery_cycle_summary import (
        TechnicianRecoveryCycleSummary,
    )

    summary = TechnicianRecoveryCycleSummary(
        history
    )

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert summary.outcome == "RESOLVED"