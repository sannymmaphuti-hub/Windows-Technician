from engine.diagnostic_case import DiagnosticCase
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import TechnicianRecoveryCycleHistory
from engine.technician_workflow import TechnicianWorkflow, WorkflowState


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def build_history(workflow):
    return TechnicianRecoveryCycleHistory(workflow)


def prepare_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()


def record_cycle(workflow, history, cycle_number):
    cycle = TechnicianRecoveryCycle(
        workflow,
        cycle_number=cycle_number,
    )
    history.record_cycle(cycle)
    return cycle


def test_recovery_history_survives_escalation():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()

    cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    workflow.escalate()

    assert workflow.state == WorkflowState.ESCALATED
    assert cycle in history.cycles
    assert history.cycles[-1] is cycle


def test_escalation_does_not_remove_recovery_history():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()

    cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    cycles_before = list(history.cycles)

    workflow.escalate()

    assert history.cycles == cycles_before
    assert history.cycles[-1] is cycle


def test_escalation_does_not_duplicate_recovery_history():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()

    cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    workflow.escalate()

    assert history.cycles.count(cycle) == 1
    assert len(history.cycles) == 2


def test_recovery_cycle_workflow_identity_survives_escalation():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()

    cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    workflow.escalate()

    assert cycle.workflow is workflow
    assert history.cycles[-1].workflow is workflow


def test_recovery_history_remains_separate_from_escalated_workflow_history():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()

    cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    workflow.escalate()

    assert cycle not in workflow.history
    assert cycle in history.cycles
    assert history.cycles[-1] is cycle


def test_recovery_history_order_survives_escalation():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()

    first_cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    second_cycle = record_cycle(
        workflow,
        history,
        cycle_number=2,
    )

    workflow.escalate()

    assert [cycle.cycle_number for cycle in history.cycles[1:]] == [1, 2]
    assert history.cycles[-2] is first_cycle
    assert history.cycles[-1] is second_cycle


def test_escalation_does_not_change_recovery_cycle_identity():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()

    cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    workflow.escalate()

    assert history.cycles[-1] is cycle
    assert cycle.cycle_number == 1


def test_escalated_workflow_remains_terminal_without_affecting_recovery_history():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()

    cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    workflow.escalate()

    assert workflow.state == WorkflowState.ESCALATED
    assert workflow.is_terminal is True
    assert history.cycles[-1] is cycle


def test_recovery_history_preserves_multiple_cycles_before_escalation():
    workflow = build_workflow()
    history = build_history(workflow)

    workflow.start_investigation()

    first_cycle = record_cycle(
        workflow,
        history,
        cycle_number=1,
    )

    second_cycle = record_cycle(
        workflow,
        history,
        cycle_number=2,
    )

    third_cycle = record_cycle(
        workflow,
        history,
        cycle_number=3,
    )

    workflow.escalate()

    assert [cycle.cycle_number for cycle in history.cycles[1:]] == [1, 2, 3]
    assert history.cycles[-3] is first_cycle
    assert history.cycles[-2] is second_cycle
    assert history.cycles[-1] is third_cycle