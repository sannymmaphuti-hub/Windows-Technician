class RemediationOperationBinder:
    def __init__(self, registry):
        self.registry = registry

    def bind(self, action, operation_id):
        if action is None:
            raise ValueError("action is required")

        if operation_id is None:
            raise ValueError("operation_id is required")

        operation = self.registry.get(operation_id)

        if operation is None:
            raise ValueError(
                f"operation_id not registered: {operation_id}"
            )

        if action.operation is not None:
            if action.operation is operation:
                return

            raise ValueError("operation already bound")

        action.operation = operation