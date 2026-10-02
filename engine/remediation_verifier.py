from engine.remediation_result import RemediationResult


class RemediationVerifier:

    def verify(self, expected, observed, action_id=None):
        verified = expected == observed

        if verified:
            reason = (
                "Observed condition matches expected condition."
            )
        else:
            reason = (
                "Observed condition does not match expected condition."
            )

        result = RemediationResult(action_id)

        result.reason = reason
        result.verification_result = {
            "action_id": action_id,
            "verified": verified,
            "expected": expected,
            "observed": observed,
        }

        return result