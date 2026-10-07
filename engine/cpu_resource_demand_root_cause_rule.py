from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_rule import RootCauseRule


class CpuResourceDemandRootCauseRule(RootCauseRule):

    def matches(self, findings):
        return any(
            finding.finding_type == "CPU_PRESSURE"
            for finding in findings
        )

    def create_candidate(self, findings):
        return RootCauseCandidate(
            cause_type="CPU_RESOURCE_DEMAND",
            category="CPU",
            explanation=(
                "High CPU pressure may reflect unusually high "
                "resource demand on the system. Further evidence "
                "is required to identify the underlying source."
            ),
        )