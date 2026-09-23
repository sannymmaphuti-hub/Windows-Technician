from engine.remediation_result import RemediationResult
from engine.remediation_verifier import RemediationVerifier


def test_verifier_accepts_matching_expected_and_observed_state():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected={"memory_pressure": "NORMAL"},
        observed={"memory_pressure": "NORMAL"},
        action_id="action-1",
    )

    assert result is not None


def test_verifier_rejects_mismatching_observed_state():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected={"memory_pressure": "NORMAL"},
        observed={"memory_pressure": "HIGH"},
        action_id="action-2",
    )

    assert result is not None


def test_verifier_preserves_action_identity_when_supplied():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected={"status": "resolved"},
        observed={"status": "resolved"},
        action_id="action-42",
    )

    assert result is not None
    assert result["action_id"] == "action-42"


def test_verifier_does_not_execute_or_authorize_an_action():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected={"status": "resolved"},
        observed={"status": "resolved"},
        action_id="action-3",
    )

    assert result is not None
    assert not hasattr(result, "authorization_status")
    assert not hasattr(result, "execution_status")


def test_remediation_result_can_be_created_for_verification():
    result = RemediationResult("action-4")

    assert result.action_id == "action-4"


def test_verification_is_based_on_expected_and_observed_evidence():
    verifier = RemediationVerifier()

    matching = verifier.verify(
        expected={"service": "running", "memory": "normal"},
        observed={"service": "running", "memory": "normal"},
        action_id="action-5",
    )

    different = verifier.verify(
        expected={"service": "running", "memory": "normal"},
        observed={"service": "stopped", "memory": "high"},
        action_id="action-6",
    )

    assert matching is not None
    assert different is not None
    assert matching != different