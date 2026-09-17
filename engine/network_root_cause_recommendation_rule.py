from engine.recommendation import Recommendation
from engine.recommendation_rule import RecommendationRule
from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation


class NetworkRootCauseRecommendationRule(RecommendationRule):

    SUPPORTED_CAUSES = {
        "DNS_FAILURE",
        "LOCAL_NETWORK_FAILURE",
        "NETWORK_ADAPTER_FAILURE",
    }

    def matches(self, subject, evidence):
        self._validate_subject(subject)
        self._validate_evidence(evidence)

        for item in evidence:
            if not isinstance(item, RootCauseEvaluation):
                continue

            if item.candidate is not subject:
                continue

            if (
                subject.cause_type in self.SUPPORTED_CAUSES
                and item.assessment in {
                    "SUPPORTED",
                    "STRONGLY_SUPPORTED",
                }
            ):
                return True

        return False

    def create_recommendation(self, subject, evidence):
        self._validate_subject(subject)
        self._validate_evidence(evidence)

        if subject.cause_type not in self.SUPPORTED_CAUSES:
            raise ValueError(
                "Unsupported network root cause."
            )

        evaluation = None

        for item in evidence:
            if not isinstance(item, RootCauseEvaluation):
                continue

            if item.candidate is subject:
                evaluation = item
                break

        if evaluation is None:
            raise ValueError(
                "No root cause evaluation found for candidate."
            )

        if evaluation.assessment not in {
            "SUPPORTED",
            "STRONGLY_SUPPORTED",
        }:
            raise ValueError(
                "Network root cause is not sufficiently supported."
            )

        priority = (
            "HIGH"
            if evaluation.assessment == "STRONGLY_SUPPORTED"
            else "MEDIUM"
        )

        if subject.cause_type == "DNS_FAILURE":
            return Recommendation(
                recommendation_type="REVIEW_DNS_CONFIGURATION",
                category="NETWORK",
                priority=priority,
                description=(
                    "Review the DNS configuration and "
                    "name resolution."
                ),
                rationale=(
                    "Evidence supports DNS failure as a "
                    "possible contributor to the loss of "
                    "Internet connectivity."
                ),
            )

        if subject.cause_type == "LOCAL_NETWORK_FAILURE":
            return Recommendation(
                recommendation_type="REVIEW_LOCAL_NETWORK",
                category="NETWORK",
                priority=priority,
                description=(
                    "Review the local network connection "
                    "and gateway."
                ),
                rationale=(
                    "Evidence supports a local network "
                    "failure as a possible contributor to "
                    "the loss of Internet connectivity."
                ),
            )

        return Recommendation(
            recommendation_type="REVIEW_NETWORK_ADAPTER",
            category="NETWORK",
            priority=priority,
            description=(
                "Review the network adapter and its "
                "connection."
            ),
            rationale=(
                "Evidence supports a network adapter "
                "failure as a possible contributor to "
                "the loss of Internet connectivity."
            ),
        )

    @staticmethod
    def _validate_subject(subject):
        if not isinstance(subject, RootCauseCandidate):
            raise ValueError(
                "Network recommendation subject "
                "must be a RootCauseCandidate."
            )

    @staticmethod
    def _validate_evidence(evidence):
        if not isinstance(evidence, list):
            raise ValueError(
                "Network recommendation evidence "
                "must be a list."
            )