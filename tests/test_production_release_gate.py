import pytest

from packaging.production_release_gate import (
    ProductionReleaseDecision,
    ProductionReleaseEvidence,
    evaluate_production_release,
)


def test_production_release_approves_only_when_all_requirements_pass():
    evidence = ProductionReleaseEvidence(
        trusted_signature_verified=True,
        clean_windows_installation_verified=True,
        explicit_release_approval=True,
    )

    decision = evaluate_production_release(evidence)

    assert decision.approved is True
    assert decision.blockers == ()


@pytest.mark.parametrize(
    ("field", "expected_blocker"),
    [
        ("trusted_signature_verified", "Trusted code-signature verification"),
        ("clean_windows_installation_verified", "Clean-Windows installation validation"),
        ("explicit_release_approval", "Explicit final production-release approval"),
    ],
)
def test_each_missing_production_requirement_blocks_release(field, expected_blocker):
    values = {
        "trusted_signature_verified": True,
        "clean_windows_installation_verified": True,
        "explicit_release_approval": True,
    }
    values[field] = False

    decision = evaluate_production_release(ProductionReleaseEvidence(**values))

    assert decision.approved is False
    assert any(expected_blocker in blocker for blocker in decision.blockers)


def test_current_unsigned_unvalidated_unapproved_candidate_is_blocked():
    evidence = ProductionReleaseEvidence(
        trusted_signature_verified=False,
        clean_windows_installation_verified=False,
        explicit_release_approval=False,
    )

    decision = evaluate_production_release(evidence)

    assert decision.approved is False
    assert len(decision.blockers) == 3


def test_all_eight_gate_combinations_follow_conjunction():
    for signature in (False, True):
        for installation in (False, True):
            for approval in (False, True):
                decision = evaluate_production_release(
                    ProductionReleaseEvidence(signature, installation, approval)
                )
                assert decision.approved is (signature and installation and approval)
                assert bool(decision.blockers) is not decision.approved


@pytest.mark.parametrize(
    "values",
    [
        (1, True, True),
        (True, "yes", True),
        (True, True, None),
    ],
)
def test_evidence_rejects_non_boolean_values(values):
    with pytest.raises(TypeError):
        ProductionReleaseEvidence(*values)


def test_evaluator_rejects_wrong_evidence_type():
    with pytest.raises(TypeError):
        evaluate_production_release(None)


def test_decision_rejects_inconsistent_approval_state():
    with pytest.raises(ValueError):
        ProductionReleaseDecision(approved=True, blockers=("still blocked",))
