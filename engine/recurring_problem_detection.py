from engine.health_baseline import HealthBaseline


class RecurringProblemDetector:

    def __init__(self, baseline):
        if not isinstance(baseline, HealthBaseline):
            raise ValueError(
                "RecurringProblemDetector requires a HealthBaseline."
            )

        self.baseline = baseline

    @property
    def machine_id(self):
        return self.baseline.machine_id

    @property
    def hostname(self):
        return self.baseline.hostname

    def detect(self, threshold, minimum_occurrences):
        if not isinstance(threshold, (int, float)):
            raise ValueError(
                "threshold must be numeric."
            )

        if not isinstance(minimum_occurrences, int):
            raise ValueError(
                "minimum_occurrences must be an integer."
            )

        if minimum_occurrences <= 0:
            raise ValueError(
                "minimum_occurrences must be greater than zero."
            )

        results = {}

        keys = set()

        for sample in self.baseline.samples:
            keys.update(sample.keys())

        for key in keys:
            values = [
                sample[key]
                for sample in self.baseline.samples
                if key in sample
            ]

            occurrences = sum(
                value >= threshold
                for value in values
            )

            results[key] = occurrences >= minimum_occurrences

        return results