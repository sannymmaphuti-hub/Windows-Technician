from engine.diagnostic_case import DiagnosticCase
from engine.finding import Finding
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


def build_finding():
    return Finding(
        finding_type="MEMORY_PRESSURE",
        category="MEMORY",
        severity="HIGH",
        description="Memory usage is consistently high.",
    )


def set_finding(workflow, finding):
    workflow.case.set_findings([finding])


def finding_signature(finding):
    return (
        finding.finding_type,
        finding.category,
        finding.severity,
        finding.description,
    )


def case_finding_signatures(workflow):
    return [
        finding_signature(finding)
        for finding in workflow.case.findings
    ]


def test_closure_does_not_create_finding():
    workflow = build_workflow()

    resolve_workflow(workflow)
    findings_before = case_finding_signatures(workflow)

    build_closure(workflow)

    assert case_finding_signatures(workflow) == findings_before


def test_closure_does_not_remove_existing_finding():
    workflow = build_workflow()

    finding = build_finding()
    expected_signature = finding_signature(finding)

    set_finding(workflow, finding)

    resolve_workflow(workflow)
    findings_before = case_finding_signatures(workflow)

    build_closure(workflow)

    assert case_finding_signatures(workflow) == findings_before
    assert expected_signature in case_finding_signatures(workflow)


def test_closure_does_not_replace_existing_finding():
    workflow = build_workflow()

    finding = build_finding()
    expected_signature = finding_signature(finding)

    set_finding(workflow, finding)

    resolve_workflow(workflow)
    build_closure(workflow)

    assert case_finding_signatures(workflow) == [expected_signature]


def test_closure_does_not_change_finding_count():
    workflow = build_workflow()

    set_finding(workflow, build_finding())

    resolve_workflow(workflow)
    count_before = len(workflow.case.findings)

    build_closure(workflow)

    assert len(workflow.case.findings) == count_before


def test_closure_does_not_change_case_evidence():
    workflow = build_workflow()

    set_finding(workflow, build_finding())

    resolve_workflow(workflow)

    evidence_before = dict(workflow.case.evidence)

    build_closure(workflow)

    assert workflow.case.evidence == evidence_before


def test_closure_does_not_appear_as_case_evidence():
    workflow = build_workflow()

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert all(
        value is not closure
        for value in workflow.case.evidence.values()
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


def test_closure_does_not_change_case_findings_after_reopen():
    workflow = build_workflow()

    finding = build_finding()
    expected_signature = finding_signature(finding)

    set_finding(workflow, finding)

    resolve_workflow(workflow)
    build_closure(workflow)

    workflow.reopen()

    assert expected_signature in case_finding_signatures(workflow)
    assert len(workflow.case.findings) == 1


def test_closure_remains_separate_from_finding_identity():
    workflow = build_workflow()

    finding = build_finding()
    expected_signature = finding_signature(finding)

    set_finding(workflow, finding)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert closure is not finding
    assert expected_signature in case_finding_signatures(workflow)


def test_multiple_closures_do_not_duplicate_findings():
    workflow = build_workflow()

    finding = build_finding()
    expected_signature = finding_signature(finding)

    set_finding(workflow, finding)

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
    assert case_finding_signatures(workflow) == [expected_signature]
    assert len(workflow.case.findings) == 1


def test_closure_does_not_become_finding_description():
    workflow = build_workflow()

    finding = build_finding()
    set_finding(workflow, finding)

    resolve_workflow(workflow)
    closure = build_closure(workflow)

    assert workflow.case.findings[0].description != closure.reason


def test_closure_does_not_mutate_finding_metadata():
    workflow = build_workflow()

    finding = build_finding()
    expected_signature = finding_signature(finding)

    set_finding(workflow, finding)

    resolve_workflow(workflow)

    build_closure(workflow)

    assert case_finding_signatures(workflow) == [expected_signature]


def test_closure_does_not_change_case_evidence_count():
    workflow = build_workflow()

    set_finding(workflow, build_finding())

    resolve_workflow(workflow)

    evidence_count_before = len(workflow.case.evidence)

    build_closure(workflow)

    assert len(workflow.case.evidence) == evidence_count_before


def test_closure_is_not_required_for_case_evidence_to_exist():
    workflow = build_workflow()

    finding = build_finding()
    expected_signature = finding_signature(finding)

    set_finding(workflow, finding)

    resolve_workflow(workflow)

    assert expected_signature in case_finding_signatures(workflow)
    assert workflow.case.findings


def test_case_evidence_does_not_create_closure():
    workflow = build_workflow()

    finding = build_finding()
    set_finding(workflow, finding)

    assert workflow.state.value == "OPEN"
    assert workflow.case.findings