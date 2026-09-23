class RemediationAudit:

    def __init__(self):
        self._records = []

    def record(
        self,
        action_id,
        execution_status,
        reason=None,
        verification_result=None,
    ):
        self._records.append(
            {
                "action_id": action_id,
                "execution_status": execution_status,
                "reason": reason,
                "verification_result": verification_result,
            }
        )

    def get_records(self):
        return list(self._records)
