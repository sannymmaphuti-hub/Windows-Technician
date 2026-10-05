from engine.managed_machine import ManagedMachine


class ProactiveAlert:

    VALID_STATUSES = {
        "ACTIVE",
        "ACKNOWLEDGED",
        "RESOLVED",
        "DISMISSED",
    }

    def __init__(
        self,
        machine,
        alert_type,
        metric,
        message,
    ):
        if not isinstance(machine, ManagedMachine):
            raise ValueError(
                "ProactiveAlert requires a ManagedMachine."
            )

        if alert_type is None:
            raise ValueError("alert_type is required.")

        if metric is None:
            raise ValueError("metric is required.")

        if message is None:
            raise ValueError("message is required.")

        self.machine = machine
        self.alert_type = alert_type
        self.metric = metric
        self.message = message
        self.status = "ACTIVE"

    @property
    def machine_id(self):
        return self.machine.machine_id

    @property
    def hostname(self):
        return self.machine.hostname

    def acknowledge(self):
        if self.status == "ACTIVE":
            self.status = "ACKNOWLEDGED"

    def resolve(self):
        if self.status in {"ACTIVE", "ACKNOWLEDGED"}:
            self.status = "RESOLVED"

    def dismiss(self):
        if self.status in {"ACTIVE", "ACKNOWLEDGED"}:
            self.status = "DISMISSED"