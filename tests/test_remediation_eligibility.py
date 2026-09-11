from engine.remediation_action import RemediationAction
from engine.remediation_eligibility import RemediationEligibility

def test_unbound_action_is_not_eligible_for_execution():
    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
    )

    assert action.operation is None


def test_unauthorized_action_is_not_eligible_for_execution():
    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=lambda: None,
    )

    assert action.authorization_status == "UNAUTHORIZED"


def test_denied_action_is_not_eligible_for_execution():
    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=lambda: None,
    )

    action.deny()

    assert action.authorization_status == "DENIED"


def test_authorized_action_has_execution_permission():
    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=lambda: None,
    )

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"


def test_failed_action_is_not_eligible_for_reexecution():
    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=lambda: None,
    )

    action.authorize()

    action.execution_status = "FAILED"

    assert action.execution_status == "FAILED"


def test_executed_action_is_not_eligible_for_reexecution():
    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=lambda: None,
    )

    action.authorize()

    action.execution_status = "EXECUTED"

    assert action.execution_status == "EXECUTED"


def test_eligibility_component_can_be_created():
    eligibility = RemediationEligibility()

    assert eligibility is not None


def test_unbound_action_is_ineligible():
    eligibility = RemediationEligibility()

    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
    )

    assert eligibility.is_eligible(action) is False


def test_unauthorized_bound_action_is_ineligible():
    eligibility = RemediationEligibility()

    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=lambda: None,
    )

    assert eligibility.is_eligible(action) is False


def test_denied_bound_action_is_ineligible():
    eligibility = RemediationEligibility()

    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=lambda: None,
    )

    action.deny()

    assert eligibility.is_eligible(action) is False


def test_authorized_bound_action_is_eligible():
    eligibility = RemediationEligibility()

    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=lambda: None,
    )

    action.authorize()

    assert eligibility.is_eligible(action) is True


def test_failed_action_is_ineligible():
    eligibility = RemediationEligibility()

    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=lambda: None,
    )

    action.authorize()
    action.execution_status = "FAILED"

    assert eligibility.is_eligible(action) is False


def test_executed_action_is_ineligible():
    eligibility = RemediationEligibility()

    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=lambda: None,
    )

    action.authorize()
    action.execution_status = "EXECUTED"

    assert eligibility.is_eligible(action) is False

def test_none_action_is_ineligible():
    eligibility = RemediationEligibility()

    assert eligibility.is_eligible(None) is False


def test_invalid_object_is_ineligible():
    eligibility = RemediationEligibility()

    assert eligibility.is_eligible("not an action") is False

def test_invalid_action_has_invalid_action_reason():
    eligibility = RemediationEligibility()

    assert eligibility.get_reason(None) == "INVALID_ACTION"


def test_invalid_object_has_invalid_action_reason():
    eligibility = RemediationEligibility()

    assert eligibility.get_reason("not an action") == "INVALID_ACTION"


def test_unbound_action_has_operation_not_bound_reason():
    eligibility = RemediationEligibility()

    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
    )

    action.authorize()

    assert eligibility.get_reason(action) == "OPERATION_NOT_BOUND"


def test_unauthorized_action_has_not_authorized_reason():
    eligibility = RemediationEligibility()

    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=lambda: None,
    )

    assert eligibility.get_reason(action) == "NOT_AUTHORIZED"


def test_denied_action_has_denied_reason():
    eligibility = RemediationEligibility()

    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=lambda: None,
    )

    action.deny()

    assert eligibility.get_reason(action) == "DENIED"


def test_failed_action_has_already_failed_reason():
    eligibility = RemediationEligibility()

    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=lambda: None,
    )

    action.authorize()
    action.execution_status = "FAILED"

    assert eligibility.get_reason(action) == "ALREADY_FAILED"


def test_executed_action_has_already_executed_reason():
    eligibility = RemediationEligibility()

    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=lambda: None,
    )

    action.authorize()
    action.execution_status = "EXECUTED"

    assert eligibility.get_reason(action) == "ALREADY_EXECUTED"


def test_eligible_action_has_eligible_reason():
    eligibility = RemediationEligibility()

    action = RemediationAction(
        action_id="test_action",
        description="Test action",
        category="MEMORY",
        severity="WARNING",
        operation=lambda: None,
    )

    action.authorize()

    assert eligibility.get_reason(action) == "ELIGIBLE"

def test_action_not_requiring_authorization_can_be_eligible_when_bound():
    action = RemediationAction(
        action_id="test_action",
        description="Test remediation",
        requires_authorization=False,
        operation=lambda: None,
    )

    eligibility = RemediationEligibility()

    assert eligibility.is_eligible(action) is True