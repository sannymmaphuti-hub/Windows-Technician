import pytest

from engine.diagnostic_case import DiagnosticCase
from engine.technician_activity_log import TechnicianActivityLog
from engine.technician_case_reopening_manager import (
    TechnicianCaseReopeningManager,
)
from engine.technician_reopening_recovery_record import (
    TechnicianReopeningRecoveryRecord,
)
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


@pytest.fixture
def resolved_workflow():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    return workflow


@pytest.fixture
def manager(resolved_workflow):
    return TechnicianCaseReopeningManager(
        resolved_workflow
    )


@pytest.fixture
def reopening(manager):
    return manager.request_reopening(
        "Technician B",
        "Issue returned after closure.",
    )


@pytest.fixture
def activity_log(resolved_workflow):
    return TechnicianActivityLog(
        resolved_workflow
    )


def test_integration_requires_workflow():
    from engine.technician_reopening_recovery_integration import (
        TechnicianReopeningRecoveryIntegration,
    )

    with pytest.raises(ValueError):
        TechnicianReopeningRecoveryIntegration(None)


def test_integration_exposes_workflow(
    resolved_workflow,
):
    from engine.technician_reopening_recovery_integration import (
        TechnicianReopeningRecoveryIntegration,
    )

    integration = TechnicianReopeningRecoveryIntegration(
        resolved_workflow
    )

    assert integration.workflow is resolved_workflow


def test_integration_exposes_recovery_record(
    resolved_workflow,
):
    from engine.technician_reopening_recovery_integration import (
        TechnicianReopeningRecoveryIntegration,
    )

    integration = TechnicianReopeningRecoveryIntegration(
        resolved_workflow
    )

    assert isinstance(
        integration.recovery_record,
        TechnicianReopeningRecoveryRecord,
    )


def test_integration_exposes_activity_log(
    resolved_workflow,
):
    from engine.technician_reopening_recovery_integration import (
        TechnicianReopeningRecoveryIntegration,
    )

    integration = TechnicianReopeningRecoveryIntegration(
        resolved_workflow
    )

    assert isinstance(
        integration.activity_log,
        TechnicianActivityLog,
    )


def test_record_recovery(
    resolved_workflow,
    manager,
    reopening,
):
    from engine.technician_reopening_recovery_integration import (
        TechnicianReopeningRecoveryIntegration,
    )

    integration = TechnicianReopeningRecoveryIntegration(
        resolved_workflow
    )

    manager.accept_reopening(reopening)

    entry = integration.record_recovery(
        reopening
    )

    assert entry["type"] == "REOPENING_RECOVERY"
    assert entry["status"] == "RECOVERED"


def test_recovery_record_is_updated(
    resolved_workflow,
    manager,
    reopening,
):
    from engine.technician_reopening_recovery_integration import (
        TechnicianReopeningRecoveryIntegration,
    )

    integration = TechnicianReopeningRecoveryIntegration(
        resolved_workflow
    )

    manager.accept_reopening(reopening)

    integration.record_recovery(reopening)

    assert len(
        integration.recovery_record.entries
    ) == 1


def test_activity_log_records_recovery(
    resolved_workflow,
    manager,
    reopening,
):
    from engine.technician_reopening_recovery_integration import (
        TechnicianReopeningRecoveryIntegration,
    )

    integration = TechnicianReopeningRecoveryIntegration(
        resolved_workflow
    )

    manager.accept_reopening(reopening)

    integration.record_recovery(reopening)

    entries = integration.activity_log.entries

    assert len(entries) == 1
    assert entries[0]["type"] == (
        "REOPENING_RECOVERY"
    )
    assert entries[0]["status"] == "RECOVERED"


def test_recovery_preserves_workflow_state(
    resolved_workflow,
    manager,
    reopening,
):
    from engine.technician_reopening_recovery_integration import (
        TechnicianReopeningRecoveryIntegration,
    )

    integration = TechnicianReopeningRecoveryIntegration(
        resolved_workflow
    )

    manager.accept_reopening(reopening)

    integration.record_recovery(reopening)

    assert resolved_workflow.state is (
        WorkflowState.INVESTIGATING
    )


def test_recovery_does_not_duplicate_record(
    resolved_workflow,
    manager,
    reopening,
):
    from engine.technician_reopening_recovery_integration import (
        TechnicianReopeningRecoveryIntegration,
    )

    integration = TechnicianReopeningRecoveryIntegration(
        resolved_workflow
    )

    manager.accept_reopening(reopening)

    integration.record_recovery(reopening)

    assert len(
        integration.recovery_record.entries
    ) == 1

    assert len(
        integration.activity_log.entries
    ) == 1


def test_foreign_reopening_is_rejected(
    resolved_workflow,
):
    from engine.technician_reopening_recovery_integration import (
        TechnicianReopeningRecoveryIntegration,
    )

    foreign_case = DiagnosticCase()
    foreign_workflow = TechnicianWorkflow(
        foreign_case
    )

    foreign_workflow.start_investigation()
    foreign_workflow.mark_diagnosed()
    foreign_workflow.require_action()
    foreign_workflow.start_remediation()
    foreign_workflow.start_verification()
    foreign_workflow.resolve()

    foreign_manager = (
        TechnicianCaseReopeningManager(
            foreign_workflow
        )
    )

    foreign_reopening = (
        foreign_manager.request_reopening(
            "Technician C",
            "Foreign issue.",
        )
    )

    integration = TechnicianReopeningRecoveryIntegration(
        resolved_workflow
    )

    with pytest.raises(ValueError):
        integration.record_recovery(
            foreign_reopening
        )