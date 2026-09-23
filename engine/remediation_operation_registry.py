class RemediationOperationRegistry:
    def __init__(self):
        self._operations = {}

    def register(self, operation_id, operation):
        if operation_id is None:
            raise ValueError("operation_id is required")

        if operation is None:
            raise ValueError("operation is required")

        if operation_id in self._operations:
            raise ValueError(
                f"operation_id already registered: {operation_id}"
            )

        self._operations[operation_id] = operation

    def get(self, operation_id):
        return self._operations.get(operation_id)
