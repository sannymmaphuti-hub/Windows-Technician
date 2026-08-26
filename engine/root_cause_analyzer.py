# ==========================================
# WINDOWS TECHNICIAN v0.2
# ROOT CAUSE ANALYZER
# ==========================================

from engine.root_cause import RootCauseCandidate


class RootCauseAnalyzer:

    def __init__(self):

        self.candidates = []

    def clear(self):

        self.candidates.clear()

    def add_candidate(
        self,
        cause,
        category,
        confidence,
        evidence=None,
        reason=""
    ):

        candidate = RootCauseCandidate(
            cause=cause,
            category=category,
            confidence=confidence,
            evidence=evidence,
            reason=reason
        )

        self.candidates.append(candidate)

        return candidate

    def analyze(
        self,
        findings=None,
        correlations=None
    ):

        self.clear()

        findings = findings or []
        correlations = correlations or []

        self._analyze_memory_cpu_relationship(
            findings,
            correlations
        )

        return self.get_candidates()

    def _analyze_memory_cpu_relationship(
        self,
        findings,
        correlations
    ):

        memory_pressure = False
        memory_evidence = []

        cpu_behavior = False
        cpu_evidence = []

        correlation_found = False
        correlation_evidence = []

        # ==========================================
        # FIND MEMORY PRESSURE
        # ==========================================

        for finding in findings:

            category = finding.get(
                "category",
                ""
            )

            severity = finding.get(
                "severity",
                ""
            )

            message = finding.get(
                "message",
                ""
            )

            if (
                category == "MEMORY"
                and severity in (
                    "WARNING",
                    "CRITICAL"
                )
            ):

                memory_pressure = True

                memory_evidence.append(
                    message
                )

        # ==========================================
        # FIND CPU BEHAVIOR
        # ==========================================

        for finding in findings:

            category = finding.get(
                "category",
                ""
            )

            if category == "PROCESS CPU BEHAVIOR":

                classification = finding.get(
                    "classification",
                    ""
                )

                if classification == "CPU SPIKE":

                    cpu_behavior = True

                    cpu_evidence.append(
                        finding.get(
                            "message",
                            ""
                        )
                    )

        # ==========================================
        # FIND CORRELATION
        # ==========================================

        for correlation in correlations:

            relationship = correlation.get(
                "relationship",
                ""
            )

            if relationship == (
                "MEMORY PRESSURE + CPU SPIKE"
            ):

                correlation_found = True

                correlation_evidence.append(
                    correlation.get(
                        "message",
                        ""
                    )
                )

        # ==========================================
        # ROOT CAUSE CANDIDATE
        # ==========================================

        if (
            memory_pressure
            and cpu_behavior
            and correlation_found
        ):

            evidence = (
                memory_evidence
                + cpu_evidence
                + correlation_evidence
            )

            self.add_candidate(

                cause=(
                    "Memory pressure may be "
                    "contributing to CPU activity "
                    "and overall system performance "
                    "degradation."
                ),

                category="MEMORY",

                confidence=0.80,

                evidence=evidence,

                reason=(
                    "High memory pressure was detected "
                    "alongside CPU activity from a "
                    "memory-related Windows process, "
                    "and the diagnostic correlation "
                    "engine identified a relationship "
                    "between the two observations."
                )
            )

    def get_candidates(self):

        return [
            candidate.to_dict()
            for candidate in self.candidates
        ]

    def get_primary_candidate(self):

        if not self.candidates:

            return None

        return max(
            self.candidates,
            key=lambda candidate:
                candidate.confidence
        ).to_dict()