from engine.remediation_verifier import RemediationVerifier


def test_verifier_can_be_created():
    verifier = RemediationVerifier()

    assert verifier is not None


def test_verification_succeeds_when_expected_condition_is_met():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected=True,
        observed=True,
    )

    assert result["verified"] is True


def test_verification_fails_when_expected_condition_is_not_met():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected=True,
        observed=False,
    )

    assert result["verified"] is False

def test_verification_result_contains_expected_condition():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected=True,
        observed=True,
    )

    assert result["expected"] is True


def test_verification_result_contains_observed_condition():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected=True,
        observed=False,
    )

    assert result["observed"] is False

def test_verification_result_contains_action_id():
    verifier = RemediationVerifier()

    result = verifier.verify(
        action_id="memory_review",
        expected=True,
        observed=True,
    )

    assert result["action_id"] == "memory_review"


def test_verification_preserves_action_id_when_verification_fails():
    verifier = RemediationVerifier()

    result = verifier.verify(
        action_id="memory_review",
        expected=True,
        observed=False,
    )

    assert result["action_id"] == "memory_review"

def test_verification_result_contains_success_reason():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected=True,
        observed=True,
    )

    assert result["reason"] == (
        "Observed condition matches expected condition."
    )


def test_verification_result_contains_failure_reason():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected=True,
        observed=False,
    )

    assert result["reason"] == (
        "Observed condition does not match expected condition."
    )

def test_verification_can_compare_non_boolean_values():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="DNS_OK",
        observed="DNS_OK",
    )

    assert result["verified"] is True
    assert result["expected"] == "DNS_OK"
    assert result["observed"] == "DNS_OK"


def test_verification_detects_different_non_boolean_values():
    verifier = RemediationVerifier()

    result = verifier.verify(
        expected="DNS_OK",
        observed="DNS_FAILED",
    )

    assert result["verified"] is False
    assert result["expected"] == "DNS_OK"
    assert result["observed"] == "DNS_FAILED"