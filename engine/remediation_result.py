class RemediationResult:
    def __init__(self, action_id):
        self.action_id = action_id
        self.execution_status = "NOT_EXECUTED"
        self.reason = None
        self.verification_result = None
