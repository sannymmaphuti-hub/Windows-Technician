# ==========================================
# Windows Technician v0.8
# MACHINE OVERVIEW
# ==========================================

from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.proactive_alert import ProactiveAlert


class MachineOverview:

    def __init__(self, machine):
        if not isinstance(machine, ManagedMachine):
            raise ValueError(
                "MachineOverview requires a ManagedMachine."
            )

        self.machine = machine
        self.alerts = []
        self.cases = []

    @property
    def machine_id(self):
        return self.machine.machine_id

    @property
    def hostname(self):
        return self.machine.hostname

    @property
    def platform(self):
        return self.machine.platform

    @property
    def operating_system(self):
        return self.machine.operating_system

    @property
    def connection_state(self):
        return self.machine.connection_state

    @property
    def health_state(self):
        return self.machine.health_state

    @property
    def last_seen(self):
        return self.machine.last_seen

    def add_alert(self, alert):
        if not isinstance(alert, ProactiveAlert):
            raise ValueError(
                "MachineOverview requires a ProactiveAlert."
            )

        if alert.machine_id != self.machine_id:
            raise ValueError(
                "Alert belongs to a different machine."
            )

        self.alerts.append(alert)

    def add_case(self, case):
        if not isinstance(case, DiagnosticCase):
            raise ValueError(
                "MachineOverview requires a DiagnosticCase."
            )

        if case.machine_id != self.machine_id:
            raise ValueError(
                "Case belongs to a different machine."
            )

        self.cases.append(case)

    @property
    def alert_count(self):
        return len(self.alerts)

    @property
    def case_count(self):
        return len(self.cases)