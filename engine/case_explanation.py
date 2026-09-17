from engine.confidence import Confidence
from engine.explanation import Explanation
from engine.network_diagnostic_case_synthesis import (
    NetworkDiagnosticCase,
)


class CaseExplanation:

    VALID_AUDIENCES = {
        "USER",
        "TECHNICIAN",
    }

    def is_supported_audience(self, audience):
        return audience in self.VALID_AUDIENCES

    def explain(self, case, audience):
        self._validate_case(case)
        self._validate_audience(audience)

        if audience == "USER":
            return self._create_user_explanation(case)

        return self._create_technician_explanation(case)

    @staticmethod
    def _validate_case(case):
        if not isinstance(
            case,
            NetworkDiagnosticCase,
        ):
            raise ValueError(
                "Case explanation subject must be "
                "a NetworkDiagnosticCase."
            )

    def _validate_audience(self, audience):
        if not self.is_supported_audience(audience):
            raise ValueError(
                "Unsupported explanation audience."
            )

    @staticmethod
    def _get_confidence_level(case):
        if not case.confidences:
            return None

        confidence = case.confidences[0]

        if isinstance(confidence, Confidence):
            return confidence.level

        return None

    @classmethod
    def _create_user_explanation(cls, case):
        primary_cause = case.primary_cause
        confidence = cls._get_confidence_level(case)

        if primary_cause is not None:
            cause_type = getattr(
                primary_cause,
                "cause_type",
                None,
            )

            if cause_type:
                cause_text = cls._format_cause(
                    cause_type
                )

                return Explanation(
                    subject="DIAGNOSTIC_CASE",
                    summary=(
                        f"The diagnostic results point to "
                        f"{cause_text}."
                    ),
                    details=(
                        cls._user_details(
                            case,
                            cause_text,
                        )
                    ),
                    confidence=confidence,
                )

        recommendation_text = (
            cls._get_recommendation_text(case)
        )

        if recommendation_text:
            return Explanation(
                subject="DIAGNOSTIC_CASE",
                summary=(
                    "The diagnostic results identified "
                    "something that should be checked."
                ),
                details=recommendation_text,
                confidence=confidence,
            )

        return Explanation(
            subject="DIAGNOSTIC_CASE",
            summary=(
                "Your computer has been checked for "
                "possible problems."
            ),
            details=(
                "The diagnostic results can be reviewed "
                "to understand what may be affecting "
                "your computer and what to do next."
            ),
            confidence=confidence,
        )

    @classmethod
    def _create_technician_explanation(cls, case):
        primary_cause = case.primary_cause
        confidence = cls._get_confidence_level(case)

        cause_text = "none identified"

        if primary_cause is not None:
            cause_type = getattr(
                primary_cause,
                "cause_type",
                None,
            )

            if cause_type:
                cause_text = cause_type

        recommendation_text = (
            cls._get_recommendation_text(case)
        )

        details = (
            "Primary cause: "
            f"{cause_text}. "
            "Review the observations, signals, "
            "findings, correlations, root-cause "
            "candidates, evaluations, confidence "
            "results, and recommendations."
        )

        if recommendation_text:
            details += (
                " Recommendations: "
                f"{recommendation_text}"
            )

        return Explanation(
            subject="DIAGNOSTIC_CASE",
            summary=(
                "Diagnostic case contains the assembled "
                "technical reasoning chain."
            ),
            details=details,
            confidence=confidence,
        )

    @staticmethod
    def _format_cause(cause_type):
        words = cause_type.lower().split("_")

        return " ".join(words)

    @staticmethod
    def _user_details(case, cause_text):
        recommendation_text = (
            CaseExplanation._get_recommendation_text(
                case
            )
        )

        if recommendation_text:
            return (
                f"This may be related to {cause_text}. "
                f"{recommendation_text}"
            )

        return (
            f"This may be related to {cause_text}. "
            "The diagnostic result may need further "
            "investigation before the problem can be "
            "confirmed."
        )

    @staticmethod
    def _get_recommendation_text(case):
        if not case.recommendations:
            return None

        texts = []

        for recommendation in case.recommendations:
            text = (
                CaseExplanation._get_single_recommendation_text(
                    recommendation
                )
            )

            if text:
                texts.append(text)

        if not texts:
            return None

        return " ".join(texts)

    @staticmethod
    def _get_single_recommendation_text(
        recommendation,
    ):
        if isinstance(recommendation, dict):
            description = recommendation.get(
                "description"
            )

            if isinstance(description, str):
                return description

            recommendation_type = recommendation.get(
                "recommendation_type"
            )

            if isinstance(
                recommendation_type,
                str,
            ):
                return (
                    "Recommended action: "
                    f"{recommendation_type}."
                )

        description = getattr(
            recommendation,
            "description",
            None,
        )

        if isinstance(description, str):
            return description

        recommendation_type = getattr(
            recommendation,
            "recommendation_type",
            None,
        )

        if isinstance(
            recommendation_type,
            str,
        ):
            return (
                "Recommended action: "
                f"{recommendation_type}."
            )

        return None