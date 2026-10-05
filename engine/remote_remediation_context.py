# ==========================================
# Windows Technician v0.8
# REMOTE REMEDIATION CONTEXT
# ==========================================

from engine.managed_machine import ManagedMachine
from engine.remote_session import RemoteSession


class RemoteRemediationContext:

    def __init__(self, machine, session):
        if not isinstance(machine, ManagedMachine):
            raise ValueError(
                "RemoteRemediationContext requires a ManagedMachine."
            )

        if not isinstance(session, RemoteSession):
            raise ValueError(
                "RemoteRemediationContext requires a RemoteSession."
            )

        if session.machine is not machine:
            raise ValueError(
                "RemoteSession does not belong to the ManagedMachine."
            )

        if not machine.is_available:
            raise ValueError(
                "Remote remediation requires an available machine."
            )

        self.machine = machine
        self.session = session

    @property
    def machine_id(self):
        return self.machine.machine_id

    @property
    def hostname(self):
        return self.machine.hostname

    @property
    def session_id(self):
        return self.session.session_id

    @property
    def is_remote(self):
        return True