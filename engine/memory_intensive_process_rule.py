from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_rule import RootCauseRule


class MemoryIntensiveProcessRule(RootCauseRule):

    def matches(self, findings):
        return any(
            finding.finding_type == "MEMORY_PRESSURE"
            for finding in findings
        )

    def create_candidate(self, findings):
        return RootCauseCandidate(
            cause_type="MEMORY_INTENSIVE_PROCESS",
            category="MEMORY",
            explanation=(
                "A memory-intensive process may be contributing "
                "to the observed memory pressure. This is a possible "
                "cause and requires further evidence."
            ),
        )
