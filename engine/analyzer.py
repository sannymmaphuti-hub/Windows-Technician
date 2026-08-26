# ==========================================
# WINDOWS TECHNICIAN v0.1
# DIAGNOSTIC ANALYZER
# ==========================================

from engine.evidence_builder import EvidenceBuilder
from engine.diagnostic_engine import DiagnosticEngine


class Analyzer:

    def __init__(
        self,
        collectors=None,
        rules=None,
        recommendation_engine=None
    ):

        self.collectors = collectors or []
        self.rules = rules or []

        self.engine = DiagnosticEngine(
            recommendation_engine=recommendation_engine
        )

        for rule in self.rules:
            self.engine.add_rule(rule)

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

    def analyze(self):

        evidence = self.collect_evidence()

        result = self.engine.diagnose(
            evidence.get_all()
        )

        return {
            "evidence": evidence.get_all(),
            "diagnosis": result
        }