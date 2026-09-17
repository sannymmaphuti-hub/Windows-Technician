from engine.explanation import Explanation
from engine.explanation_rule import ExplanationRule
from engine.root_cause_candidate import RootCauseCandidate


class AudienceExplanationRule(ExplanationRule):

    VALID_AUDIENCES = {
        "USER",
        "TECHNICIAN",
    }

    def matches(self, subject, evidence):
        if not isinstance(subject, RootCauseCandidate):
            raise ValueError(
                "Audience explanation subject must be "
                "a RootCauseCandidate."
            )

        return True

    def create_explanation(
        self,
        subject,
        evidence,
        audience,
    ):
        if not isinstance(subject, RootCauseCandidate):
            raise ValueError(
                "Audience explanation subject must be "
                "a RootCauseCandidate."
            )

        if not self.is_supported_audience(audience):
            raise ValueError(
                "Unsupported explanation audience."
            )

        if audience == "USER":
            return self._create_user_explanation(subject)

        return self._create_technician_explanation(subject)

    def is_supported_audience(self, audience):
        return audience in self.VALID_AUDIENCES

    @staticmethod
    def _create_user_explanation(subject):
        return Explanation(
            subject=subject.cause_type,
            summary=(
                "Your computer may have a program "
                "using a lot of memory."
            ),
            details=(
                "This can leave less memory available for "
                "Windows and other programs, which may make "
                "the computer feel slow. More investigation "
                "may be needed to confirm the cause."
            ),
        )

    @staticmethod
    def _create_technician_explanation(subject):
        return Explanation(
            subject=subject.cause_type,
            summary=(
                "A memory-intensive process may be "
                "contributing to memory pressure."
            ),
            details=(
                "Evidence should be reviewed to identify "
                "the process responsible for elevated memory "
                "utilization and determine whether the "
                "condition is persistent or transient."
            ),
        )