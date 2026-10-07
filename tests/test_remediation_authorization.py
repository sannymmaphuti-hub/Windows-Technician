"""Tests for the production remediation authorization boundary."""

from dataclasses import FrozenInstanceError

import pytest

from packaging.remediation_authorization import (
    AuthorizationReason,
    AuthorizationState,
    RemediationAuthorization,
    authorize,
    authorization_allows_execution,
    deny,
    unauthorized,
)


def test_unauthorized_is_safe_default():
    authorization = unauthorized("action-001")

    assert authorization.state == AuthorizationState.UNAUTHORIZED
    assert authorization.reason == AuthorizationReason.NOT_REQUESTED
    assert not authorization_allows_execution(authorization)


def test_user_authorization_allows_execution():
    authorization = authorize("action-001")

    assert authorization.state == AuthorizationState.AUTHORIZED
    assert authorization.reason == AuthorizationReason.USER_APPROVED
    assert authorization_allows_execution(authorization)


def test_technician_authorization_allows_execution():
    authorization = authorize(
        "action-001",
        technician=True,
    )

    assert authorization.state == AuthorizationState.AUTHORIZED
    assert authorization.reason == AuthorizationReason.TECHNICIAN_APPROVED
    assert authorization_allows_execution(authorization)


def test_user_denial_blocks_execution():
    authorization = deny("action-001")

    assert authorization.state == AuthorizationState.DENIED
    assert authorization.reason == AuthorizationReason.USER_DENIED
    assert not authorization_allows_execution(authorization)


def test_technician_denial_blocks_execution():
    authorization = deny(
        "action-001",
        technician=True,
    )

    assert authorization.state == AuthorizationState.DENIED
    assert authorization.reason == AuthorizationReason.TECHNICIAN_DENIED
    assert not authorization_allows_execution(authorization)


@pytest.mark.parametrize(
    "state, reason",
    [
        (
            AuthorizationState.AUTHORIZED,
            AuthorizationReason.NOT_REQUESTED,
        ),
        (
            AuthorizationState.AUTHORIZED,
            AuthorizationReason.USER_DENIED,
        ),
        (
            AuthorizationState.AUTHORIZED,
            AuthorizationReason.TECHNICIAN_DENIED,
        ),
        (
            AuthorizationState.DENIED,
            AuthorizationReason.NOT_REQUESTED,
        ),
        (
            AuthorizationState.DENIED,
            AuthorizationReason.USER_APPROVED,
        ),
        (
            AuthorizationState.DENIED,
            AuthorizationReason.TECHNICIAN_APPROVED,
        ),
    ],
)
def test_invalid_state_reason_combinations_are_rejected(
    state,
    reason,
):
    with pytest.raises(ValueError):
        RemediationAuthorization(
            action_id="action-001",
            state=state,
            reason=reason,
        )


def test_empty_action_id_is_rejected():
    with pytest.raises(ValueError):
        unauthorized("")


def test_whitespace_action_id_is_rejected():
    with pytest.raises(ValueError):
        unauthorized("   ")


def test_invalid_state_type_is_rejected():
    with pytest.raises(TypeError):
        RemediationAuthorization(
            action_id="action-001",
            state="AUTHORIZED",
            reason=AuthorizationReason.USER_APPROVED,
        )


def test_invalid_reason_type_is_rejected():
    with pytest.raises(TypeError):
        RemediationAuthorization(
            action_id="action-001",
            state=AuthorizationState.AUTHORIZED,
            reason="USER_APPROVED",
        )


def test_unauthorized_reason_cannot_be_used_for_authorized_state():
    with pytest.raises(ValueError):
        RemediationAuthorization(
            action_id="action-001",
            state=AuthorizationState.AUTHORIZED,
            reason=AuthorizationReason.NOT_REQUESTED,
        )


def test_unauthorized_state_is_not_executable():
    authorization = RemediationAuthorization(
        action_id="action-001",
        state=AuthorizationState.UNAUTHORIZED,
        reason=AuthorizationReason.NOT_REQUESTED,
    )

    assert not authorization_allows_execution(authorization)


def test_denied_state_is_not_executable():
    authorization = RemediationAuthorization(
        action_id="action-001",
        state=AuthorizationState.DENIED,
        reason=AuthorizationReason.USER_DENIED,
    )

    assert not authorization_allows_execution(authorization)


def test_authorized_state_is_executable():
    authorization = RemediationAuthorization(
        action_id="action-001",
        state=AuthorizationState.AUTHORIZED,
        reason=AuthorizationReason.USER_APPROVED,
    )

    assert authorization_allows_execution(authorization)


def test_authorization_is_immutable():
    authorization = authorize("action-001")

    with pytest.raises(FrozenInstanceError):
        authorization.state = AuthorizationState.DENIED


def test_execution_gate_rejects_wrong_type():
    with pytest.raises(TypeError):
        authorization_allows_execution(object())
