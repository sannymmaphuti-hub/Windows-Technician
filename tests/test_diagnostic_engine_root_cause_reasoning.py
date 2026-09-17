from engine.diagnostic_engine import DiagnosticEngine
from engine.root_cause_reasoning import RootCauseReasoning
from engine.root_cause_engine import RootCauseEngine
from engine.rules.memory_rule import MemoryUsageRule
from engine.root_cause_evaluation_engine import (
    RootCauseEvaluationEngine,
)
from engine.root_cause_evaluation_pipeline import (
    RootCauseEvaluationPipeline,
)
from engine.root_cause_selection import RootCauseSelection
from engine.memory_intensive_process_rule import (
    MemoryIntensiveProcessRule,
)
from engine.memory_leak_rule import MemoryLeakRule
from engine.memory_intensive_process_evaluation_rule import (
    MemoryIntensiveProcessEvaluationRule,
)
from engine.memory_leak_evaluation_rule import (
    MemoryLeakEvaluationRule,
)


def create_reasoning():

    candidate_engine = RootCauseEngine()

    candidate_engine.register_rule(
        MemoryIntensiveProcessRule()
    )

    candidate_engine.register_rule(
        MemoryLeakRule()
    )

    evaluation_engine = RootCauseEvaluationEngine()

    evaluation_engine.register_rule(
        MemoryIntensiveProcessEvaluationRule()
    )

    evaluation_engine.register_rule(
        MemoryLeakEvaluationRule()
    )

    evaluation_pipeline = RootCauseEvaluationPipeline(
        evaluation_engine=evaluation_engine
    )

    selection = RootCauseSelection()

    return RootCauseReasoning(
        candidate_engine=candidate_engine,
        evaluation_pipeline=evaluation_pipeline,
        selection=selection,
    )


def test_diagnostic_engine_accepts_root_cause_reasoning():

    reasoning = create_reasoning()

    engine = DiagnosticEngine(
        root_cause_reasoning=reasoning
    )

    assert engine.root_cause_reasoning is reasoning


def test_diagnostic_engine_can_run_root_cause_reasoning():

    reasoning = create_reasoning()

    engine = DiagnosticEngine(
        root_cause_reasoning=reasoning
    )

    evidence = {
        "MEMORY": {
            "usage_percent": 88,
        }
    }

    result = engine.diagnose(evidence)

    assert "root_cause_reasoning" in result


def test_diagnostic_engine_root_cause_reasoning_contains_evaluations():

    reasoning = create_reasoning()

    engine = DiagnosticEngine(
        root_cause_reasoning=reasoning
    )

    engine.add_rule(MemoryUsageRule())

    evidence = {
        "MEMORY": {
            "usage_percent": 88,
        }
    }

    result = engine.diagnose(evidence)

    root_cause_result = result["root_cause_reasoning"]

    assert "evaluations" in root_cause_result
    assert len(root_cause_result["evaluations"]) == 2

def test_diagnostic_engine_root_cause_reasoning_can_identify_primary_cause():

    reasoning = create_reasoning()

    engine = DiagnosticEngine(
        root_cause_reasoning=reasoning
    )

    result = engine.diagnose(
        {
            "MEMORY": {
                "usage_percent": 88,
            }
        }
    )

    root_cause_result = result["root_cause_reasoning"]

    assert root_cause_result["primary_cause"] is None


def test_diagnostic_engine_preserves_existing_diagnostic_output():

    reasoning = create_reasoning()

    engine = DiagnosticEngine(
        root_cause_reasoning=reasoning
    )

    evidence = {
        "MEMORY": {
            "usage_percent": 88,
        }
    }

    result = engine.diagnose(evidence)

    assert "findings" in result
    assert "recommendations" in result


def test_diagnostic_engine_works_without_root_cause_reasoning():

    engine = DiagnosticEngine()

    evidence = {
        "MEMORY": {
            "usage_percent": 88,
        }
    }

    result = engine.diagnose(evidence)

    assert "findings" in result
    assert "recommendations" in result
    assert "root_cause_reasoning" not in result


def test_diagnostic_engine_does_not_create_root_cause_reasoning_unless_configured():

    engine = DiagnosticEngine()

    evidence = {
        "MEMORY": {
            "usage_percent": 50,
        }
    }

    result = engine.diagnose(evidence)

    assert "root_cause_reasoning" not in result