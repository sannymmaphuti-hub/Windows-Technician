# ==========================================
# Windows Technician v0.8
# REMOTE REMEDIATION EXECUTOR
# ==========================================

from engine.remote_remediation_context import (
    RemoteRemediationContext,
)
from engine.remediation_action import RemediationAction


class RemoteRemediationExecutor:

    def __init__(self, context):
        if not isinstance(
            context,
            RemoteRemediationContext,
        ):
            raise ValueError(
                "RemoteRemediationExecutor requires "
                "a RemoteRemediationContext."
            )

        self.context = context

    def execute(self, action):
        if not isinstance(
            action,
            RemediationAction,
        ):
            raise ValueError(
                "RemoteRemediationExecutor requires "
                "a RemediationAction."
            )

        if not self.context.machine.is_available:
            return False

        return action.execute()