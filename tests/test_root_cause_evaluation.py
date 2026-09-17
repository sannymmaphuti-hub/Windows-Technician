from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation


def create_candidate():

    return RootCauseCandidate(
        cause_type="MEMORY_LEAK",
        category="MEMORY",
        explanation=(
            "A memory leak may be contributing to "
            "the observed memory pressure."
        ),
    )


def test_root_cause_evaluation_can_be_created():

    candidate = create_candidate()

    evaluation = RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=[],
        assessment="INSUFFICIENT",
        explanation=(
            "Current evidence is insufficient "
            "to establish this cause."
        ),
    )

    assert evaluation is not None


def test_root_cause_evaluation_requires_candidate():

    try:
        RootCauseEvaluation(
            candidate=None,
            supporting_evidence=[],
            assessment="INSUFFICIENT",
            explanation="Evidence is insufficient.",
        )
        assert False
    except ValueError:
        assert True


def test_root_cause_evaluation_preserves_candidate():

    candidate = create_candidate()

    evaluation = RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=[],
        assessment="INSUFFICIENT",
        explanation="Evidence is insufficient.",
    )

    assert evaluation.candidate is candidate


def test_root_cause_evaluation_preserves_supporting_evidence():

    candidate = create_candidate()

    evidence = [
        "MEMORY_PRESSURE",
        "HIGH_MEMORY_USAGE",
    ]

    evaluation = RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=evidence,
        assessment="SUPPORTED",
        explanation=(
            "The observed memory signals support "
            "this possible cause."
        ),
    )

    assert evaluation.supporting_evidence is evidence


def test_root_cause_evaluation_accepts_valid_assessments():

    candidate = create_candidate()

    valid_assessments = [
        "INSUFFICIENT",
        "SUPPORTED",
        "STRONGLY_SUPPORTED",
    ]

    for assessment in valid_assessments:

        evaluation = RootCauseEvaluation(
            candidate=candidate,
            supporting_evidence=[],
            assessment=assessment,
            explanation="Assessment explanation.",
        )

        assert evaluation.assessment == assessment


def test_root_cause_evaluation_rejects_invalid_assessment():

    candidate = create_candidate()

    try:
        RootCauseEvaluation(
            candidate=candidate,
            supporting_evidence=[],
            assessment="DEFINITE",
            explanation="This should fail.",
        )
        assert False
    except ValueError:
        assert True


def test_root_cause_evaluation_requires_explanation():

    candidate = create_candidate()

    try:
        RootCauseEvaluation(
            candidate=candidate,
            supporting_evidence=[],
            assessment="SUPPORTED",
            explanation="",
        )
        assert False
    except ValueError:
        assert True


def test_root_cause_evaluation_exports_evidence():

    candidate = create_candidate()

    evaluation = RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=[
            "MEMORY_PRESSURE",
        ],
        assessment="SUPPORTED",
        explanation=(
            "The observed memory pressure supports "
            "this possible cause."
        ),
    )

    evidence = evaluation.to_evidence()

    assert evidence["candidate"] is candidate
    assert evidence["supporting_evidence"] == [
        "MEMORY_PRESSURE",
    ]
    assert evidence["assessment"] == "SUPPORTED"
    assert (
        evidence["explanation"]
        == evaluation.explanation
    )


def test_root_cause_evaluation_does_not_claim_primary_cause():

    candidate = create_candidate()

    evaluation = RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=[],
        assessment="SUPPORTED",
        explanation="The evidence supports this cause.",
    )

    assert not hasattr(
        evaluation,
        "is_primary",
    )

    assert not hasattr(
        evaluation,
        "selected",
    )


def test_root_cause_evaluation_does_not_contain_confidence():

    candidate = create_candidate()

    evaluation = RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=[],
        assessment="SUPPORTED",
        explanation="The evidence supports this cause.",
    )

    assert not hasattr(
        evaluation,
        "confidence",
    )