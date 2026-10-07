from copy import deepcopy


class DiagnosticCardModel:
    """
    Read-only presentation model for one diagnostic finding.

    This model translates an existing finding into a stable UI
    representation. It does not diagnose, reason, recommend,
    authorize, remediate, or execute.
    """

    SEVERITIES = {
        "INFO",
        "LOW",
        "MEDIUM",
        "HIGH",
        "CRITICAL",
        "WARNING",
        "NORMAL",
        "UNKNOWN",
    }

    def __init__(self, finding):
        if not isinstance(finding, dict):
            raise ValueError("finding must be a dictionary.")

        self._finding = deepcopy(finding)

    @staticmethod
    def _first_value(data, *keys, default=None):
        for key in keys:
            value = data.get(key)
            if value is not None and value != "":
                return value
        return default

    def severity(self):
        value = self._first_value(
            self._finding,
            "severity",
            "level",
            "priority",
            default="UNKNOWN",
        )

        return str(value).upper()

    def title(self):
        return str(
            self._first_value(
                self._finding,
                "title",
                "name",
                "summary",
                "message",
                default="Diagnostic finding",
            )
        )

    def explanation(self):
        return str(
            self._first_value(
                self._finding,
                "explanation",
                "description",
                "details",
                "message",
                default="No explanation available.",
            )
        )

    def evidence(self):
        value = self._first_value(
            self._finding,
            "evidence",
            "observations",
            "data",
            default=[],
        )

        if isinstance(value, list):
            return deepcopy(value)

        if value is None:
            return []

        return [deepcopy(value)]

    def next_step(self):
        value = self._first_value(
            self._finding,
            "next_step",
            "recommended_action",
            "recommendation",
            "action",
            default="Review this finding.",
        )

        return str(value)

    def category(self):
        value = self._first_value(
            self._finding,
            "category",
            "domain",
            "type",
            default="SYSTEM",
        )

        return str(value)

    def identifier(self):
        value = self._first_value(
            self._finding,
            "finding_id",
            "id",
            "uuid",
            default=None,
        )

        return None if value is None else str(value)

    def to_dict(self):
        return {
            "finding_id": self.identifier(),
            "severity": self.severity(),
            "category": self.category(),
            "title": self.title(),
            "explanation": self.explanation(),
            "evidence": self.evidence(),
            "next_step": self.next_step(),
        }
