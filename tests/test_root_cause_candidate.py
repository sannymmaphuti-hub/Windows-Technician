from engine.root_cause_candidate import RootCauseCandidate


def test_root_cause_candidate_can_be_created():

    candidate = RootCauseCandidate(
        cause_type="MEMORY_INTENSIVE_PROCESS",
        category="MEMORY",
        explanation="A process may be consuming an unusually large amount of memory.",
    )

    assert candidate.cause_type == "MEMORY_INTENSIVE_PROCESS"
    assert candidate.category == "MEMORY"
    assert (
        candidate.explanation
        == "A process may be consuming an unusually large amount of memory."
    )


def test_root_cause_candidate_requires_cause_type():

    try:
        RootCauseCandidate(
            cause_type="",
            category="MEMORY",
            explanation="A possible cause.",
        )
        assert False
    except ValueError:
        assert True


def test_root_cause_candidate_requires_category():

    try:
        RootCauseCandidate(
            cause_type="MEMORY_INTENSIVE_PROCESS",
            category="",
            explanation="A possible cause.",
        )
        assert False
    except ValueError:
        assert True


def test_root_cause_candidate_requires_explanation():

    try:
        RootCauseCandidate(
            cause_type="MEMORY_INTENSIVE_PROCESS",
            category="MEMORY",
            explanation="",
        )
        assert False
    except ValueError:
        assert True


def test_root_cause_candidate_rejects_invalid_cause_type():

    try:
        RootCauseCandidate(
            cause_type=None,
            category="MEMORY",
            explanation="A possible cause.",
        )
        assert False
    except ValueError:
        assert True


def test_root_cause_candidate_rejects_invalid_category():

    try:
        RootCauseCandidate(
            cause_type="MEMORY_INTENSIVE_PROCESS",
            category=None,
            explanation="A possible cause.",
        )
        assert False
    except ValueError:
        assert True


def test_root_cause_candidate_rejects_invalid_explanation():

    try:
        RootCauseCandidate(
            cause_type="MEMORY_INTENSIVE_PROCESS",
            category="MEMORY",
            explanation=None,
        )
        assert False
    except ValueError:
        assert True


def test_root_cause_candidate_can_export_evidence():

    candidate = RootCauseCandidate(
        cause_type="MEMORY_INTENSIVE_PROCESS",
        category="MEMORY",
        explanation="A process may be consuming an unusually large amount of memory.",
    )

    evidence = candidate.to_evidence()

    assert evidence == {
        "cause_type": "MEMORY_INTENSIVE_PROCESS",
        "category": "MEMORY",
        "explanation": (
            "A process may be consuming an unusually large amount of memory."
        ),
    }


def test_root_cause_candidate_does_not_claim_selection():

    candidate = RootCauseCandidate(
        cause_type="MEMORY_INTENSIVE_PROCESS",
        category="MEMORY",
        explanation="A process may be consuming an unusually large amount of memory.",
    )

    assert not hasattr(candidate, "is_primary")
    assert not hasattr(candidate, "selected")
