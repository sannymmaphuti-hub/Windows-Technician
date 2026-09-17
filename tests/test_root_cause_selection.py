from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_selection import RootCauseSelection


def create_process_candidate():

    return RootCauseCandidate(
        cause_type="MEMORY_INTENSIVE_PROCESS",
        category="MEMORY",
        explanation=(
            "A memory-intensive process may be contributing "
            "to the observed memory pressure."
        ),
    )


def create_leak_candidate():

    return RootCauseCandidate(
        cause_type="MEMORY_LEAK",
        category="MEMORY",
        explanation=(
            "A memory leak may be contributing to the "
            "observed memory pressure."
        ),
    )


def create_evaluation(
    candidate,
    assessment,
):

    return RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=[],
        assessment=assessment,
        explanation="Evaluation result.",
    )


def test_root_cause_selection_can_be_created():

    selection = RootCauseSelection()

    assert selection is not None


def test_insufficient_evaluation_cannot_be_primary():

    candidate = create_process_candidate()

    evaluation = create_evaluation(
        candidate,
        "INSUFFICIENT",
    )

    selection = RootCauseSelection()

    result = selection.select([evaluation])

    assert result is None


def test_supported_evaluation_can_be_selected_as_primary():

    candidate = create_process_candidate()

    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    selection = RootCauseSelection()

    result = selection.select([evaluation])

    assert result is candidate


def test_strongly_supported_evaluation_can_be_selected_as_primary():

    candidate = create_process_candidate()

    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    selection = RootCauseSelection()

    result = selection.select([evaluation])

    assert result is candidate


def test_insufficient_candidate_does_not_beat_supported_candidate():

    insufficient_candidate = create_leak_candidate()
    supported_candidate = create_process_candidate()

    evaluations = [
        create_evaluation(
            insufficient_candidate,
            "INSUFFICIENT",
        ),
        create_evaluation(
            supported_candidate,
            "SUPPORTED",
        ),
    ]

    selection = RootCauseSelection()

    result = selection.select(evaluations)

    assert result is supported_candidate


def test_strongly_supported_candidate_beats_supported_candidate():

    supported_candidate = create_process_candidate()
    strongly_supported_candidate = create_leak_candidate()

    evaluations = [
        create_evaluation(
            supported_candidate,
            "SUPPORTED",
        ),
        create_evaluation(
            strongly_supported_candidate,
            "STRONGLY_SUPPORTED",
        ),
    ]

    selection = RootCauseSelection()

    result = selection.select(evaluations)

    assert result is strongly_supported_candidate


def test_multiple_supported_candidates_do_not_create_unjustified_winner():

    process_candidate = create_process_candidate()
    leak_candidate = create_leak_candidate()

    evaluations = [
        create_evaluation(
            process_candidate,
            "SUPPORTED",
        ),
        create_evaluation(
            leak_candidate,
            "SUPPORTED",
        ),
    ]

    selection = RootCauseSelection()

    result = selection.select(evaluations)

    assert result is None


def test_multiple_strongly_supported_candidates_do_not_create_unjustified_winner():

    process_candidate = create_process_candidate()
    leak_candidate = create_leak_candidate()

    evaluations = [
        create_evaluation(
            process_candidate,
            "STRONGLY_SUPPORTED",
        ),
        create_evaluation(
            leak_candidate,
            "STRONGLY_SUPPORTED",
        ),
    ]

    selection = RootCauseSelection()

    result = selection.select(evaluations)

    assert result is None


def test_selection_does_not_modify_evaluations():

    candidate = create_process_candidate()

    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    evaluations = [evaluation]

    selection = RootCauseSelection()

    selection.select(evaluations)

    assert evaluations == [evaluation]
    assert evaluation.candidate is candidate
    assert evaluation.assessment == "SUPPORTED"


def test_selection_does_not_modify_candidate():

    candidate = create_process_candidate()

    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    selection = RootCauseSelection()

    selection.select([evaluation])

    assert candidate.cause_type == "MEMORY_INTENSIVE_PROCESS"
    assert candidate.category == "MEMORY"