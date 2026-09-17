import copy
from engine.confidence import ConfidenceCalculator
from engine.legacy_finding_adapter import LegacyFindingAdapter


class DiagnosticEngine:

    VALID_SEVERITIES = {
        "INFO",
        "WARNING",
        "CRITICAL"
    }

    def __init__(
        self,
        recommendation_engine=None,
        correlation_engine=None,
        root_cause_reasoning=None,
        explanation_engine=None,
    ):

        self.findings = []
        self.rules = []

        self.recommendation_engine = recommendation_engine
        self.correlation_engine = correlation_engine
        self.root_cause_reasoning = root_cause_reasoning

        self.confidence_calculator = ConfidenceCalculator()
        self.legacy_finding_adapter = LegacyFindingAdapter()

        if explanation_engine is None:
            explanation_engine = None

        self.explanation_engine = explanation_engine

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

            correlation_findings = [
                self.legacy_finding_adapter.convert(finding)
                for finding in self.findings
            ]

            correlations = self.correlation_engine.detect(
                correlation_findings
            )

        if additional_findings:

            for finding in additional_findings:
                self.add_finding(finding)

        root_cause_reasoning = None

        if self.root_cause_reasoning is not None:

            reasoning_findings = [
                self.legacy_finding_adapter.convert(finding)
                for finding in self.findings
            ]

            root_cause_reasoning = (
                self.root_cause_reasoning.analyze(
                    reasoning_findings
                )
            )

        explanations = []

        if self.explanation_engine is not None:

            for finding in self.findings:

                finding_explanations = (
                    self.explanation_engine.evaluate(
                        self.legacy_finding_adapter.convert(finding),
                        [],
                    )
                )

                explanations.extend(finding_explanations)

        recommendations = []

        if self.recommendation_engine is not None:

            recommendations = (
                self.recommendation_engine
                .get_recommendations(self.findings)
            )
        result = {
            "evidence": copy.deepcopy(evidence),
            "status": self.get_overall_status(),
            "total_findings": len(self.findings),
            "findings": copy.deepcopy(self.findings),
            "correlations": copy.deepcopy(correlations),
            "root_causes": copy.deepcopy(root_causes),
            "recommendations": copy.deepcopy(recommendations)
        }

        if self.explanation_engine is not None:
            result["explanations"] = copy.deepcopy(
                explanations
            )

        if root_cause_reasoning is not None:
            result["root_cause_reasoning"] = (
                copy.deepcopy(root_cause_reasoning)
            )

        if self.explanation_engine is not None:
            explanations = []

            for finding in self.findings:
                finding_object = (
                    self.legacy_finding_adapter.convert(finding)
                )

                finding_explanations = (
                    self.explanation_engine.evaluate(
                        finding_object,
                        [],
                    )
                )

                explanations.extend(finding_explanations)

            result["explanations"] = explanations

        return result

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
