from engine.diagnostic_case import DiagnosticCase
from engine.finding import Finding
from engine.recommendation import Recommendation
from engine.root_cause import RootCauseCandidate
from engine.technician_case_notes import TechnicianCaseNotes
from engine.technician_case_summary import TechnicianCaseSummary
from engine.technician_recovery_cycle import TechnicianRecoveryCycle
from engine.technician_recovery_cycle_history import TechnicianRecoveryCycleHistory
from engine.technician_reasoning_summary import TechnicianReasoningSummary
from engine.technician_workflow import TechnicianWorkflow


def build_workflow():
    return TechnicianWorkflow(DiagnosticCase())


def build_finding():
    return Finding(
        "TEST_FINDING",
        "TEST",
        "HIGH",
        "Test finding description",
    )


def build_second_finding():
    return Finding(
        "TEST_FINDING_2",
        "TEST",
        "MEDIUM",
        "Second test finding description",
    )


def build_root_cause():
    return RootCauseCandidate(
        cause="Test root cause",
        category="TEST",
        confidence=0.90,
        evidence=[],
        reason="Test root cause reason",
    )


def build_recommendation():
    return Recommendation(
        "test-recommendation",
        "Test recommendation",
        "MEDIUM",
        "Test recommendation description",
        "Test recommendation rationale",
    )


def populate_diagnostic_content(workflow):
    workflow.case.findings.append(build_finding())
    workflow.case.root_causes.append(build_root_cause())
    workflow.case.recommendations.append(build_recommendation())


def build_notes(workflow):
    notes = TechnicianCaseNotes(workflow)
    notes.add_note("Initial technician observation.")
    notes.add_note("Follow-up technician observation.")
    return notes


def build_recovery_history(workflow):
    history = TechnicianRecoveryCycleHistory(workflow)

    history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=1,
        )
    )

    return history


def build_summary_with_reasoning(workflow, history):
    summary = TechnicianCaseSummary(workflow)

    reasoning_summary = TechnicianReasoningSummary(
        workflow,
        history,
    )

    summary.set_reasoning_summary(reasoning_summary)

    return summary


def test_summary_exposes_diagnostic_content_while_notes_exist_separately():
    workflow = build_workflow()

    populate_diagnostic_content(workflow)
    notes = build_notes(workflow)

    summary = TechnicianCaseSummary(workflow)

    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1

    assert len(notes.notes) == 2
    assert all(note.workflow_state == workflow.state for note in notes.notes)


def test_adding_notes_does_not_change_diagnostic_content():
    workflow = build_workflow()

    populate_diagnostic_content(workflow)
    notes = build_notes(workflow)

    summary_before = TechnicianCaseSummary(workflow)

    findings_before = summary_before.findings
    root_causes_before = summary_before.root_causes
    recommendations_before = summary_before.recommendations

    notes.add_note("Third technician observation.")

    summary_after = TechnicianCaseSummary(workflow)

    assert summary_after.findings == findings_before
    assert summary_after.root_causes == root_causes_before
    assert summary_after.recommendations == recommendations_before
    assert len(notes.notes) == 3


def test_diagnostic_content_does_not_change_existing_notes():
    workflow = build_workflow()

    notes = build_notes(workflow)
    notes_before = notes.notes

    populate_diagnostic_content(workflow)

    summary = TechnicianCaseSummary(workflow)

    assert notes.notes == notes_before
    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1


def test_notes_collection_returns_snapshot_reads():
    workflow = build_workflow()

    notes = build_notes(workflow)

    snapshot = notes.notes

    assert len(snapshot) == 2

    snapshot.clear()

    assert len(notes.notes) == 2


def test_diagnostic_collections_are_snapshot_reads():
    workflow = build_workflow()

    populate_diagnostic_content(workflow)
    summary = TechnicianCaseSummary(workflow)

    findings = summary.findings
    root_causes = summary.root_causes
    recommendations = summary.recommendations

    findings.clear()
    root_causes.clear()
    recommendations.clear()

    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1


def test_notes_and_diagnostic_content_coexist_with_recovery_history():
    workflow = build_workflow()

    populate_diagnostic_content(workflow)
    notes = build_notes(workflow)
    history = build_recovery_history(workflow)

    summary = build_summary_with_reasoning(workflow, history)

    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1

    assert len(notes.notes) == 2

    assert summary.reasoning_summary is not None
    assert summary.reasoning_summary.workflow is workflow
    assert summary.reasoning_summary.cycle_history is history
    assert len(summary.reasoning_summary.cycle_history.cycles) == 2


def test_adding_recovery_cycle_does_not_change_notes_or_diagnostic_content():
    workflow = build_workflow()

    populate_diagnostic_content(workflow)
    notes = build_notes(workflow)
    history = build_recovery_history(workflow)

    summary_before = build_summary_with_reasoning(workflow, history)

    notes_before = notes.notes
    findings_before = summary_before.findings
    root_causes_before = summary_before.root_causes
    recommendations_before = summary_before.recommendations

    history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=2,
        )
    )

    summary_after = build_summary_with_reasoning(workflow, history)

    assert notes.notes == notes_before
    assert summary_after.findings == findings_before
    assert summary_after.root_causes == root_causes_before
    assert summary_after.recommendations == recommendations_before

    assert len(summary_after.reasoning_summary.cycle_history.cycles) == 3


def test_all_surfaces_remain_attached_to_same_workflow_and_case():
    workflow = build_workflow()

    populate_diagnostic_content(workflow)
    notes = build_notes(workflow)
    history = build_recovery_history(workflow)

    summary = build_summary_with_reasoning(workflow, history)

    assert summary.workflow is workflow
    assert summary.case_id == workflow.case.case_id
    assert summary.workflow_id == workflow.workflow_id

    assert summary.reasoning_summary.workflow is workflow
    assert summary.reasoning_summary.cycle_history is history

    assert all(note.workflow_state == workflow.state for note in notes.notes)


def test_repeated_summary_reads_do_not_duplicate_diagnostic_content():
    workflow = build_workflow()

    populate_diagnostic_content(workflow)
    notes = build_notes(workflow)
    history = build_recovery_history(workflow)

    summary_one = build_summary_with_reasoning(workflow, history)
    summary_two = build_summary_with_reasoning(workflow, history)
    summary_three = build_summary_with_reasoning(workflow, history)

    assert len(summary_one.findings) == 1
    assert len(summary_two.findings) == 1
    assert len(summary_three.findings) == 1

    assert len(summary_one.root_causes) == 1
    assert len(summary_two.root_causes) == 1
    assert len(summary_three.root_causes) == 1

    assert len(summary_one.recommendations) == 1
    assert len(summary_two.recommendations) == 1
    assert len(summary_three.recommendations) == 1

    assert len(notes.notes) == 2
    assert len(history.cycles) == 2


def test_repeated_notes_reads_do_not_duplicate_notes():
    workflow = build_workflow()

    notes = build_notes(workflow)

    first = notes.notes
    second = notes.notes
    third = notes.notes

    assert len(first) == 2
    assert len(second) == 2
    assert len(third) == 2

    assert first == second
    assert second == third


def test_complete_surface_remains_consistent_after_multiple_updates():
    workflow = build_workflow()

    populate_diagnostic_content(workflow)
    notes = build_notes(workflow)
    history = build_recovery_history(workflow)

    notes.add_note(
        "Technician identified a possible contributing factor."
    )

    workflow.case.findings.append(build_second_finding())

    history.record_cycle(
        TechnicianRecoveryCycle(
            workflow,
            cycle_number=2,
        )
    )

    summary = build_summary_with_reasoning(workflow, history)

    assert len(notes.notes) == 3

    assert len(summary.findings) == 2
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1

    assert len(summary.reasoning_summary.cycle_history.cycles) == 3

    assert summary.workflow is workflow
    assert summary.reasoning_summary.workflow is workflow
    assert summary.reasoning_summary.cycle_history is history


def test_notes_do_not_become_diagnostic_content():
    workflow = build_workflow()

    notes = build_notes(workflow)

    summary = TechnicianCaseSummary(workflow)

    assert len(notes.notes) == 2
    assert len(summary.findings) == 0
    assert len(summary.root_causes) == 0
    assert len(summary.recommendations) == 0


def test_diagnostic_content_does_not_become_notes():
    workflow = build_workflow()

    populate_diagnostic_content(workflow)

    notes = TechnicianCaseNotes(workflow)
    summary = TechnicianCaseSummary(workflow)

    assert len(summary.findings) == 1
    assert len(summary.root_causes) == 1
    assert len(summary.recommendations) == 1
    assert notes.notes == []


def test_notes_and_diagnostic_content_survive_repeated_summary_creation():
    workflow = build_workflow()

    populate_diagnostic_content(workflow)
    notes = build_notes(workflow)

    for _ in range(5):
        summary = TechnicianCaseSummary(workflow)

        assert len(summary.findings) == 1
        assert len(summary.root_causes) == 1
        assert len(summary.recommendations) == 1
        assert len(notes.notes) == 2


def test_diagnostic_updates_are_visible_without_mutating_existing_notes():
    workflow = build_workflow()

    notes = build_notes(workflow)

    populate_diagnostic_content(workflow)

    first_summary = TechnicianCaseSummary(workflow)

    assert len(first_summary.findings) == 1
    assert len(first_summary.root_causes) == 1
    assert len(first_summary.recommendations) == 1
    assert len(notes.notes) == 2

    workflow.case.findings.append(build_second_finding())

    second_summary = TechnicianCaseSummary(workflow)

    assert len(second_summary.findings) == 2
    assert len(second_summary.root_causes) == 1
    assert len(second_summary.recommendations) == 1
    assert len(notes.notes) == 2