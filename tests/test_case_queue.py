# ==========================================
# Windows Technician v0.8
# CASE QUEUE TESTS
# ==========================================

from engine.diagnostic_case import DiagnosticCase


def build_case(
    lifecycle_state="OPEN",
    machine_id="machine-001",
    hostname="TECH-PC",
):
    case = DiagnosticCase()

    case.machine_id = machine_id
    case.hostname = hostname
    case.lifecycle_state = lifecycle_state

    return case


def test_case_queue_module_exists():
    from engine.case_queue import CaseQueue

    assert CaseQueue is not None


def test_case_queue_can_be_created():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    assert queue is not None


def test_case_queue_starts_empty():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    assert queue.cases == []


def test_case_queue_can_add_case():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()
    case = build_case()

    queue.add_case(case)

    assert queue.cases == [case]


def test_case_queue_rejects_invalid_case():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    try:
        queue.add_case(object())
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Invalid case should raise ValueError."
        )


def test_case_queue_preserves_case_identity():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()
    case = build_case()

    queue.add_case(case)

    assert queue.cases[0] is case


def test_case_queue_can_hold_multiple_cases():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    case_one = build_case(
        machine_id="machine-001"
    )
    case_two = build_case(
        machine_id="machine-002"
    )

    queue.add_case(case_one)
    queue.add_case(case_two)

    assert queue.cases == [
        case_one,
        case_two,
    ]


def test_case_queue_preserves_insertion_order():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    case_one = build_case(
        machine_id="machine-001"
    )
    case_two = build_case(
        machine_id="machine-002"
    )
    case_three = build_case(
        machine_id="machine-003"
    )

    queue.add_case(case_one)
    queue.add_case(case_two)
    queue.add_case(case_three)

    assert queue.cases == [
        case_one,
        case_two,
        case_three,
    ]


def test_case_queue_exposes_case_count():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    queue.add_case(build_case())
    queue.add_case(
        build_case(machine_id="machine-002")
    )

    assert queue.case_count == 2


def test_case_queue_can_filter_by_machine():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    target = build_case(
        machine_id="machine-001"
    )
    other = build_case(
        machine_id="machine-002"
    )

    queue.add_case(target)
    queue.add_case(other)

    results = queue.for_machine("machine-001")

    assert results == [target]


def test_case_queue_machine_filter_returns_empty_when_missing():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    queue.add_case(build_case())

    assert queue.for_machine("missing-machine") == []


def test_case_queue_can_filter_by_lifecycle_state():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    open_case = build_case(
        lifecycle_state="OPEN"
    )
    investigating_case = build_case(
        lifecycle_state="INVESTIGATING",
        machine_id="machine-002",
    )

    queue.add_case(open_case)
    queue.add_case(investigating_case)

    results = queue.by_lifecycle_state(
        "INVESTIGATING"
    )

    assert results == [investigating_case]


def test_case_queue_lifecycle_filter_returns_empty_when_missing():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    queue.add_case(build_case())

    assert queue.by_lifecycle_state(
        "RESOLVED"
    ) == []


def test_case_queue_can_return_open_cases():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    open_case = build_case(
        lifecycle_state="OPEN"
    )
    resolved_case = build_case(
        lifecycle_state="RESOLVED",
        machine_id="machine-002",
    )

    queue.add_case(open_case)
    queue.add_case(resolved_case)

    assert queue.open_cases == [open_case]


def test_case_queue_can_return_active_cases():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    open_case = build_case(
        lifecycle_state="OPEN"
    )
    investigating_case = build_case(
        lifecycle_state="INVESTIGATING",
        machine_id="machine-002",
    )
    resolved_case = build_case(
        lifecycle_state="RESOLVED",
        machine_id="machine-003",
    )

    queue.add_case(open_case)
    queue.add_case(investigating_case)
    queue.add_case(resolved_case)

    assert queue.active_cases == [
        open_case,
        investigating_case,
    ]


def test_case_queue_does_not_mutate_case():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    case = build_case()
    original_state = case.lifecycle_state

    queue.add_case(case)

    assert case.lifecycle_state == original_state


def test_case_queue_does_not_diagnose():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    assert not hasattr(queue, "diagnose")
    assert not hasattr(queue, "diagnostic_pipeline")


def test_case_queue_does_not_authorize():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    assert not hasattr(queue, "authorize")
    assert not hasattr(queue, "authorization_status")


def test_case_queue_does_not_execute():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    assert not hasattr(queue, "execute")
    assert not hasattr(queue, "execution_status")


def test_case_queue_does_not_remediate():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    assert not hasattr(queue, "remediate")
    assert not hasattr(queue, "remediation_action")
    assert not hasattr(queue, "remediation_actions")


def test_case_queue_does_not_create_workflow():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    assert not hasattr(queue, "workflow")
    assert not hasattr(queue, "technician_workflow")


def test_case_queue_uses_existing_case_model():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()
    case = build_case()

    queue.add_case(case)

    assert type(queue.cases[0]) is DiagnosticCase


def test_case_queue_machine_filter_does_not_mutate_cases():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    case = build_case(
        machine_id="machine-001"
    )

    queue.add_case(case)

    results = queue.for_machine(
        "machine-001"
    )

    assert results[0] is case
    assert case.machine_id == "machine-001"


def test_case_queue_lifecycle_filter_does_not_mutate_cases():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    case = build_case(
        lifecycle_state="INVESTIGATING"
    )

    queue.add_case(case)

    results = queue.by_lifecycle_state(
        "INVESTIGATING"
    )

    assert results[0] is case
    assert case.lifecycle_state == "INVESTIGATING"


def test_case_queue_can_combine_machine_and_lifecycle_filters():
    from engine.case_queue import CaseQueue

    queue = CaseQueue()

    target = build_case(
        lifecycle_state="INVESTIGATING",
        machine_id="machine-001",
    )

    wrong_machine = build_case(
        lifecycle_state="INVESTIGATING",
        machine_id="machine-002",
    )

    wrong_state = build_case(
        lifecycle_state="OPEN",
        machine_id="machine-001",
    )

    queue.add_case(target)
    queue.add_case(wrong_machine)
    queue.add_case(wrong_state)

    results = queue.for_machine(
        "machine-001"
    )

    results = [
        case
        for case in results
        if case.lifecycle_state == "INVESTIGATING"
    ]

    assert results == [target]