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

        return {
            "action_id": action_id,
            "verified": verified,
            "expected": expected,
            "observed": observed,
            "reason": reason,
        }
