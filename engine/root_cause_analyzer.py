
# ==========================================
# Windows Technician v0.6
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
        reason="",
        process=None,
        pid=None
    ):

        candidate = RootCauseCandidate(
            cause=cause,
            category=category,
            confidence=confidence,
            evidence=evidence,
            reason=reason
        )

        result = candidate.to_dict()

        if process is not None:
            result["process"] = process

        if pid is not None:
            result["pid"] = pid

        self.candidates.append(result)

        return result

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

        self._analyze_memory_diagnostic_root_cause(
            findings
        )

        self._analyze_cpu_root_cause(
            findings
        )

        # Preserve the original public API.
        #
        # analyze() returns the list of root-cause
        # candidates so existing callers and tests
        # remain compatible.
        return self.get_candidates()


    # ==========================================
    # v0.6 STRUCTURED ANALYSIS RESULT
    # ==========================================

    def analyze_result(
        self,
        findings=None,
        correlations=None
    ):

        candidates = self.analyze(
            findings=findings,
            correlations=correlations
        )

        return {
            "candidates": candidates,
            "primary": self.get_primary_candidate()
        }
    # ==========================================
    # MEMORY + CPU RELATIONSHIP
    # ==========================================

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

        # ------------------------------------------
        # FIND MEMORY PRESSURE
        # ------------------------------------------

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

        # ------------------------------------------
        # FIND CPU BEHAVIOR
        # ------------------------------------------

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

        # ------------------------------------------
        # FIND CORRELATION
        # ------------------------------------------

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

        # ------------------------------------------
        # ROOT CAUSE CANDIDATE
        # ------------------------------------------

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

    # ==========================================
    # MEMORY DIAGNOSTIC ROOT CAUSE
    # ==========================================

    def _analyze_memory_diagnostic_root_cause(
        self,
        findings
    ):

        for finding in findings:

            category = finding.get(
                "category",
                ""
            )

            severity = finding.get(
                "severity",
                ""
            )

            if category != "MEMORY DIAGNOSTIC":
                continue

            if severity not in (
                "WARNING",
                "CRITICAL"
            ):
                continue

            process = finding.get(
                "process"
            )

            pid = finding.get(
                "pid"
            )

            message = finding.get(
                "message",
                ""
            )

            evidence = []

            if message:
                evidence.append(message)

            if process:

                process_memory = finding.get(
                    "process_memory_mb"
                )

                system_memory = finding.get(
                    "system_memory_percent"
                )

                behavior = finding.get(
                    "behavior"
                )

                trend = finding.get(
                    "trend"
                )

                if process_memory is not None:
                    evidence.append(
                        f"{process} memory usage: "
                        f"{process_memory} MB"
                    )

                if system_memory is not None:
                    evidence.append(
                        f"System memory usage: "
                        f"{system_memory}%"
                    )

                if behavior:
                    evidence.append(
                        f"Process behavior: "
                        f"{behavior}"
                    )

                if trend:
                    evidence.append(
                        f"Memory trend: "
                        f"{trend}"
                    )

                cause = (
                    f"Memory pressure is likely "
                    f"being contributed to by "
                    f"{process}."
                )

                reason = (
                    f"{process} was identified as a "
                    f"significant memory contributor "
                    f"while the system was experiencing "
                    f"{severity.lower()} memory pressure."
                )

                self.add_candidate(
                    cause=cause,
                    category="MEMORY",
                    confidence=0.85,
                    evidence=evidence,
                    reason=reason,
                    process=process,
                    pid=pid
                )

    # ==========================================
    # CPU ROOT CAUSE
    # ==========================================

    def _analyze_cpu_root_cause(
        self,
        findings
    ):

        for finding in findings:

            category = finding.get(
                "category",
                ""
            )

            severity = finding.get(
                "severity",
                ""
            )

            if category != "CPU":
                continue

            if severity not in (
                "WARNING",
                "CRITICAL"
            ):
                continue

            process = finding.get(
                "process"
            )

            pid = finding.get(
                "pid"
            )

            cpu_usage = finding.get(
                "cpu_usage_percent"
            )

            process_cpu = finding.get(
                "process_cpu_percent"
            )

            message = finding.get(
                "message",
                ""
            )

            evidence = []

            if message:
                evidence.append(message)

            if cpu_usage is not None:

                evidence.append(
                    f"System CPU usage: "
                    f"{cpu_usage}%"
                )

            if process_cpu is not None:

                evidence.append(
                    f"Process CPU usage: "
                    f"{process_cpu}%"
                )

            if process:

                cause = (
                    f"CPU pressure is likely "
                    f"being contributed to by "
                    f"{process}."
                )

                reason = (
                    f"{process} was identified as a "
                    f"significant CPU contributor while "
                    f"the system was experiencing "
                    f"{severity.lower()} CPU pressure."
                )

                self.add_candidate(
                    cause=cause,
                    category="CPU",
                    confidence=0.85,
                    evidence=evidence,
                    reason=reason,
                    process=process,
                    pid=pid
                )

    # ==========================================
    # RESULTS
    # ==========================================

    def get_candidates(self):

        return [
            candidate
            for candidate in self.candidates
        ]

    def get_primary_candidate(self):

        if not self.candidates:
            return None

        return max(
            self.candidates,
            key=lambda candidate:
                candidate["confidence"]
        )
