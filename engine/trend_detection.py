from engine.health_baseline import HealthBaseline


class TrendDetector:

    def __init__(self, baseline):
        if not isinstance(baseline, HealthBaseline):
            raise ValueError(
                "TrendDetector requires a HealthBaseline."
            )

        self.baseline = baseline

    @property
    def machine_id(self):
        return self.baseline.machine_id

    @property
    def hostname(self):
        return self.baseline.hostname

    def detect(self):
        if len(self.baseline.samples) < 2:
            raise ValueError(
                "TrendDetector requires at least two samples."
            )

        keys = set()

        for sample in self.baseline.samples:
            keys.update(sample.keys())

        trends = {}

        for key in keys:
            values = [
                sample[key]
                for sample in self.baseline.samples
                if key in sample
            ]

            if len(values) < 2:
                continue

            if all(
                current > previous
                for previous, current in zip(values, values[1:])
            ):
                trends[key] = "INCREASING"
            elif all(
                current < previous
                for previous, current in zip(values, values[1:])
            ):
                trends[key] = "DECREASING"
            else:
                trends[key] = "STABLE"

        return trends