
# ==========================================
# WINDOWS TECHNICIAN v0.2
# DIAGNOSTIC ANALYZER
# ==========================================


from engine.evidence_builder import EvidenceBuilder
from engine.diagnostic_engine import DiagnosticEngine

from engine.intelligence.process_intelligence import (
    ProcessIntelligence
)

from engine.intelligence.process_finding import (
    ProcessFindingBuilder
)

from engine.intelligence.process_pipeline import (
    ProcessIntelligencePipeline
)

from engine.intelligence.memory_intelligence import (
    MemoryIntelligence
)

from engine.intelligence.memory_finding import (
    MemoryFindingBuilder
)

from engine.intelligence.memory_temporal_intelligence import (
    MemoryTemporalIntelligence
)

from engine.intelligence.memory_temporal_finding import (
    MemoryTemporalFindingBuilder
)

from engine.intelligence.memory_trend_intelligence import (
    MemoryTrendIntelligence
)

from engine.intelligence.memory_diagnostic_intelligence import (
    MemoryDiagnosticIntelligence
)

from engine.intelligence.memory_diagnostic_finding import (
    MemoryDiagnosticFindingBuilder
)

from engine.root_cause_analyzer import (
    RootCauseAnalyzer
)

from diagnostics.correlation_analyzer import (
    correlate_memory_and_cpu_behavior
)

from engine.correlation_adapter import (
    build_process_cpu_behavior_findings
)


class Analyzer:

    def __init__(
        self,
        collectors=None,
        rules=None,
        recommendation_engine=None,
        intelligence=None,
        process_collector=None
    ):

        self.collectors = collectors or []
        self.rules = rules or []

        # ==========================================
        # PROCESS COLLECTOR
        # ==========================================

        self.process_collector = process_collector

        # ==========================================
        # PROCESS INTELLIGENCE
        # ==========================================

        # Keep the public attribute expected by tests
        # and by other parts of the application.
        self.intelligence = (
            intelligence
            or ProcessIntelligence()
        )

        self.process_finding_builder = (
            ProcessFindingBuilder()
        )

        self.process_pipeline = (
            ProcessIntelligencePipeline(
                intelligence=self.intelligence,
                finding_builder=self.process_finding_builder
            )
)

        # ==========================================
        # DIAGNOSTIC ENGINE
        # ==========================================

        self.engine = DiagnosticEngine(
            recommendation_engine=recommendation_engine
        )

        # ==========================================
        # MEMORY INTELLIGENCE
        # ==========================================

        self.memory_intelligence = (
            MemoryIntelligence()
        )

        self.memory_finding_builder = (
            MemoryFindingBuilder()
        )

        # ==========================================
        # MEMORY HISTORY
        # ==========================================

        # Persistent across multiple analyze() calls.
        self.memory_history = []

        # ==========================================
        # MEMORY TEMPORAL INTELLIGENCE
        # ==========================================

        self.memory_temporal_intelligence = (
            MemoryTemporalIntelligence()
        )

        self.memory_temporal_finding_builder = (
            MemoryTemporalFindingBuilder()
        )

        # ==========================================
        # MEMORY TREND INTELLIGENCE
        # ==========================================

        self.memory_trend_intelligence = (
            MemoryTrendIntelligence()
        )

        # ==========================================
        # MEMORY DIAGNOSTIC INTELLIGENCE
        # ==========================================

        self.memory_diagnostic_intelligence = (
            MemoryDiagnosticIntelligence()
        )

        self.memory_diagnostic_finding_builder = (
            MemoryDiagnosticFindingBuilder()
        )

        # ==========================================
        # ROOT CAUSE ANALYSIS
        # ==========================================

        self.root_cause_analyzer = (
            RootCauseAnalyzer()
        )

        # ==========================================
        # RULES
        # ==========================================

        for rule in self.rules:
            self.engine.add_rule(rule)


    # ==========================================
    # EVIDENCE COLLECTION
    # ==========================================

    def collect_evidence(self):

        builder = EvidenceBuilder()

        for collector in self.collectors:

            data = collector.collect()

            if collector.category == "STORAGE":

                data = {
                    "devices": data
                }

            elif collector.category == "GPU":

                data = {
                    "gpus": data
                }

            builder.add_category(
                collector.category,
                data
            )

        return builder.build()

    # ==========================================
    # PROCESS INTELLIGENCE
    # ==========================================

    def _run_process_intelligence(
        self,
        evidence_data
    ):

        cpu_evidence = evidence_data.get(
            "CPU"
        )

        process_evidence = evidence_data.get(
            "PROCESS"
        )

        if not cpu_evidence:
            return {
                "intelligence": None,
                "finding": None
            }

        if not process_evidence:
            return {
                "intelligence": None,
                "finding": None
            }

        # ------------------------------------------
        # Process collector
        # ------------------------------------------

        process_collector = self.process_collector

        # ------------------------------------------
        # Temporal CPU history is OPTIONAL.
        #
        # Some collectors (especially test/fake
        # collectors) only provide static process
        # evidence.
        # ------------------------------------------

        process_cpu_history = []

        if (
            process_collector is not None
            and hasattr(
                process_collector,
                "collect_cpu_history"
            )
        ):

            try:

                process_cpu_history = (
                    process_collector.collect_cpu_history(
                        sample_count=5,
                        interval=1
                    )
                )

            except (
                TypeError,
                AttributeError,
                RuntimeError
            ):

                process_cpu_history = []

        # ------------------------------------------
        # Run process intelligence
        # ------------------------------------------

        return self.process_pipeline.analyze(
            cpu_evidence=cpu_evidence,
            process_evidence=process_evidence,
            process_cpu_history=process_cpu_history
        )


    # ==========================================
    # MEMORY INTELLIGENCE
    # ==========================================

    def _run_memory_intelligence(
        self,
        evidence_data
    ):

        memory_evidence = evidence_data.get(
            "MEMORY"
        )

        process_evidence = evidence_data.get(
            "PROCESS"
        )

        if not memory_evidence:
            return {
                "intelligence": None,
                "finding": None
            }

        system_memory = memory_evidence.get(
            "usage_percent"
        )

        if system_memory is None:
            return {
                "intelligence": None,
                "finding": None
            }

        processes = []

        if process_evidence:
            processes = process_evidence.get(
                "processes",
                []
            )

        if not processes:
            return {
                "intelligence": None,
                "finding": None
            }

        # Find the process using the most memory.
        valid_processes = [
            process
            for process in processes
            if isinstance(process, dict)
        ]

        if not valid_processes:
            return {
                "intelligence": None,
                "finding": None
            }

        top_process = max(
            valid_processes,
            key=lambda process: process.get(
                "memory_mb",
                0
            )
        )

        intelligence = (
            self.memory_intelligence.analyze(
                system_memory_percent=system_memory,
                process=top_process
            )
        )

        if intelligence is None:
            return {
                "intelligence": None,
                "finding": None
            }

        finding = (
            self.memory_finding_builder.build(
                intelligence
            )
        )

        return {
            "intelligence": intelligence,
            "finding": finding
        }


    # ==========================================
    # MEMORY HISTORY
    # ==========================================

    def _record_memory_history(
        self,
        evidence_data
    ):

        memory_evidence = evidence_data.get(
            "MEMORY"
        )

        if not memory_evidence:
            return

        usage_percent = memory_evidence.get(
            "usage_percent"
        )

        if usage_percent is None:
            return

        self.memory_history.append(
            usage_percent
        )


    # ==========================================
    # MEMORY TREND INTELLIGENCE
    # ==========================================

    def _run_memory_trend_intelligence(self):

        return (
            self.memory_trend_intelligence.analyze(
                self.memory_history
            )
        )


    # ==========================================
    # MEMORY TEMPORAL INTELLIGENCE
    # ==========================================

    def _run_memory_temporal_intelligence(
        self,
        evidence_data
    ):

        memory_evidence = evidence_data.get(
            "MEMORY"
        )

        process_evidence = evidence_data.get(
            "PROCESS"
        )

        if not memory_evidence:
            return None

        if not process_evidence:
            return None

        system_memory = memory_evidence.get(
            "usage_percent"
        )

        if system_memory is None:
            return None

        processes = process_evidence.get(
            "processes",
            []
        )

        if not processes:
            return None

        valid_processes = [
            process
            for process in processes
            if isinstance(process, dict)
        ]

        if not valid_processes:
            return None

        top_process = max(
            valid_processes,
            key=lambda process: process.get(
                "memory_mb",
                0
            )
        )

        pid = top_process.get(
            "pid",
            0
        )

        # Memory history is currently system-level history.
        # Feed it to the temporal intelligence so that the
        # temporal component can classify the current behavior.
        return (
            self.memory_temporal_intelligence.analyze(
                system_memory_percent=system_memory,
                process=top_process,
                memory_history=self.memory_history
            )
        )


    # ==========================================
    # MEMORY TEMPORAL FINDING
    # ==========================================

    def _build_memory_temporal_finding(
        self,
        temporal_intelligence
    ):

        if temporal_intelligence is None:
            return None

        return (
            self.memory_temporal_finding_builder.build(
                temporal_intelligence
            )
        )


    # ==========================================
    # MEMORY DIAGNOSTIC INTELLIGENCE
    # ==========================================

    def _run_memory_diagnostic_intelligence(
        self,
        evidence_data,
        temporal_intelligence,
        trend_intelligence
    ):

        memory_evidence = evidence_data.get(
            "MEMORY"
        )

        if not memory_evidence:
            return None

        system_memory = memory_evidence.get(
            "usage_percent"
        )

        if system_memory is None:
            return None

        if temporal_intelligence is None:
            return None

        return (
            self.memory_diagnostic_intelligence.analyze(
                system_memory_percent=system_memory,
                temporal_intelligence=temporal_intelligence,
                trend_intelligence=trend_intelligence
            )
        )


    # ==========================================
    # MEMORY DIAGNOSTIC FINDING
    # ==========================================

    def _build_memory_diagnostic_finding(
        self,
        diagnostic_intelligence
    ):

        if diagnostic_intelligence is None:
            return None

        return (
            self.memory_diagnostic_finding_builder.build(
                diagnostic_intelligence
            )
        )


    # ==========================================
    # CORRELATION ANALYSIS
    # ==========================================

    def _run_correlations(
        self,
        evidence_data,
        process_intelligence=None,
        memory_intelligence=None
    ):

        correlations = []

        if (
            memory_intelligence is not None
            and process_intelligence is not None
        ):

            try:

                memory_diagnostics = {
                    "status": memory_intelligence.get(
                        "severity",
                        "INFO"
                    )
                }

                process_behavior_findings = [
                    {
                        "name": process_intelligence.get(
                            "name",
                            "Unknown"
                        ),
                        "behavior": process_intelligence.get(
                            "behavior",
                            "UNKNOWN"
                        ),
                        "severity": process_intelligence.get(
                            "severity",
                            "INFO"
                        ),
                        "category": "PROCESS CPU BEHAVIOR"
                    }
                ]

                correlation = (
                    correlate_memory_and_cpu_behavior(
                        memory_diagnostics,
                        process_behavior_findings
                    )
                )

                if correlation:

                    if isinstance(
                        correlation,
                        list
                    ):

                        correlations.extend(
                            correlation
                        )

                    else:

                        correlations.append(
                            correlation
                        )

            except (
                TypeError,
                AttributeError,
                KeyError
            ):

                pass

        return correlations


    # ==========================================
    # ROOT CAUSE ANALYSIS
    # ==========================================

    def _run_root_cause_analysis(
        self,
        findings,
        correlations
    ):

        try:

            result = (
                self.root_cause_analyzer.analyze_result(
                    findings=findings,
                    correlations=correlations
                )
            )

            if isinstance(
                result,
                dict
            ):

                candidates = result.get(
                    "candidates",
                    []
                )

                primary = result.get(
                    "primary"
                )

                return candidates, primary

        except (
            TypeError,
            AttributeError,
            KeyError
        ):

            pass

        return [], None
    
    # ==========================================
    # OVERALL DIAGNOSIS STATUS
    # ==========================================

    def _calculate_overall_status(
        self,
        findings
    ):

        if not findings:
            return "NORMAL"

        severity_priority = {
            "INFO": 1,
            "NORMAL": 1,
            "WARNING": 2,
            "CRITICAL": 3
        }

        highest_severity = "NORMAL"
        highest_priority = 0

        for finding in findings:

            if not isinstance(
                finding,
                dict
            ):
                continue

            severity = finding.get(
                "severity",
                "NORMAL"
            )

            priority = severity_priority.get(
                severity,
                1
            )

            if priority > highest_priority:

                highest_priority = priority
                highest_severity = severity

        return highest_severity


    # ==========================================
    # MAIN ANALYSIS PIPELINE
    # ==========================================

    def analyze(self):

        # ------------------------------------------
        # 1. COLLECT EVIDENCE
        # ------------------------------------------

        evidence = self.collect_evidence()

        evidence_data = evidence.get_all()

        # ------------------------------------------
        # 2. PROCESS INTELLIGENCE
        # ------------------------------------------

        process_result = (
            self._run_process_intelligence(
                evidence_data
            )
        )

        process_intelligence = (
            process_result.get(
                "intelligence"
            )
        )

        process_finding = (
            process_result.get(
                "finding"
            )
        )

        # ------------------------------------------
        # 3. MEMORY HISTORY
        # ------------------------------------------

        self._record_memory_history(
            evidence_data
        )

        # ------------------------------------------
        # 4. MEMORY INTELLIGENCE
        # ------------------------------------------

        memory_result = (
            self._run_memory_intelligence(
                evidence_data
            )
        )

        memory_intelligence = (
            memory_result.get(
                "intelligence"
            )
        )

        memory_finding = (
            memory_result.get(
                "finding"
            )
        )

        # ------------------------------------------
        # 5. MEMORY TREND
        # ------------------------------------------

        memory_trend_intelligence = (
            self._run_memory_trend_intelligence()
        )

        # ------------------------------------------
        # 6. MEMORY TEMPORAL
        # ------------------------------------------

        memory_temporal_intelligence = (
            self._run_memory_temporal_intelligence(
                evidence_data
            )
        )

        memory_temporal_finding = (
            self._build_memory_temporal_finding(
                memory_temporal_intelligence
            )
        )

        # ------------------------------------------
        # 7. MEMORY DIAGNOSTIC
        # ------------------------------------------

        memory_diagnostic_intelligence = (
            self._run_memory_diagnostic_intelligence(
                evidence_data,
                memory_temporal_intelligence,
                memory_trend_intelligence
            )
        )

        memory_diagnostic_finding = (
            self._build_memory_diagnostic_finding(
                memory_diagnostic_intelligence
            )
        )

        # ------------------------------------------
        # 8. COLLECT DIAGNOSTIC ENGINE FINDINGS
        # ------------------------------------------

        diagnosis = (
            self.engine.analyze(
                evidence_data
            )
        )

        # ------------------------------------------
        # Normalize diagnosis structure.
        # ------------------------------------------

        if diagnosis is None:

            diagnosis = {
                "findings": [],
                "recommendations": [],
                "total_findings": 0
            }

        if not isinstance(
            diagnosis,
            dict
        ):

            diagnosis = {
                "findings": [],
                "recommendations": [],
                "total_findings": 0
            }

        diagnosis_findings = list(
            diagnosis.get(
                "findings",
                []
            )
            or []
        )

        # ------------------------------------------
        # Add intelligence findings only when they
        # are not already represented by the engine.
        #
        # Process intelligence should become the
        # process diagnostic finding rather than
        # creating duplicate process findings.
        # ------------------------------------------

        if process_finding is not None:

            process_already_present = any(

                finding is process_finding

                or (
                    isinstance(
                        finding,
                        dict
                    )
                    and isinstance(
                        process_finding,
                        dict
                    )
                    and finding.get(
                        "category"
                    )
                    == process_finding.get(
                        "category"
                    )
                    and finding.get(
                        "process"
                    )
                    == process_finding.get(
                        "process"
                    )
                    and finding.get(
                        "pid"
                    )
                    == process_finding.get(
                        "pid"
                    )
                )

                for finding in diagnosis_findings
            )

            if not process_already_present:

                diagnosis_findings.append(
                    process_finding
                )
        # ------------------------------------------
        # Add memory intelligence finding.
        # ------------------------------------------

        if memory_finding is not None:

            memory_intelligence_already_present = any(

                finding is memory_finding

                or (
                    isinstance(
                        finding,
                        dict
                    )
                    and isinstance(
                        memory_finding,
                        dict
                    )
                    and finding.get(
                        "category"
                    )
                    == memory_finding.get(
                        "category"
                    )
                    and finding.get(
                        "process"
                    )
                    == memory_finding.get(
                        "process"
                    )
                    and finding.get(
                        "pid"
                    )
                    == memory_finding.get(
                        "pid"
                    )
                )

                for finding in diagnosis_findings
            )

            if not memory_intelligence_already_present:

                diagnosis_findings.append(
                    memory_finding
                )


        # ------------------------------------------
        # Add memory diagnostic finding.
        # ------------------------------------------

        if memory_diagnostic_finding is not None:

            memory_already_present = any(

                finding is memory_diagnostic_finding

                or (
                    isinstance(
                        finding,
                        dict
                    )
                    and isinstance(
                        memory_diagnostic_finding,
                        dict
                    )
                    and finding.get(
                        "category"
                    )
                    == "MEMORY"
                    and finding.get(
                        "process"
                    )
                    == memory_diagnostic_finding.get(
                        "process"
                    )
                    and finding.get(
                        "pid"
                    )
                    == memory_diagnostic_finding.get(
                        "pid"
                    )
                )

                for finding in diagnosis_findings
            )

            if not memory_already_present:

                diagnosis_findings.append(
                    memory_diagnostic_finding
                )

        # ------------------------------------------
        # Recalculate overall status after all
        # intelligence findings have been added.
        # ------------------------------------------

        diagnosis["status"] = (
            self._calculate_overall_status(
                diagnosis_findings
            )
        )

        diagnosis["findings"] = diagnosis_findings

        diagnosis["total_findings"] = len(
            diagnosis_findings
        )

        # ------------------------------------------
        # 9. CORRELATIONS
        # ------------------------------------------

        correlations = (
            self._run_correlations(
                evidence_data,
                process_intelligence,
                memory_intelligence
            )
        )

        # ------------------------------------------
        # 10. ROOT CAUSE ANALYSIS
        # ------------------------------------------

        root_cause_candidates, primary_root_cause = (
            self._run_root_cause_analysis(
                diagnosis_findings,
                correlations
            )
        )

        # ------------------------------------------
        # 11. FINAL RESULT
        # ------------------------------------------

        return {

            "evidence":
                evidence_data,

            # Process intelligence
            "intelligence":
                process_intelligence,

            "process_intelligence":
                process_intelligence,

            "process_finding":
                process_finding,

            # Memory intelligence
            "memory_intelligence":
                memory_intelligence,

            "memory_finding":
                memory_finding,

            # Memory history
            "memory_history":
                list(self.memory_history),

            # Memory trend
            "memory_trend_intelligence":
                memory_trend_intelligence,

            # Memory temporal
            "memory_temporal_intelligence":
                memory_temporal_intelligence,

            "memory_temporal_finding":
                memory_temporal_finding,

            # Memory diagnostic
            "memory_diagnostic_intelligence":
                memory_diagnostic_intelligence,

            "memory_diagnostic_finding":
                memory_diagnostic_finding,

            # Correlation
            "correlations":
                correlations,

            # Root cause
            "root_cause_candidates":
                root_cause_candidates,

            "primary_root_cause":
                primary_root_cause,

            # Final diagnosis
            "diagnosis":
                diagnosis
        }

