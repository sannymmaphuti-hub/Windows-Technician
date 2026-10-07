# ==========================================
# Windows Technician v0.9
# FLEET
# ==========================================

import uuid

from engine.managed_machine import ManagedMachine


class Fleet:
    """
    Orchestration scope for a collection of managed machines.

    Fleet owns:
    - machine membership
    - fleet-level machine observation
    - non-authoritative aggregate intelligence

    Fleet does NOT own:
    - DiagnosticCase
    - TechnicianWorkflow
    - RemoteSession
    - RemediationAction
    - RemediationResult
    - authorization
    - recovery lifecycle
    """

    def __init__(self, name):
        if name is None:
            raise ValueError("name is required")

        if not isinstance(name, str):
            raise ValueError("name must be a string")

        if not name.strip():
            raise ValueError("name cannot be empty")

        self.fleet_id = str(uuid.uuid4())
        self.name = name

        # Machine identity is the canonical membership key.
        self._machines = {}

    @property
    def machines(self):
        """
        Return the current fleet members.

        A new list is returned so callers cannot mutate
        fleet membership directly.
        """
        return list(self._machines.values())

    @property
    def machine_ids(self):
        """
        Return machine IDs in fleet membership order.
        """
        return list(self._machines.keys())

    @property
    def machine_count(self):
        return len(self._machines)

    @property
    def connected_machines(self):
        return [
            machine
            for machine in self._machines.values()
            if machine.connection_state == "CONNECTED"
        ]

    @property
    def disconnected_machines(self):
        return [
            machine
            for machine in self._machines.values()
            if machine.connection_state == "DISCONNECTED"
        ]

    @property
    def unknown_connection_machines(self):
        return [
            machine
            for machine in self._machines.values()
            if machine.connection_state == "UNKNOWN"
        ]

    @property
    def healthy_machines(self):
        return [
            machine
            for machine in self._machines.values()
            if machine.health_state == "HEALTHY"
        ]

    @property
    def warning_machines(self):
        return [
            machine
            for machine in self._machines.values()
            if machine.health_state == "WARNING"
        ]

    @property
    def unknown_health_machines(self):
        return [
            machine
            for machine in self._machines.values()
            if machine.health_state == "UNKNOWN"
        ]

    @property
    def summary(self):
        """
        Return a snapshot of the current fleet state.

        Observation only. This does not diagnose, authorize,
        execute, or modify any machine.
        """
        return {
            "fleet_id": self.fleet_id,
            "name": self.name,
            "machine_count": self.machine_count,
            "connected_count": len(self.connected_machines),
            "disconnected_count": len(self.disconnected_machines),
            "unknown_connection_count": len(
                self.unknown_connection_machines
            ),
            "healthy_count": len(self.healthy_machines),
            "warning_count": len(self.warning_machines),
            "unknown_health_count": len(
                self.unknown_health_machines
            ),
        }

    @property
    def intelligence(self):
        """
        Return non-authoritative aggregate fleet intelligence.

        This describes concentration of current machine states.
        It does not diagnose individual machines and does not
        authorize or execute remediation.
        """
        health_counts = {
            "HEALTHY": len(self.healthy_machines),
            "WARNING": len(self.warning_machines),
            "UNKNOWN": len(self.unknown_health_machines),
        }

        connection_counts = {
            "CONNECTED": len(self.connected_machines),
            "DISCONNECTED": len(self.disconnected_machines),
            "UNKNOWN": len(self.unknown_connection_machines),
        }

        return {
            "machine_count": self.machine_count,
            "healthy_count": health_counts["HEALTHY"],
            "warning_count": health_counts["WARNING"],
            "unknown_health_count": health_counts["UNKNOWN"],
            "dominant_health_state": self._dominant_state(
                health_counts
            ),
            "connected_count": connection_counts["CONNECTED"],
            "disconnected_count": connection_counts["DISCONNECTED"],
            "unknown_connection_count": connection_counts[
                "UNKNOWN"
            ],
            "dominant_connection_state": self._dominant_state(
                connection_counts
            ),
        }

    @staticmethod
    def _dominant_state(counts):
        """
        Return the unique state with the highest count.

        A tie or an empty collection produces None.
        """
        if not counts:
            return None

        highest = max(counts.values())

        if highest == 0:
            return None

        dominant_states = [
            state
            for state, count in counts.items()
            if count == highest
        ]

        if len(dominant_states) != 1:
            return None

        return dominant_states[0]

    def add_machine(self, machine):
        """
        Add an existing ManagedMachine to the fleet.

        Fleet references the existing machine object. It does
        not create a copy and does not modify machine state.
        """
        if not isinstance(machine, ManagedMachine):
            raise ValueError(
                "Fleet requires a ManagedMachine."
            )

        machine_id = machine.machine_id

        if machine_id in self._machines:
            raise ValueError(
                f"Machine '{machine_id}' is already a member "
                "of this fleet."
            )

        self._machines[machine_id] = machine

    def remove_machine(self, machine_id):
        """
        Remove a machine from the fleet.

        Removing membership does not destroy or modify the
        ManagedMachine object.
        """
        return self._machines.pop(machine_id, None)

    def get_machine(self, machine_id):
        """
        Return the ManagedMachine with the supplied identity.

        Returns None when the machine is not a fleet member.
        """
        return self._machines.get(machine_id)

    def contains_machine(self, machine_id):
        """
        Return whether the machine belongs to this fleet.
        """
        return machine_id in self._machines

    def find_by_hostname(self, hostname):
        """
        Find a fleet member by hostname.

        Returns None when no member has the supplied hostname.
        """
        for machine in self._machines.values():
            if machine.hostname == hostname:
                return machine

        return None