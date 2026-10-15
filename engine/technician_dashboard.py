# ==========================================
# Windows Technician v1.0
# TECHNICIAN DASHBOARD
# ==========================================

from copy import deepcopy

from engine.case_queue import CaseQueue
from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.managed_machine import ManagedMachine
from engine.proactive_alert import ProactiveAlert


class TechnicianDashboard:
    """
    Canonical technician dashboard composition boundary.

    The dashboard observes canonical platform objects and exposes
    presentation-ready snapshots.

    It does NOT:
    - diagnose
    - reason
    - generate recommendations
    - authorize remediation
    - execute remediation
    - verify remediation
    """

    def __init__(self):
        self.machines = []
        self.alerts = []
        self.cases = []
        self.fleets = []
        self.case_queue = None
        self._activity_logs = []

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

    def add_fleet(self, fleet):
        if not isinstance(fleet, Fleet):
            raise ValueError(
                "TechnicianDashboard requires a Fleet."
            )

        self.fleets.append(fleet)

    def set_case_queue(self, case_queue):
        if not isinstance(case_queue, CaseQueue):
            raise ValueError(
                "TechnicianDashboard requires a CaseQueue."
            )

        self.case_queue = case_queue

    def add_activity_log(self, activity_log):
        if activity_log is None:
            raise ValueError(
                "TechnicianDashboard requires an activity log."
            )

        if not hasattr(activity_log, "entries"):
            raise ValueError(
                "TechnicianDashboard requires an activity log "
                "with entries."
            )

        self._activity_logs.append(activity_log)

    @property
    def machine_count(self):
        return len(self.machines)

    @property
    def alert_count(self):
        return len(self.alerts)

    @property
    def case_count(self):
        return len(self.cases)

    @property
    def fleet_count(self):
        return len(self.fleets)

    def machine_health(self):
        """
        Return a presentation snapshot of machine health.
        """
        return [
            {
                "machine_id": machine.machine_id,
                "hostname": machine.hostname,
                "connection_state": machine.connection_state,
                "health_state": machine.health_state,
                "last_seen": machine.last_seen,
            }
            for machine in self.machines
        ]

    def fleet_alerts(self):
        """
        Return active/acknowledged proactive alerts.

        Resolved and dismissed alerts are not current dashboard
        alerts.
        """
        return [
            {
                "machine_id": alert.machine_id,
                "hostname": alert.hostname,
                "alert_type": alert.alert_type,
                "metric": alert.metric,
                "message": alert.message,
                "status": alert.status,
            }
            for alert in self.alerts
            if alert.status in {"ACTIVE", "ACKNOWLEDGED"}
        ]

    def active_cases(self):
        """
        Return the canonical active case collection.

        CaseQueue is preferred when supplied because it owns the
        lifecycle-state definition for active cases. The dashboard
        does not duplicate that lifecycle policy.
        """
        if self.case_queue is not None:
            cases = self.case_queue.active_cases
        else:
            active_states = {
                "OPEN",
                "INVESTIGATING",
                "DIAGNOSED",
                "ACTION_REQUIRED",
                "REMEDIATING",
                "VERIFYING",
            }
            cases = [
                case
                for case in self.cases
                if case.lifecycle_state in active_states
            ]

        return [
            self._case_snapshot(case)
            for case in cases
        ]

    def unresolved_problems(self):
        """
        Return cases that are not terminal/resolved.

        The dashboard reports state; it does not determine a
        remediation or resolution decision.
        """
        cases = (
            self.case_queue.cases
            if self.case_queue is not None
            else self.cases
        )

        terminal_states = {
            "RESOLVED",
            "CLOSED",
        }

        return [
            self._case_snapshot(case)
            for case in cases
            if case.lifecycle_state not in terminal_states
        ]

    def remediation_status(self):
        """
        Return remediation status already attached to dashboard
        case summaries/workflows when available.

        Missing status remains UNKNOWN rather than being inferred.
        """
        return self._case_status_projection("remediation_status")

    def verification_status(self):
        """
        Return verification status already attached to dashboard
        case summaries/workflows when available.

        Missing status remains UNKNOWN rather than being inferred.
        """
        return self._case_status_projection("verification_status")

    def recent_activity(self):
        """
        Return a defensive snapshot of canonical technician activity.
        """
        entries = []

        for activity_log in self._activity_logs:
            entries.extend(activity_log.entries)

        return deepcopy(entries)

    def dashboard_projection(self):
        """
        Build the complete read-only V1.0 dashboard projection.
        """
        return {
            "machine_health": self.machine_health(),
            "active_cases": self.active_cases(),
            "fleet_alerts": self.fleet_alerts(),
            "unresolved_problems": self.unresolved_problems(),
            "remediation_status": self.remediation_status(),
            "verification_status": self.verification_status(),
            "recent_activity": self.recent_activity(),
        }

    @staticmethod
    def _case_snapshot(case):
        return {
            "case_id": case.case_id,
            "machine_id": case.machine_id,
            "hostname": case.hostname,
            "lifecycle_state": case.lifecycle_state,
        }

    def _case_status_projection(self, attribute):
        projection = []

        for case in self._dashboard_cases():
            value = getattr(case, attribute, None)

            if value is None:
                value = "UNKNOWN"

            projection.append(
                {
                    "case_id": case.case_id,
                    "machine_id": case.machine_id,
                    "status": value,
                }
            )

        return projection

    def _dashboard_cases(self):
        if self.case_queue is not None:
            return list(self.case_queue.cases)

        return list(self.cases)
