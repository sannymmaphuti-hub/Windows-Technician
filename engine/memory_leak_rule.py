from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_rule import RootCauseRule


class MemoryLeakRule(RootCauseRule):

    def matches(self, findings):
        return any(
            finding.finding_type == "MEMORY_PRESSURE"
            for finding in findings
        )

    def create_candidate(self, findings):
        return RootCauseCandidate(
            cause_type="MEMORY_LEAK",
            category="MEMORY",
            explanation=(
                "A memory leak may be contributing to the "
                "observed memory pressure. Further evidence "
                "is required to determine whether this is involved."
            ),
        )