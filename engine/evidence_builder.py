# ==========================================
# Windows Technician v0.3
# EVIDENCE BUILDER
# ==========================================

from engine.evidence import DiagnosticEvidence


class EvidenceBuilder:

    def __init__(self):

        self.evidence = DiagnosticEvidence()

    def add_category(self, category, data):

        self.evidence.add(
            category,
            data
        )

    def add_collector(self, collector):

        data = collector.collect()

        self.add_category(
            collector.category,
            data
        )

    def build(self):

        return self.evidence
