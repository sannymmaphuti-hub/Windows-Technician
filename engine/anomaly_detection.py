from engine.baseline_comparison import BaselineComparison


class AnomalyDetector:

    DEFAULT_THRESHOLD = 10

    def __init__(self, comparison):
        if not isinstance(comparison, BaselineComparison):
            raise ValueError(
                "AnomalyDetector requires a BaselineComparison."
            )

        self.comparison = comparison

    @property
    def machine_id(self):
        return self.comparison.machine_id

    @property
    def hostname(self):
        return self.comparison.hostname

    def detect(self, current_sample):
        if not isinstance(current_sample, dict):
            raise ValueError(
                "AnomalyDetector requires a dictionary sample."
            )

        differences = self.comparison.compare(current_sample)

        return {
            key: abs(value) > self.DEFAULT_THRESHOLD
            for key, value in differences.items()
        }