from engine.remediation_action_planner import RemediationActionPlanner
from engine.diagnostic_case import DiagnosticCase

def test_planner_can_be_created():
    planner = RemediationActionPlanner()

    assert planner is not None


def test_planner_returns_no_action_for_empty_recommendation():
    planner = RemediationActionPlanner()

    result = planner.create_action({})

    assert result is None


def test_planner_returns_no_action_when_recommendation_is_missing():
    planner = RemediationActionPlanner()

    result = planner.create_action(None)

    assert result is None


def test_planner_creates_action_from_supported_recommendation():
    planner = RemediationActionPlanner()

    recommendation = {
        "category": "memory",
        "severity": "WARNING",
        "recommendation": "Review memory-intensive processes.",
    }

    action = planner.create_action(recommendation)

    assert action is not None
    assert action.description == (
        "Review memory-intensive processes."
    )

def test_planner_preserves_recommendation_context():
    planner = RemediationActionPlanner()

    recommendation = {
        "category": "memory",
        "severity": "WARNING",
        "recommendation": "Review memory-intensive processes.",
    }

    action = planner.create_action(recommendation)

    assert action.category == "memory"
    assert action.severity == "WARNING"

def test_planner_does_not_create_action_for_non_actionable_recommendation():
    planner = RemediationActionPlanner()

    recommendation = {
        "category": "memory",
        "severity": "NORMAL",
        "recommendation": "Continue monitoring memory usage.",
    }

    action = planner.create_action(recommendation)

    assert action is None

def test_planner_creates_actions_for_multiple_recommendations():
    planner = RemediationActionPlanner()

    recommendations = [
        {
            "category": "memory",
            "severity": "WARNING",
            "recommendation": "Review memory-intensive processes.",
        },
        {
            "category": "storage",
            "severity": "NORMAL",
            "recommendation": "Continue monitoring storage usage.",
        },
        {
            "category": "cpu",
            "severity": "CRITICAL",
            "recommendation": "Investigate sustained CPU pressure.",
        },
    ]

    actions = planner.create_actions(recommendations)

    assert len(actions) == 2
    assert actions[0].category == "memory"
    assert actions[1].category == "cpu"

def test_planner_creates_actions_from_diagnostic_case():
    planner = RemediationActionPlanner()

    case = DiagnosticCase()

    case.set_recommendations(
        [
            {
                "category": "memory",
                "severity": "WARNING",
                "recommendation": "Review memory-intensive processes.",
            },
            {
                "category": "storage",
                "severity": "NORMAL",
                "recommendation": "Continue monitoring storage usage.",
            },
        ]
    )

    actions = planner.create_actions_from_case(case)

    assert len(actions) == 1
    assert actions[0].category == "memory"
    assert actions[0].severity == "WARNING"
    assert actions[0].description == (
        "Review memory-intensive processes."
    )

def test_planned_action_has_deterministic_id():
    planner = RemediationActionPlanner()

    recommendation = {
        "recommendation": "Review memory-intensive processes.",
        "category": "memory",
        "severity": "WARNING",
    }

    action_one = planner.create_action(recommendation)
    action_two = planner.create_action(recommendation)

    assert action_one.action_id
    assert action_one.action_id == action_two.action_id


def test_different_recommendations_have_different_action_ids():
    planner = RemediationActionPlanner()

    recommendation_one = {
        "recommendation": "Review memory-intensive processes.",
        "category": "memory",
        "severity": "WARNING",
    }

    recommendation_two = {
        "recommendation": "Check storage health.",
        "category": "storage",
        "severity": "CRITICAL",
    }

    action_one = planner.create_action(recommendation_one)
    action_two = planner.create_action(recommendation_two)

    assert action_one.action_id != action_two.action_id

def test_planner_created_action_starts_unauthorized_and_unexecuted():
    planner = RemediationActionPlanner()

    recommendation = {
        "recommendation": "Review memory-intensive processes.",
        "category": "memory",
        "severity": "WARNING",
    }

    action = planner.create_action(recommendation)

    assert action is not None
    assert action.authorization_status == "UNAUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

def test_planner_created_action_does_not_execute_during_planning():
    planner = RemediationActionPlanner()

    recommendation = {
        "recommendation": "Review memory-intensive processes.",
        "category": "memory",
        "severity": "WARNING",
    }

    action = planner.create_action(recommendation)

    assert action.execution_status == "NOT_EXECUTED"

def test_planner_created_action_can_be_authorized_without_execution():
    planner = RemediationActionPlanner()

    recommendation = {
        "recommendation": "Review memory-intensive processes.",
        "category": "memory",
        "severity": "WARNING",
    }

    action = planner.create_action(recommendation)

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

def test_planner_created_action_can_be_denied_and_remains_unexecuted():
    planner = RemediationActionPlanner()

    recommendation = {
        "recommendation": "Review memory-intensive processes.",
        "category": "memory",
        "severity": "WARNING",
    }

    action = planner.create_action(recommendation)

    action.deny()

    assert action.authorization_status == "DENIED"
    assert action.execution_status == "NOT_EXECUTED"
    assert action.execute() is False

def test_authorized_planner_action_can_execute():
    executed = []

    planner = RemediationActionPlanner()

    recommendation = {
        "recommendation": "Review memory-intensive processes.",
        "category": "memory",
        "severity": "WARNING",
    }

    action = planner.create_action(recommendation)

    action.operation = lambda: executed.append("run")

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    assert action.execute() is True

    assert executed == ["run"]
    assert action.execution_status == "EXECUTED"

def test_denied_planner_action_cannot_execute():
    executed = []

    planner = RemediationActionPlanner()

    recommendation = {
        "recommendation": "Review memory-intensive processes.",
        "category": "memory",
        "severity": "WARNING",
    }

    action = planner.create_action(recommendation)

    action.operation = lambda: executed.append("run")

    action.deny()

    assert action.authorization_status == "DENIED"
    assert action.execution_status == "NOT_EXECUTED"

    assert action.execute() is False

    assert executed == []
    assert action.execution_status == "NOT_EXECUTED"