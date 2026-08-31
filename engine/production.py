# ==========================================
# Windows Technician v0.3
# PRODUCTION DIAGNOSTIC ENGINE
# ==========================================

from engine.factory import create_diagnostic_engine


def run_diagnostics():

    analyzer = create_diagnostic_engine()

    return analyzer.analyze()
