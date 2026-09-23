from engine.finding import Finding


class LegacyFindingAdapter:

    FINDING_TYPE_MAP = {
        "CPU": "CPU_PRESSURE",
        "MEMORY": "MEMORY_PRESSURE",
    }

    def convert(self, legacy_finding):

        category = legacy_finding["category"]

        finding_type = self.FINDING_TYPE_MAP.get(category)

        if finding_type is None:
            return None

        return Finding(
            finding_type=finding_type,
            category=category,
            severity=self._convert_severity(
                legacy_finding["severity"]
            ),
            description=legacy_finding["message"],
            supporting_signals=[],
        )

    @staticmethod
    def _convert_severity(severity):

        severity_map = {
            "INFO": "LOW",
            "WARNING": "MEDIUM",
            "CRITICAL": "HIGH",
            "NORMAL": "LOW",
        }

        if severity not in severity_map:
            raise ValueError(
                f"Unsupported legacy severity: {severity}"
            )

        return severity_map[severity]
