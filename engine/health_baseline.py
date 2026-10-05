from engine.managed_machine import ManagedMachine


class HealthBaseline:

    def __init__(self, machine):
        if not isinstance(machine, ManagedMachine):
            raise ValueError(
                "HealthBaseline requires a ManagedMachine."
            )

        self.machine = machine
        self.samples = []

    @property
    def machine_id(self):
        return self.machine.machine_id

    @property
    def hostname(self):
        return self.machine.hostname

    def add_sample(self, sample):
        if not isinstance(sample, dict):
            raise ValueError(
                "HealthBaseline samples must be dictionaries."
            )

        self.samples.append(dict(sample))