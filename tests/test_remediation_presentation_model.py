import pytest

from engine.remediation_presentation_model import RemediationPresentationModel


def test_requires_action_dictionary():
    with pytest.raises(ValueError):
        RemediationPresentationModel(None)


def test_safe_defaults():
    model = RemediationPresentationModel({})

    assert model.action_id() is None
    assert model.action_type() == "UNKNOWN"
    assert model.title() == "UNKNOWN"
    assert model.risk() == "UNKNOWN"
    assert model.authorization_status() == "UNAUTHORIZED"
    assert model.execution_status() == "NOT_EXECUTED"
    assert model.requires_authorization() is True
    assert model.has_executed() is False


def test_action_aliases_are_supported():
    model = RemediationPresentationModel(
        {
            "id": "memory-review-1",
            "type": "memory_review",
            "name": "Review memory pressure",
            "description": "Review processes consuming excessive memory.",
            "risk_level": "medium",
        }
    )

    assert model.action_id() == "memory-review-1"
    assert model.action_type() == "memory_review"
    assert model.title() == "Review memory pressure"
    assert model.explanation() == "Review processes consuming excessive memory."
    assert model.risk() == "MEDIUM"


def test_default_authorization_is_unauthorized():
    model = RemediationPresentationModel(
        {"action_id": "A1", "action_type": "memory_review"}
    )

    assert model.authorization_status() == "UNAUTHORIZED"
    assert model.requires_authorization() is True
    assert "requires your authorization" in model.user_message()


def test_authorized_action_is_ready_but_not_executed():
    model = RemediationPresentationModel(
        {
            "action_id": "A1",
            "action_type": "memory_review",
            "authorization_status": "AUTHORIZED",
            "execution_status": "NOT_EXECUTED",
        }
    )

    assert model.is_authorized() is True
    assert model.requires_authorization() is False
    assert model.has_executed() is False
    assert "ready" in model.user_message()


def test_denied_action_is_not_presented_as_executable():
    model = RemediationPresentationModel(
        {
            "action_id": "A1",
            "authorization_status": "DENIED",
            "execution_status": "NOT_EXECUTED",
        }
    )

    assert model.is_authorized() is False
    assert model.requires_authorization() is True
    assert "denied" in model.user_message()


def test_executed_action_is_reported_as_executed():
    model = RemediationPresentationModel(
        {
            "action_id": "A1",
            "authorization_status": "AUTHORIZED",
            "execution_status": "EXECUTED",
        }
    )

    assert model.has_executed() is True
    assert "already been executed" in model.user_message()


def test_failed_action_is_reported_as_failed():
    model = RemediationPresentationModel(
        {
            "action_id": "A1",
            "authorization_status": "AUTHORIZED",
            "execution_status": "FAILED",
        }
    )

    assert model.has_executed() is False
    assert "failed" in model.user_message()


def test_unknown_authorization_state_fails_safe():
    model = RemediationPresentationModel(
        {
            "authorization_status": "SOMETHING_UNKNOWN",
        }
    )

    assert model.authorization_status() == "UNAUTHORIZED"
    assert model.requires_authorization() is True


def test_unknown_execution_state_fails_safe():
    model = RemediationPresentationModel(
        {
            "execution_status": "SOMETHING_UNKNOWN",
        }
    )

    assert model.execution_status() == "NOT_EXECUTED"


def test_to_dict_contains_complete_presentation_surface():
    model = RemediationPresentationModel(
        {
            "action_id": "A1",
            "action_type": "memory_review",
            "title": "Review memory",
            "explanation": "Memory pressure is elevated.",
            "risk": "high",
            "authorization_status": "UNAUTHORIZED",
            "execution_status": "NOT_EXECUTED",
        }
    )

    result = model.to_dict()

    assert result == {
        "action_id": "A1",
        "action_type": "memory_review",
        "title": "Review memory",
        "explanation": "Memory pressure is elevated.",
        "risk": "HIGH",
        "authorization_status": "UNAUTHORIZED",
        "execution_status": "NOT_EXECUTED",
        "is_authorized": False,
        "has_executed": False,
        "requires_authorization": True,
        "user_message": "This remediation requires your authorization before it can be executed.",
    }


def test_input_is_defensively_copied():
    action = {
        "action_id": "A1",
        "title": "Original",
    }

    model = RemediationPresentationModel(action)
    action["title"] = "Changed"

    assert model.title() == "Original"


def test_output_is_independent():
    model = RemediationPresentationModel(
        {
            "action_id": "A1",
            "title": "Review memory",
        }
    )

    result = model.to_dict()
    result["title"] = "Changed"

    assert model.title() == "Review memory"


def test_model_has_no_execution_surface():
    forbidden = {
        "authorize",
        "execute",
        "remediate",
        "run",
        "retry",
        "verify",
    }

    public_methods = {
        name
        for name in dir(RemediationPresentationModel)
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(public_methods)
