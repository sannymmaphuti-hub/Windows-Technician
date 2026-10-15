from copy import deepcopy

from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.proactive_alert import ProactiveAlert
from engine.technician_case_summary import TechnicianCaseSummary


class MachineOverview:
    """
    Canonical technician machine workspace.

    MachineOverview composes the canonical machine, alerts, diagnostic
    cases, and technician case summaries into a presentation-ready view.

    It does NOT diagnose, reason, generate recommendations, authorize,
    execute, or verify remediation.
    """

    def __init__(self, machine):
        if not isinstance(machine, ManagedMachine):
            raise ValueError(
                "MachineOverview requires a ManagedMachine."
            )

        self.machine = machine
        self.alerts = []
        self.cases = []
        self.case_summaries = []

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

    def add_case_summary(self, summary):
        if not isinstance(summary, TechnicianCaseSummary):
            raise ValueError(
                "MachineOverview requires a TechnicianCaseSummary."
            )

        if summary.workflow.case.machine_id != self.machine_id:
            raise ValueError(
                "Case summary belongs to a different machine."
            )

        self.case_summaries.append(summary)

    @property
    def alert_count(self):
        return len(self.alerts)

    @property
    def case_count(self):
        return len(self.cases)

    @property
    def case_summary_count(self):
        return len(self.case_summaries)

    def active_alerts(self):
        return [
            self._alert_snapshot(alert)
            for alert in self.alerts
            if alert.status in {"ACTIVE", "ACKNOWLEDGED"}
        ]

    def active_cases(self):
        active_states = {
            "OPEN",
            "INVESTIGATING",
            "DIAGNOSED",
            "ACTION_REQUIRED",
            "REMEDIATING",
            "VERIFYING",
        }

        return [
            self._case_snapshot(case)
            for case in self.cases
            if case.lifecycle_state in active_states
        ]

    def unresolved_problems(self):
        terminal_states = {"RESOLVED", "CLOSED"}

        return [
            self._case_snapshot(case)
            for case in self.cases
            if case.lifecycle_state not in terminal_states
        ]

    def findings(self):
        return deepcopy(
            [
                finding
                for case in self.cases
                for finding in case.findings
            ]
        )

    def root_causes(self):
        return deepcopy(
            [
                root_cause
                for case in self.cases
                for root_cause in case.root_causes
            ]
        )

    def recommendations(self):
        return deepcopy(
            [
                recommendation
                for case in self.cases
                for recommendation in case.recommendations
            ]
        )

    def remediation_status(self):
        return [
            {
                "case_id": summary.case_id,
                "status": summary.remediation_status,
            }
            for summary in self.case_summaries
        ]

    def verification_status(self):
        return [
            {
                "case_id": summary.case_id,
                "status": summary.verification_status,
            }
            for summary in self.case_summaries
        ]

    def escalation_status(self):
        return [
            {
                "case_id": summary.case_id,
                "status": summary.escalation_status,
            }
            for summary in self.case_summaries
        ]

    def decisions(self):
        return [
            {
                "case_id": summary.case_id,
                "decision": deepcopy(summary.decision),
            }
            for summary in self.case_summaries
        ]

    def workspace_projection(self):
        """
        Return the complete presentation-ready machine workspace.

        Operational status is read from TechnicianCaseSummary, which owns
        those lifecycle surfaces. No remediation or verification operation
        is performed here.
        """
        return {
            "machine": {
                "machine_id": self.machine_id,
                "hostname": self.hostname,
                "platform": self.platform,
                "operating_system": self.operating_system,
                "connection_state": self.connection_state,
                "health_state": self.health_state,
                "last_seen": self.last_seen,
            },
            "alerts": self.active_alerts(),
            "active_cases": self.active_cases(),
            "unresolved_problems": self.unresolved_problems(),
            "findings": self.findings(),
            "root_causes": self.root_causes(),
            "recommendations": self.recommendations(),
            "remediation_status": self.remediation_status(),
            "verification_status": self.verification_status(),
            "escalation_status": self.escalation_status(),
            "decisions": self.decisions(),
        }

    @staticmethod
    def _alert_snapshot(alert):
        return {
            "machine_id": alert.machine_id,
            "hostname": alert.hostname,
            "alert_type": alert.alert_type,
            "metric": alert.metric,
            "message": alert.message,
            "status": alert.status,
        }

    @staticmethod
    def _case_snapshot(case):
        return {
            "case_id": case.case_id,
            "machine_id": case.machine_id,
            "hostname": case.hostname,
            "lifecycle_state": case.lifecycle_state,
        }
