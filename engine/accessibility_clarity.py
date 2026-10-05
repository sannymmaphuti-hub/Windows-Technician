class AccessibilityClarity:
    """Provide clear labels for internal authorization and execution states."""

    def authorization_label(self, authorization_status):
        if not isinstance(authorization_status, str):
            raise ValueError(
                "authorization_status must be a string."
            )

        if not authorization_status.strip():
            raise ValueError(
                "authorization_status cannot be empty."
            )

        labels = {
            "UNAUTHORIZED": "Authorization required",
            "AUTHORIZED": "Authorized",
            "DENIED": "Denied",
        }

        return labels.get(
            authorization_status,
            "Unknown authorization state",
        )

    def execution_label(self, execution_status):
        if not isinstance(execution_status, str):
            raise ValueError(
                "execution_status must be a string."
            )

        if not execution_status.strip():
            raise ValueError(
                "execution_status cannot be empty."
            )

        labels = {
            "NOT_EXECUTED": "Not executed",
            "EXECUTED": "Executed",
            "FAILED": "Failed",
        }

        return labels.get(
            execution_status,
            "Unknown execution state",
        )