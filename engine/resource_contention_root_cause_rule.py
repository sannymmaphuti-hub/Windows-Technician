from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_rule import RootCauseRule


class ResourceContentionRootCauseRule(RootCauseRule):

    def matches(self, findings):
        finding_types = {
            finding.finding_type
            for finding in findings
        }

        return (
            "CPU_PRESSURE" in finding_types
            and "MEMORY_PRESSURE" in finding_types
        )

    def create_candidate(self, findings):
        return RootCauseCandidate(
            cause_type="RESOURCE_CONTENTION",
            category="SYSTEM",
            explanation=(
                "Concurrent CPU and memory pressure may indicate "
                "competing resource demand on the system. Further "
                "evidence is required to determine whether resource "
                "contention is the primary underlying cause."
            ),
        )