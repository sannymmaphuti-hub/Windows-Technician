"""Production remediation authorization security boundary."""

from dataclasses import dataclass
from enum import Enum


class AuthorizationState(str, Enum):
    UNAUTHORIZED = "UNAUTHORIZED"
    AUTHORIZED = "AUTHORIZED"
    DENIED = "DENIED"


class AuthorizationReason(str, Enum):
    NOT_REQUESTED = "NOT_REQUESTED"
    USER_APPROVED = "USER_APPROVED"
    TECHNICIAN_APPROVED = "TECHNICIAN_APPROVED"
    USER_DENIED = "USER_DENIED"
    TECHNICIAN_DENIED = "TECHNICIAN_DENIED"
    INVALID_REQUEST = "INVALID_REQUEST"


@dataclass(frozen=True)
class RemediationAuthorization:
    """Immutable authorization decision for a remediation action."""

    action_id: str
    state: AuthorizationState
    reason: AuthorizationReason

    def __post_init__(self):
        if not isinstance(self.action_id, str) or not self.action_id.strip():
            raise ValueError("action_id must be a non-empty string.")

        if not isinstance(self.state, AuthorizationState):
            raise TypeError("state must be an AuthorizationState.")

        if not isinstance(self.reason, AuthorizationReason):
            raise TypeError("reason must be an AuthorizationReason.")

        if self.state == AuthorizationState.AUTHORIZED:
            if self.reason not in {
                AuthorizationReason.USER_APPROVED,
                AuthorizationReason.TECHNICIAN_APPROVED,
            }:
                raise ValueError(
                    "AUTHORIZED requires an explicit approval reason."
                )

        if self.state == AuthorizationState.DENIED:
            if self.reason not in {
                AuthorizationReason.USER_DENIED,
                AuthorizationReason.TECHNICIAN_DENIED,
                AuthorizationReason.INVALID_REQUEST,
            }:
                raise ValueError(
                    "DENIED requires a denial or invalid-request reason."
                )


def unauthorized(action_id: str) -> RemediationAuthorization:
    """Create the safe default authorization state."""

    return RemediationAuthorization(
        action_id=action_id,
        state=AuthorizationState.UNAUTHORIZED,
        reason=AuthorizationReason.NOT_REQUESTED,
    )


def authorize(
    action_id: str,
    *,
    technician: bool = False,
) -> RemediationAuthorization:
    """Create an explicit authorization decision."""

    return RemediationAuthorization(
        action_id=action_id,
        state=AuthorizationState.AUTHORIZED,
        reason=(
            AuthorizationReason.TECHNICIAN_APPROVED
            if technician
            else AuthorizationReason.USER_APPROVED
        ),
    )


def deny(
    action_id: str,
    *,
    technician: bool = False,
) -> RemediationAuthorization:
    """Create an explicit denial decision."""

    return RemediationAuthorization(
        action_id=action_id,
        state=AuthorizationState.DENIED,
        reason=(
            AuthorizationReason.TECHNICIAN_DENIED
            if technician
            else AuthorizationReason.USER_DENIED
        ),
    )


def authorization_allows_execution(
    authorization: RemediationAuthorization,
) -> bool:
    """Return whether execution is legally permitted by the boundary."""

    if not isinstance(
        authorization,
        RemediationAuthorization,
    ):
        raise TypeError(
            "authorization must be a RemediationAuthorization."
        )

    return authorization.state == AuthorizationState.AUTHORIZED
