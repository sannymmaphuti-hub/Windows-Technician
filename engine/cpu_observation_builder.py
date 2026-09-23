from engine.observation import Observation


class CPUObservationBuilder:

    def build(self, evidence):

        observations = []

        metrics = (
            "physical_cores",
            "logical_processors",
            "usage_percent",
            "frequency_mhz",
        )

        for attribute in metrics:

            if attribute in evidence:

                observations.append(
                    Observation(
                        source="cpu",
                        subject="system_cpu",
                        attribute=attribute,
                        value=evidence[attribute]
                    )
                )

        return observations
