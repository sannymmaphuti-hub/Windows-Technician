from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import TechnicianRecoveryCycleHistory
from engine.technician_workflow import TechnicianWorkflow
from engine.diagnostic_case import DiagnosticCase


def build_workflow():
    case = DiagnosticCase()
    return TechnicianWorkflow(case)


def build_history(workflow):
    return TechnicianRecoveryCycleHistory(workflow)


def build_recovery_cycle(workflow):
    return TechnicianRecoveryCycle(workflow)


def resolve_workflow(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()


def build_closure(workflow):
    return TechnicianCaseClosure(
        workflow=workflow,
        technician="Test Technician",
        reason="Issue resolved and verified.",
    )


def test_closure_does_not_create_recovery_cycle():
    workflow = build_workflow()
    history = build_history(workflow)

    cycle_numbers_before = [
        cycle.cycle_number
        for cycle in history.cycles
    ]

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert closure.workflow is workflow
    assert [
        cycle.cycle_number
        for cycle in history.cycles
    ] == cycle_numbers_before


def test_closure_does_not_change_recovery_cycle_count():
    workflow = build_workflow()
    history = build_history(workflow)

    resolve_workflow(workflow)
    cycle_count_before = len(history.cycles)

    build_closure(workflow)

    assert len(history.cycles) == cycle_count_before


def test_closure_does_not_change_existing_cycle_identity():
    workflow = build_workflow()
    history = build_history(workflow)

    original_cycles = list(history.cycles)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert closure.workflow is workflow
    assert history.cycles == original_cycles


def test_closure_does_not_change_cycle_numbers():
    workflow = build_workflow()
    history = build_history(workflow)

    resolve_workflow(workflow)

    cycle_numbers_before = [
        cycle.cycle_number
        for cycle in history.cycles
    ]

    build_closure(workflow)

    cycle_numbers_after = [
        cycle.cycle_number
        for cycle in history.cycles
    ]

    assert cycle_numbers_after == cycle_numbers_before


def test_closure_does_not_change_recovery_history_identity():
    workflow = build_workflow()
    history = build_history(workflow)

    resolve_workflow(workflow)

    original_history = history
    original_cycles = list(history.cycles)

    closure = build_closure(workflow)

    assert closure.workflow is workflow
    assert history is original_history
    assert history.cycles == original_cycles


def test_recovery_cycle_can_exist_before_closure():
    workflow = build_workflow()

    workflow.start_investigation()

    history = build_history(workflow)
    cycle = build_recovery_cycle(workflow)

    assert cycle.workflow is workflow
    assert cycle.cycle_number >= 0

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    closure = build_closure(workflow)

    assert closure.workflow is workflow
    assert cycle.workflow is workflow


def test_closure_does_not_replace_recovery_cycle():
    workflow = build_workflow()
    history = build_history(workflow)

    resolve_workflow(workflow)

    original_cycles = list(history.cycles)

    closure = build_closure(workflow)

    assert closure.workflow is workflow
    assert history.cycles == original_cycles


def test_recovery_cycle_does_not_create_closure():
    workflow = build_workflow()

    cycle = build_recovery_cycle(workflow)

    assert cycle.workflow is workflow
    assert workflow.state.value == "OPEN"


def test_closure_requires_resolved_workflow_even_with_recovery_cycle():
    workflow = build_workflow()

    build_history(workflow)
    build_recovery_cycle(workflow)

    try:
        build_closure(workflow)
    except ValueError as exc:
        assert str(exc) == "A case can only be closed after it is RESOLVED."
    else:
        raise AssertionError(
            "Closure should not be allowed before the workflow is RESOLVED."
        )


def test_closure_does_not_change_workflow_state():
    workflow = build_workflow()
    build_history(workflow)

    resolve_workflow(workflow)

    state_before = workflow.state
    history_before = workflow.history

    build_closure(workflow)

    assert workflow.state is state_before
    assert workflow.history == history_before


def test_closure_does_not_change_workflow_history():
    workflow = build_workflow()
    build_history(workflow)

    resolve_workflow(workflow)

    history_before = workflow.history

    build_closure(workflow)

    assert workflow.history == history_before


def test_recovery_cycle_and_closure_share_same_workflow_without_becoming_each_other():
    workflow = build_workflow()
    history = build_history(workflow)

    resolve_workflow(workflow)

    cycle = build_recovery_cycle(workflow)
    closure = build_closure(workflow)

    assert cycle.workflow is workflow
    assert closure.workflow is workflow
    assert cycle is not closure
    assert history.workflow is workflow


def test_closure_does_not_create_second_recovery_cycle():
    workflow = build_workflow()
    history = build_history(workflow)

    resolve_workflow(workflow)

    cycles_before = list(history.cycles)

    build_closure(workflow)

    assert history.cycles == cycles_before
    assert len(history.cycles) == len(cycles_before)


def test_recovery_cycle_history_remains_sequential_after_closure():
    workflow = build_workflow()
    history = build_history(workflow)

    resolve_workflow(workflow)

    build_closure(workflow)

    cycle_numbers = [
        cycle.cycle_number
        for cycle in history.cycles
    ]

    assert cycle_numbers == sorted(cycle_numbers)
    assert len(cycle_numbers) == len(set(cycle_numbers))


def test_closure_metadata_does_not_contaminate_recovery_cycle_data():
    workflow = build_workflow()
    history = build_history(workflow)

    resolve_workflow(workflow)

    cycles_before = [
        (
            cycle.cycle_number,
            cycle.workflow,
            cycle.outcome,
        )
        for cycle in history.cycles
    ]

    closure = build_closure(workflow)

    cycles_after = [
        (
            cycle.cycle_number,
            cycle.workflow,
            cycle.outcome,
        )
        for cycle in history.cycles
    ]

    assert closure.workflow is workflow
    assert cycles_after == cycles_before


def test_recovery_history_does_not_store_closure_as_a_cycle():
    workflow = build_workflow()
    history = build_history(workflow)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert all(
        cycle is not closure
        for cycle in history.cycles
    )


def test_closure_identity_is_independent_from_recovery_cycle_number():
    workflow = build_workflow()
    history = build_history(workflow)

    resolve_workflow(workflow)

    cycle = build_recovery_cycle(workflow)
    closure = build_closure(workflow)

    assert cycle is not closure
    assert isinstance(cycle.cycle_number, int)
    assert isinstance(closure.closure_id, str)


def test_recovery_cycle_number_survives_closure():
    workflow = build_workflow()
    history = build_history(workflow)

    resolve_workflow(workflow)

    cycle = build_recovery_cycle(workflow)
    cycle_number_before = cycle.cycle_number

    build_closure(workflow)

    assert cycle.cycle_number == cycle_number_before
    assert cycle.workflow is workflow


def test_closure_identity_survives_recovery_history_inspection():
    workflow = build_workflow()
    history = build_history(workflow)

    resolve_workflow(workflow)

    closure = build_closure(workflow)
    closure_id_before = closure.closure_id

    _ = history.cycles

    assert closure.closure_id == closure_id_before


def test_closure_does_not_create_additional_cycle_after_recovery():
    workflow = build_workflow()

    workflow.start_investigation()

    history = build_history(workflow)
    cycle = build_recovery_cycle(workflow)

    cycle_numbers_before = [
        cycle.cycle_number
        for cycle in history.cycles
    ]

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    closure = build_closure(workflow)

    assert closure.workflow is workflow
    assert [
        cycle.cycle_number
        for cycle in history.cycles
    ] == cycle_numbers_before


def test_recovery_cycle_and_closure_remain_independent_after_closure_creation():
    workflow = build_workflow()
    history = build_history(workflow)

    resolve_workflow(workflow)

    cycle = build_recovery_cycle(workflow)
    closure = build_closure(workflow)

    assert cycle.workflow is workflow
    assert closure.workflow is workflow
    assert cycle is not closure
    assert history.workflow is workflow


def test_closure_does_not_mutate_recovery_cycle_object():
    workflow = build_workflow()
    build_history(workflow)

    resolve_workflow(workflow)

    cycle = build_recovery_cycle(workflow)

    cycle_number_before = cycle.cycle_number
    cycle_outcome_before = cycle.outcome
    cycle_workflow_before = cycle.workflow

    build_closure(workflow)

    assert cycle.cycle_number == cycle_number_before
    assert cycle.outcome == cycle_outcome_before
    assert cycle.workflow is cycle_workflow_before


def test_recovery_cycle_history_remains_owned_by_workflow():
    workflow = build_workflow()
    history = build_history(workflow)

    resolve_workflow(workflow)

    build_recovery_cycle(workflow)
    closure = build_closure(workflow)

    assert history.workflow is workflow
    assert closure.workflow is workflow