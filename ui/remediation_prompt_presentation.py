"""User-facing remediation prompts with explicit authorization boundaries."""
from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any


class RemediationPromptPresentation:
    """Present remediation proposals without authorizing or executing them."""

    SCHEMA_VERSION = "1.0"

    _AUTHORIZATION_MESSAGES = {
        "UNAUTHORIZED": "This action has not been authorized.",
        "AUTHORIZED": "This action has been authorized.",
        "DENIED": "Authorization for this action was denied.",
    }

    _EXECUTION_MESSAGES = {
        "NOT_EXECUTED": "No changes have been made by this action.",
        "EXECUTED": "The action has been executed; verification may still be required.",
        "FAILED": "The action failed; its outcome should be investigated.",
    }

    def build(self, action: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(action, Mapping):
            raise TypeError("action must be a mapping")

        source = deepcopy(dict(action))

        action_id = source.get("action_id", "")
        title = source.get("title", source.get("name", ""))
        explanation = source.get("explanation", source.get("reason", ""))
        impact = source.get("impact", "Not specified")
        authorization = source.get("authorization_status", "UNAUTHORIZED")
        execution = source.get("execution_status", "NOT_EXECUTED")

        for field, value in (
            ("action_id", action_id),
            ("title", title),
            ("explanation", explanation),
            ("impact", impact),
        ):
            if not isinstance(value, str):
                raise TypeError(f"{field} must be a string")

        if not title.strip():
            raise ValueError("title must be a non-empty string")

        if not explanation.strip():
            raise ValueError("explanation must be a non-empty string")

        if not impact.strip():
            impact = "Not specified"

        if not isinstance(authorization, str):
            raise TypeError("authorization_status must be a string")

        if not isinstance(execution, str):
            raise TypeError("execution_status must be a string")

        authorization = authorization.strip().upper()
        execution = execution.strip().upper()

        if authorization not in self._AUTHORIZATION_MESSAGES:
            raise ValueError("unsupported authorization_status")

        if execution not in self._EXECUTION_MESSAGES:
            raise ValueError("unsupported execution_status")

        return {
            "schema_version": self.SCHEMA_VERSION,
            "action_id": action_id,
            "title": title.strip(),
            "explanation": explanation.strip(),
            "impact": impact.strip(),
            "authorization_status": authorization,
            "authorization_message": self._AUTHORIZATION_MESSAGES[authorization],
            "execution_status": execution,
            "execution_message": self._EXECUTION_MESSAGES[execution],
            "requires_user_authorization": authorization == "UNAUTHORIZED",
            "authorization_denied": authorization == "DENIED",
            "execution_performed_by_presentation": False,
        }
