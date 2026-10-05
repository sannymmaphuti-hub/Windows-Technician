# ==========================================
# Windows Technician v0.8
# REMOTE SESSION
# ==========================================

import uuid

from engine.managed_machine import ManagedMachine


class RemoteSession:

    VALID_STATES = {
        "DISCONNECTED",
        "CONNECTING",
        "CONNECTED",
        "FAILED",
    }

    def __init__(self, machine):
        if not isinstance(machine, ManagedMachine):
            raise ValueError(
                "RemoteSession requires a ManagedMachine."
            )

        self.machine = machine
        self.session_id = str(uuid.uuid4())
        self.state = "DISCONNECTED"

    def connect(self):
        if self.state == "CONNECTED":
            return

        self.state = "CONNECTED"
        self.machine.connection_state = "CONNECTED"

    def disconnect(self):
        if self.state == "DISCONNECTED":
            return

        self.state = "DISCONNECTED"
        self.machine.connection_state = "DISCONNECTED"