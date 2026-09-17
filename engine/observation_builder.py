from engine.cpu_observation_builder import CPUObservationBuilder
from engine.memory_observation_builder import MemoryObservationBuilder
from engine.network_observation_builder import NetworkObservationBuilder


class ObservationBuilder:

    def __init__(self):
        self._builders = {
            "CPU": CPUObservationBuilder(),
            "MEMORY": MemoryObservationBuilder(),
            "NETWORK": NetworkObservationBuilder(),
        }

    def build(self, evidence):

        observations = []

        for category, builder in self._builders.items():

            category_evidence = evidence.get(category)

            if category_evidence is None:
                continue

            observations.extend(
                builder.build(category_evidence)
            )

        return observations