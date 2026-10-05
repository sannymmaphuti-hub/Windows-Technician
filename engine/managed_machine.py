# ==========================================
# Windows Technician v0.8
# MANAGED MACHINE
# ==========================================


class ManagedMachine:

    def __init__(
        self,
        machine_id,
        hostname,
        platform,
        operating_system,
    ):
        if machine_id is None:
            raise ValueError("machine_id is required")

        if hostname is None:
            raise ValueError("hostname is required")

        if platform is None:
            raise ValueError("platform is required")

        if operating_system is None:
            raise ValueError(
                "operating_system is required"
            )

        self.machine_id = machine_id
        self.hostname = hostname
        self.platform = platform
        self.operating_system = operating_system

        self.connection_state = "UNKNOWN"
        self.health_state = "UNKNOWN"
        self.last_seen = None

    @property
    def is_available(self):
        return self.connection_state == "CONNECTED"