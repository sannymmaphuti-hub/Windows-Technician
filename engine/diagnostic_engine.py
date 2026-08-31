# ==========================================
# Windows Technician v0.3
# DIAGNOSTIC ENGINE
# ==========================================

import copy

from engine.confidence import ConfidenceCalculator

class DiagnosticEngine:

    VALID_SEVERITIES = {
        "INFO",
        "WARNING",
        "CRITICAL"
    }

    def __init__(
        self,
        recommendation_engine=None,
        correlation_engine=None
    ):

        self.findings = []
        self.rules = []

        self.recommendation_engine = recommendation_engine
        self.correlation_engine = correlation_engine

        self.confidence_calculator = ConfidenceCalculator()

    def _validate_finding(self, finding):

        if not isinstance(finding, dict):
            raise ValueError("Finding must be a dictionary.")

        required_fields = [
            "category",
            "severity",
            "message"
        ]

        for field in required_fields:

            if field not in finding:
                raise ValueError(
                    f"Finding is missing required field: {field}"
                )

        if not isinstance(finding["category"], str):
            raise ValueError(
                "Finding category must be a string."
            )

        valid_severities = {
            "INFO",
            "WARNING",
            "CRITICAL",
            "NORMAL"
        }

        if finding["severity"] not in valid_severities:
            raise ValueError(
                f"Invalid severity: {finding['severity']}"
            )

        if not isinstance(finding["message"], str):
            raise ValueError(
                "Finding message must be a string."
            )

        confidence = finding.get("confidence")

        if confidence is not None:

            if not isinstance(confidence, (int, float)):
                raise ValueError(
                    "Finding confidence must be numeric."
                )

            if not 0.0 <= confidence <= 1.0:
                raise ValueError(
                    "Finding confidence must be between 0.0 and 1.0."
                )

        return True

    def add_finding(self, finding):

        self._validate_finding(finding)

        finding = self._add_confidence_level(finding)

        self.findings.append(finding)

    def add_rule(self, rule):

        if not hasattr(rule, "evaluate"):
            raise ValueError("Invalid diagnostic rule.")

        self.rules.append(rule)

    def run_rules(self, evidence):

        for rule in self.rules:

            rule_evidence = evidence.get(
                rule.category,
                {}
            )

            findings = rule.evaluate(
                rule_evidence
            )

            if findings is None:
                continue

            if isinstance(findings, list):

                for finding in findings:
                    self.add_finding(finding)

            else:

                self.add_finding(findings)

        return self.get_findings()

    def analyze(
        self,
        evidence,
        additional_findings=None,
        correlations=None,
        root_causes=None
    ):

        return self.diagnose(
            evidence,
            additional_findings=additional_findings,
            correlations=correlations,
            root_causes=root_causes
        )

    def diagnose(
        self,
        evidence,
        additional_findings=None,
        correlations=None,
        root_causes=None
    ):

        self.clear_findings()

        if correlations is None:
            correlations = []

        if root_causes is None:
            root_causes = []

        self.run_rules(evidence)

        if self.correlation_engine is not None:
            correlations = self.correlation_engine.analyze(
                evidence
            )

        if additional_findings:

            for finding in additional_findings:
                self.add_finding(finding)

        recommendations = []

        if self.recommendation_engine is not None:

            recommendations = (
                self.recommendation_engine
                .get_recommendations(self.findings)
            )

        return {
            "evidence": copy.deepcopy(evidence),
            "status": self.get_overall_status(),
            "total_findings": len(self.findings),
            "findings": copy.deepcopy(self.findings),
            "correlations": copy.deepcopy(correlations),
            "root_causes": copy.deepcopy(root_causes),
            "recommendations": copy.deepcopy(recommendations)
        }
    def get_findings(self):

        return self.findings

    def clear_findings(self):

        self.findings.clear()

    def get_summary(self):

        return {
            "total_findings": len(self.findings),
            "findings": self.findings
        }

    def get_overall_status(self):

        if not self.findings:
            return "NORMAL"

        severity_priority = {
            "INFO": 1,
            "WARNING": 2,
            "CRITICAL": 3
        }

        highest_severity = "INFO"
        highest_priority = 0

        for finding in self.findings:

            severity = finding.get(
                "severity",
                "INFO"
            )

            priority = severity_priority.get(
                severity,
                1
            )

            if priority > highest_priority:

                highest_priority = priority
                highest_severity = severity

        return highest_severity

    def _add_confidence_level(self, finding):

        confidence = finding.get("confidence")

        if confidence is None:
            return finding

        finding["confidence_level"] = (
            self.confidence_calculator.classify(confidence)
        )

        return finding
