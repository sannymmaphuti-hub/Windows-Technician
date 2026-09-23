

class RootCauseSelection:

    def select(self, evaluations):

        if not isinstance(evaluations, list):
            raise ValueError(
                "Root cause evaluations must be a list."
            )

        strongly_supported = [
            evaluation
            for evaluation in evaluations
            if evaluation.assessment == "STRONGLY_SUPPORTED"
        ]

        if len(strongly_supported) == 1:
            return strongly_supported[0].candidate

        if len(strongly_supported) > 1:
            return None

        supported = [
            evaluation
            for evaluation in evaluations
            if evaluation.assessment == "SUPPORTED"
        ]

        if len(supported) == 1:
            return supported[0].candidate

        return None

