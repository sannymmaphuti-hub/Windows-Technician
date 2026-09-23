from engine.observation import Observation


class MemoryObservationBuilder:

    def build(self, evidence):

        observations = []

        metrics = (
            "total_gb",
            "used_gb",
            "available_gb",
            "usage_percent",
        )

        for attribute in metrics:

            if attribute in evidence:

                observations.append(
                    Observation(
                        source="memory",
                        subject="system_memory",
                        attribute=attribute,
                        value=evidence[attribute]
                    )
                )

        return observations
