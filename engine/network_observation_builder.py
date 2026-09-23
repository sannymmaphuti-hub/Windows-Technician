from engine.observation import Observation


class NetworkObservationBuilder:

    def build(self, evidence):

        observations = []

        active_adapter = evidence.get("active_adapter")

        if active_adapter is not None:

            observations.append(
                Observation(
                    source="network",
                    subject="network_adapter",
                    attribute="is_up",
                    value=active_adapter["is_up"]
                )
            )

            for address in active_adapter.get("addresses", []):

                if address.get("type") != "IPv4":
                    continue

                observations.append(
                    Observation(
                        source="network",
                        subject="network_adapter",
                        attribute="ipv4_address",
                        value=address["address"]
                    )
                )

                classification = address.get("classification")

                if classification is not None:

                    observations.append(
                        Observation(
                            source="network",
                            subject="network_adapter",
                            attribute="ipv4_classification",
                            value=classification
                        )
                    )

                break

        if "gateway" in evidence and evidence["gateway"] is not None:

            observations.append(
                Observation(
                    source="network",
                    subject="network_gateway",
                    attribute="address",
                    value=evidence["gateway"]
                )
            )

        if "gateway_reachable" in evidence:

            observations.append(
                Observation(
                    source="network",
                    subject="network_gateway",
                    attribute="reachable",
                    value=evidence["gateway_reachable"]
                )
            )

        if "internet_reachable" in evidence:

            observations.append(
                Observation(
                    source="network",
                    subject="network_internet",
                    attribute="reachable",
                    value=evidence["internet_reachable"]
                )
            )

        if "dns_working" in evidence:

            observations.append(
                Observation(
                    source="network",
                    subject="network_dns",
                    attribute="working",
                    value=evidence["dns_working"]
                )
            )

        return observations
