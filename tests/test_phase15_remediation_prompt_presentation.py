import pytest

from ui.remediation_prompt_presentation import RemediationPromptPresentation


def test_unauthorized_action_is_presented_as_a_proposal():
    result = RemediationPromptPresentation().build({
        "action_id": "fix-1",
        "title": "Restart the affected service",
        "explanation": "The service is not responding.",
        "impact": "The service may be temporarily unavailable.",
    })

    assert result["authorization_status"] == "UNAUTHORIZED"
    assert result["execution_status"] == "NOT_EXECUTED"
    assert result["requires_user_authorization"] is True
    assert result["execution_performed_by_presentation"] is False


def test_authorization_does_not_change_execution_status():
    result = RemediationPromptPresentation().build({
        "action_id": "fix-2",
        "title": "Clear a temporary cache",
        "explanation": "The cache may contain stale data.",
        "authorization_status": "AUTHORIZED",
        "execution_status": "NOT_EXECUTED",
    })

    assert result["authorization_status"] == "AUTHORIZED"
    assert result["execution_status"] == "NOT_EXECUTED"


def test_denied_action_is_not_presented_as_authorized():
    result = RemediationPromptPresentation().build({
        "title": "Change a system setting",
        "explanation": "A setting may be contributing to the problem.",
        "authorization_status": "DENIED",
    })

    assert result["authorization_denied"] is True
    assert result["requires_user_authorization"] is False
    assert result["execution_status"] == "NOT_EXECUTED"


def test_executed_action_still_requires_verification():
    result = RemediationPromptPresentation().build({
        "title": "Restart a service",
        "explanation": "The service stopped responding.",
        "authorization_status": "AUTHORIZED",
        "execution_status": "EXECUTED",
    })

    assert result["execution_status"] == "EXECUTED"
    assert "verification" in result["execution_message"].lower()


def test_rejects_invalid_statuses_and_required_fields():
    presenter = RemediationPromptPresentation()

    with pytest.raises(ValueError, match="title"):
        presenter.build({"explanation": "An explanation"})

    with pytest.raises(ValueError, match="authorization_status"):
        presenter.build({
            "title": "Action",
            "explanation": "Reason",
            "authorization_status": "AUTO_APPROVED",
        })

    with pytest.raises(ValueError, match="execution_status"):
        presenter.build({
            "title": "Action",
            "explanation": "Reason",
            "execution_status": "AUTO_EXECUTE",
        })


def test_rejects_non_mapping_input():
    with pytest.raises(TypeError, match="mapping"):
        RemediationPromptPresentation().build(None)


def test_source_action_is_not_mutated():
    source = {
        "title": "Review startup applications",
        "explanation": "Several applications launch at startup.",
        "authorization_status": "unauthorized",
    }

    RemediationPromptPresentation().build(source)

    assert source["authorization_status"] == "unauthorized"
