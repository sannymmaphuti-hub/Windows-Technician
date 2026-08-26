# ==========================================
# WINDOWS TECHNICIAN v0.1
# DIAGNOSTIC EVIDENCE
# ==========================================


class DiagnosticEvidence:

    def __init__(self, data=None):

        if data is None:
            self.data = {}

        else:

            if not isinstance(data, dict):
                raise ValueError(
                    "Evidence data must be a dictionary."
                )

            self.data = {}

            for category, evidence in data.items():

                self._validate_category(category)
                self._validate_evidence(evidence)

                self.data[category] = evidence

    def _validate_category(self, category):

        if not isinstance(category, str):
            raise ValueError(
                "Evidence category must be a string."
            )

        if not category.strip():
            raise ValueError(
                "Evidence category cannot be empty."
            )

    def _validate_evidence(self, evidence):

        if not isinstance(evidence, dict):
            raise ValueError(
                "Evidence payload must be a dictionary."
            )

    def add(self, category, evidence):

        self._validate_category(category)
        self._validate_evidence(evidence)

        self.data[category] = evidence

    def get(self, category):

        return self.data.get(category)

    def has(self, category):

        return category in self.data

    def get_all(self):

        return self.data