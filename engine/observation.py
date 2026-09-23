class Observation:
    def __init__(self, source, subject, attribute, value):
        self._validate_text(source, "source")
        self._validate_text(subject, "subject")
        self._validate_text(attribute, "attribute")

        self.source = source
        self.subject = subject
        self.attribute = attribute
        self.value = value

    def to_evidence(self):
        return {
            "source": self.source,
            "subject": self.subject,
            "attribute": self.attribute,
            "value": self.value
        }

    @staticmethod
    def _validate_text(value, field_name):
        if not isinstance(value, str):
            raise ValueError(f"Observation {field_name} must be a string.")

        if not value.strip():
            raise ValueError(f"Observation {field_name} cannot be empty.")
