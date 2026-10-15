from copy import deepcopy

from engine.fleet import Fleet
from engine.proactive_alert import ProactiveAlert


class FleetAlertAggregation:
    """
    Read-only fleet proactive-alert aggregation.

    Projects ProactiveAlert objects whose machine identity belongs
    to the canonical Fleet membership.

    This class does not create, mutate, acknowledge, resolve,
    diagnose, authorize, execute, or verify alerts.
    """

    _VISIBLE_STATES = {
        "ACTIVE",
        "ACKNOWLEDGED",
    }

    def __init__(self, fleet, alerts=None):
        if not isinstance(fleet, Fleet):
            raise ValueError(
                "FleetAlertAggregation requires a Fleet."
            )

        if alerts is None:
            alerts = []

        if not isinstance(alerts, (list, tuple)):
            raise ValueError(
                "alerts must be a list or tuple."
            )

        for alert in alerts:
            if not isinstance(alert, ProactiveAlert):
                raise ValueError(
                    "FleetAlertAggregation requires "
                    "ProactiveAlert objects."
                )

        self.fleet = fleet
        self._alerts = list(alerts)

    @property
    def alerts(self):
        return list(self._fleet_alerts())

    @property
    def alert_count(self):
        return len(self.alerts)

    @property
    def active_alert_count(self):
        return len(self.active_alerts())

    @property
    def acknowledged_alert_count(self):
        return len(self.acknowledged_alerts())

    def active_alerts(self):
        return [
            self._alert_snapshot(alert)
            for alert in self._fleet_alerts()
            if alert.status == "ACTIVE"
        ]

    def acknowledged_alerts(self):
        return [
            self._alert_snapshot(alert)
            for alert in self._fleet_alerts()
            if alert.status == "ACKNOWLEDGED"
        ]

    def visible_alerts(self):
        return [
            self._alert_snapshot(alert)
            for alert in self._fleet_alerts()
            if alert.status in self._VISIBLE_STATES
        ]

    def alerts_by_machine(self):
        result = {}

        for alert in self._fleet_alerts():
            machine_id = alert.machine_id
            result.setdefault(machine_id, [])
            result[machine_id].append(
                self._alert_snapshot(alert)
            )

        return deepcopy(result)

    def alert_type_counts(self):
        counts = {}

        for alert in self._fleet_alerts():
            alert_type = alert.alert_type
            counts[alert_type] = counts.get(
                alert_type,
                0,
            ) + 1

        return counts

    def affected_machine_ids(self):
        return list(
            dict.fromkeys(
                alert.machine_id
                for alert in self._fleet_alerts()
            )
        )

    def projection(self):
        return {
            "alert_count": self.alert_count,
            "active_alert_count": self.active_alert_count,
            "acknowledged_alert_count": (
                self.acknowledged_alert_count
            ),
            "affected_machine_ids": self.affected_machine_ids(),
            "alert_type_counts": self.alert_type_counts(),
            "active_alerts": self.active_alerts(),
            "acknowledged_alerts": self.acknowledged_alerts(),
            "visible_alerts": self.visible_alerts(),
            "alerts_by_machine": self.alerts_by_machine(),
        }

    def _fleet_alerts(self):
        fleet_machine_ids = set(self.fleet.machine_ids)

        return [
            alert
            for alert in self._alerts
            if alert.machine_id in fleet_machine_ids
        ]

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
