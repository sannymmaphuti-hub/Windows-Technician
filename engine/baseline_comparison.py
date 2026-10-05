from engine.health_baseline import HealthBaseline


class BaselineComparison:

    def __init__(self, baseline):
        if not isinstance(baseline, HealthBaseline):
            raise ValueError(
                "BaselineComparison requires a HealthBaseline."
            )

        self.baseline = baseline

    @property
    def machine_id(self):
        return self.baseline.machine_id

    @property
    def hostname(self):
        return self.baseline.hostname

    def compare(self, current_sample):
        if not isinstance(current_sample, dict):
            raise ValueError(
                "BaselineComparison requires a dictionary sample."
            )

        if not self.baseline.samples:
            raise ValueError(
                "BaselineComparison requires an existing baseline sample."
            )

        baseline_sample = self.baseline.samples[-1]

        comparison = {}

        for key, current_value in current_sample.items():
            if key not in baseline_sample:
                continue

            comparison[key] = current_value - baseline_sample[key]

        return comparison