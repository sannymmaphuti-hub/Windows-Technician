from engine.v1_0_architecture import (
    V1ArchitectureBoundary,
    V1ArchitectureLayer,
    V1_ARCHITECTURE,
    V1ArchitectureDefinition,
)


def test_v1_architecture_has_canonical_identity():
    architecture = V1_ARCHITECTURE

    assert isinstance(architecture, V1ArchitectureDefinition)
    assert architecture.name == "Windows Technician V1.0"
    assert architecture.product_type == "production_technician_platform"
    assert architecture.architecture_version == "1.0"


def test_v1_architecture_contains_complete_production_flow():
    layers = V1_ARCHITECTURE.layers

    assert layers == (
        V1ArchitectureLayer.CAPABILITY,
        V1ArchitectureLayer.EVIDENCE,
        V1ArchitectureLayer.INTELLIGENCE,
        V1ArchitectureLayer.INVESTIGATION,
        V1ArchitectureLayer.CASE,
        V1ArchitectureLayer.DECISION,
        V1ArchitectureLayer.REMEDIATION,
        V1ArchitectureLayer.VERIFICATION,
        V1ArchitectureLayer.HISTORY,
    )


def test_v1_architecture_preserves_security_boundaries():
    boundaries = V1_ARCHITECTURE.boundaries

    assert V1ArchitectureBoundary.UI_PRESENTATION in boundaries
    assert V1ArchitectureBoundary.AUTHORIZATION in boundaries
    assert V1ArchitectureBoundary.EXECUTION in boundaries
    assert V1ArchitectureBoundary.VERIFICATION in boundaries


def test_v1_architecture_uses_diagnostic_case_as_canonical_container():
    assert V1_ARCHITECTURE.canonical_case_type == "DiagnosticCase"
    assert V1_ARCHITECTURE.case_is_canonical_investigation_container


def test_v1_architecture_intelligence_consumes_system_evidence():
    assert "observations" in V1_ARCHITECTURE.intelligence_inputs
    assert "signals" in V1_ARCHITECTURE.intelligence_inputs
    assert "evidence" in V1_ARCHITECTURE.intelligence_inputs
    assert "correlations" in V1_ARCHITECTURE.intelligence_inputs
    assert "historical_context" in V1_ARCHITECTURE.intelligence_inputs
    assert "fleet_context" in V1_ARCHITECTURE.intelligence_inputs


def test_v1_architecture_intelligence_produces_reasoned_outputs():
    outputs = V1_ARCHITECTURE.intelligence_outputs

    assert "findings" in outputs
    assert "relationships" in outputs
    assert "root_causes" in outputs
    assert "explanations" in outputs
    assert "recommendations" in outputs


def test_v1_architecture_remediation_chain_is_explicit():
    assert V1_ARCHITECTURE.remediation_chain == (
        "eligibility",
        "decision",
        "authorization",
        "execution",
        "verification",
        "recovery",
    )


def test_v1_architecture_forbids_intelligence_execution():
    assert V1_ARCHITECTURE.intelligence_must_not_execute


def test_v1_architecture_forbids_ui_decision_making():
    assert V1_ARCHITECTURE.ui_must_not_decide


def test_v1_architecture_separates_recommendation_from_authorization():
    assert V1_ARCHITECTURE.recommendation_is_not_authorization


def test_v1_architecture_separates_execution_from_verification():
    assert V1_ARCHITECTURE.execution_is_not_verification


def test_v1_architecture_does_not_treat_failure_as_retry_authorization():
    assert V1_ARCHITECTURE.failure_is_not_retry_authorization
