from engine.adaptive_diagnostic_loop import AdaptiveDiagnosticLoop
from engine.diagnostic_action_executor import DiagnosticActionExecutor
from engine.diagnostic_action_selector import DiagnosticActionSelector
from engine.network_decision_configuration import (
    create_network_decision_orchestrator,
)
from engine.network_diagnostic_operation_binding import (
    NetworkDiagnosticOperationBinding,
)


def create_network_adaptive_loop():
    decision_engine = create_network_decision_orchestrator()

    action_selector = DiagnosticActionSelector()

    executor = DiagnosticActionExecutor()

    NetworkDiagnosticOperationBinding().register(executor)

    return AdaptiveDiagnosticLoop(
        decision_engine=decision_engine,
        action_selector=action_selector,
        executor=executor,
    )


def test_network_adaptive_loop_can_be_created():
    loop = create_network_adaptive_loop()

    assert loop is not None


def test_network_adaptive_loop_accepts_partial_network_evidence():
    loop = create_network_adaptive_loop()

    result = loop.run(
        {
            "active_adapter": {
                "is_up": True,
            },
        }
    )

    assert result is not None


def test_network_adaptive_loop_returns_diagnostic_result():
    loop = create_network_adaptive_loop()

    result = loop.run(
        {
            "active_adapter": {
                "is_up": True,
            },
        }
    )

    assert hasattr(result, "evidence")
    assert hasattr(result, "decisions")
    assert hasattr(result, "actions")
    assert hasattr(result, "steps")
    assert hasattr(result, "stopped_reason")


def test_network_adaptive_loop_records_diagnostic_process():
    loop = create_network_adaptive_loop()

    result = loop.run(
        {
            "active_adapter": {
                "is_up": True,
            },
        }
    )

    assert result.steps >= 1
    assert len(result.decisions) == result.steps
    assert len(result.actions) == result.steps


def test_network_adaptive_loop_does_not_return_remediation():
    loop = create_network_adaptive_loop()

    result = loop.run(
        {
            "active_adapter": {
                "is_up": True,
            },
        }
    )

    result_data = result.to_dict()

    assert "remediation" not in result_data
    assert "remediation_actions" not in result_data
    assert "findings" not in result_data
    assert "root_causes" not in result_data
    assert "recommendations" not in result_data