from engine.diagnostic_case import DiagnosticCase
from engine.root_cause import RootCauseCandidate
from engine.technician_case_closure import TechnicianCaseClosure
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


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


def build_root_cause():
    return RootCauseCandidate(
        cause="Sustained memory pressure caused system instability.",
        category="MEMORY",
        confidence=0.90,
        evidence=["memory_usage"],
        reason="Memory usage remained consistently high.",
    )


def set_root_cause(workflow, root_cause):
    workflow.case.set_root_causes([root_cause])


def root_cause_signature(root_cause):
    return (
        root_cause.cause,
        root_cause.category,
        root_cause.confidence,
        root_cause.reason,
    )


def case_root_cause_signatures(workflow):
    return [
        root_cause_signature(root_cause)
        for root_cause in workflow.case.root_causes
    ]


def test_closure_does_not_create_root_cause():
    workflow = build_workflow()

    resolve_workflow(workflow)
    root_causes_before = case_root_cause_signatures(workflow)

    build_closure(workflow)

    assert case_root_cause_signatures(workflow) == root_causes_before


def test_closure_does_not_remove_existing_root_cause():
    workflow = build_workflow()

    root_cause = build_root_cause()
    expected_signature = root_cause_signature(root_cause)

    set_root_cause(workflow, root_cause)

    resolve_workflow(workflow)
    root_causes_before = case_root_cause_signatures(workflow)

    build_closure(workflow)

    assert case_root_cause_signatures(workflow) == root_causes_before
    assert expected_signature in case_root_cause_signatures(workflow)


def test_closure_does_not_replace_existing_root_cause():
    workflow = build_workflow()

    root_cause = build_root_cause()
    expected_signature = root_cause_signature(root_cause)

    set_root_cause(workflow, root_cause)

    resolve_workflow(workflow)
    build_closure(workflow)

    assert case_root_cause_signatures(workflow) == [expected_signature]


def test_closure_does_not_change_root_cause_count():
    workflow = build_workflow()

    set_root_cause(workflow, build_root_cause())

    resolve_workflow(workflow)
    count_before = len(workflow.case.root_causes)

    build_closure(workflow)

    assert len(workflow.case.root_causes) == count_before


def test_closure_does_not_change_case_evidence():
    workflow = build_workflow()

    set_root_cause(workflow, build_root_cause())

    resolve_workflow(workflow)

    evidence_before = dict(workflow.case.evidence)

    build_closure(workflow)

    assert workflow.case.evidence == evidence_before


def test_closure_does_not_appear_as_root_cause():
    workflow = build_workflow()

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert all(
        value is not closure
        for value in workflow.case.root_causes
    )


def test_closure_does_not_change_case_identity():
    workflow = build_workflow()

    case_id_before = workflow.case.case_id

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert workflow.case.case_id == case_id_before
    assert closure.workflow.case.case_id == case_id_before


def test_closure_does_not_change_case_status():
    workflow = build_workflow()

    resolve_workflow(workflow)

    status_before = workflow.case.status

    build_closure(workflow)

    assert workflow.case.status == status_before


def test_closure_does_not_change_root_causes_after_reopen():
    workflow = build_workflow()

    root_cause = build_root_cause()
    expected_signature = root_cause_signature(root_cause)

    set_root_cause(workflow, root_cause)

    resolve_workflow(workflow)
    build_closure(workflow)

    workflow.reopen()

    assert expected_signature in case_root_cause_signatures(workflow)
    assert len(workflow.case.root_causes) == 1


def test_closure_remains_separate_from_root_cause_identity():
    workflow = build_workflow()

    root_cause = build_root_cause()
    expected_signature = root_cause_signature(root_cause)

    set_root_cause(workflow, root_cause)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert closure is not root_cause
    assert expected_signature in case_root_cause_signatures(workflow)


def test_multiple_closures_do_not_duplicate_root_causes():
    workflow = build_workflow()

    root_cause = build_root_cause()
    expected_signature = root_cause_signature(root_cause)

    set_root_cause(workflow, root_cause)

    resolve_workflow(workflow)
    first_closure = build_closure(workflow)

    workflow.reopen()

    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    second_closure = TechnicianCaseClosure(
        workflow=workflow,
        technician="Second Technician",
        reason="Issue resolved after another recovery cycle.",
    )

    assert first_closure is not second_closure
    assert case_root_cause_signatures(workflow) == [expected_signature]
    assert len(workflow.case.root_causes) == 1


def test_closure_does_not_become_root_cause():
    workflow = build_workflow()

    root_cause = build_root_cause()
    set_root_cause(workflow, root_cause)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert closure not in workflow.case.root_causes


def test_closure_does_not_mutate_root_cause_metadata():
    workflow = build_workflow()

    root_cause = build_root_cause()
    expected_signature = root_cause_signature(root_cause)

    set_root_cause(workflow, root_cause)

    resolve_workflow(workflow)

    build_closure(workflow)

    assert case_root_cause_signatures(workflow) == [expected_signature]


def test_closure_does_not_change_case_root_cause_count_after_reopen():
    workflow = build_workflow()

    set_root_cause(workflow, build_root_cause())

    resolve_workflow(workflow)

    build_closure(workflow)
    workflow.reopen()

    assert len(workflow.case.root_causes) == 1


def test_closure_is_not_required_for_root_cause_to_exist():
    workflow = build_workflow()

    root_cause = build_root_cause()
    expected_signature = root_cause_signature(root_cause)

    set_root_cause(workflow, root_cause)

    resolve_workflow(workflow)

    assert expected_signature in case_root_cause_signatures(workflow)
    assert workflow.case.root_causes


def test_case_root_cause_does_not_create_closure():
    workflow = build_workflow()

    root_cause = build_root_cause()
    set_root_cause(workflow, root_cause)

    assert workflow.state.value == "OPEN"
    assert workflow.case.root_causes