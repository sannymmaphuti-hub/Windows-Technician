# ==========================================
# Windows Technician v0.8
# TECHNICIAN DASHBOARD
# ==========================================

from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.proactive_alert import ProactiveAlert


class TechnicianDashboard:

    def __init__(self):
        self.machines = []
        self.alerts = []
        self.cases = []

    def add_machine(self, machine):
        if not isinstance(machine, ManagedMachine):
            raise ValueError(
                "TechnicianDashboard requires a ManagedMachine."
            )

        self.machines.append(machine)

    def add_alert(self, alert):
        if not isinstance(alert, ProactiveAlert):
            raise ValueError(
                "TechnicianDashboard requires a ProactiveAlert."
            )

        self.alerts.append(alert)

    def add_case(self, case):
        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "TechnicianDashboard requires a DiagnosticCase."
            )

        self.cases.append(case)

    @property
    def machine_count(self):
        return len(self.machines)

    @property
    def alert_count(self):
        return len(self.alerts)

    @property
    def case_count(self):
        return len(self.cases)