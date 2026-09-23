class Signal:

    VALID_STRENGTHS = {"LOW", "MEDIUM", "HIGH"}
    VALID_QUALITIES = {"LOW", "MEDIUM", "HIGH"}

    def __init__(
        self,
        signal_type,
        source,
        subject,
        attribute,
        value,
        strength=None,
        quality=None,
    ):
        self._validate_text(signal_type, "signal_type")
        self._validate_text(source, "source")
        self._validate_text(subject, "subject")
        self._validate_text(attribute, "attribute")

        if strength is not None and strength not in self.VALID_STRENGTHS:
            raise ValueError(
                "Signal strength must be LOW, MEDIUM, or HIGH."
            )

        if quality is not None and quality not in self.VALID_QUALITIES:
            raise ValueError(
                "Signal quality must be LOW, MEDIUM, or HIGH."
            )

        self.signal_type = signal_type
        self.source = source
        self.subject = subject
        self.attribute = attribute
        self.value = value
        self.strength = strength
        self.quality = quality

    def to_evidence(self):
        evidence = {
            "signal_type": self.signal_type,
            "source": self.source,
            "subject": self.subject,
            "attribute": self.attribute,
            "value": self.value,
        }

        if self.strength is not None:
            evidence["strength"] = self.strength

        if self.quality is not None:
            evidence["quality"] = self.quality

        return evidence

    @staticmethod
    def _validate_text(value, field_name):
        if not isinstance(value, str):
            raise ValueError(f"Signal {field_name} must be a string.")

        if not value.strip():
            raise ValueError(f"Signal {field_name} cannot be empty.")
