from engine.diagnostic_case import DiagnosticCase
from engine.fleet import Fleet
from engine.system_level_investigation import SystemLevelInvestigation
from engine.system_level_recommendations import SystemLevelRecommendations
from engine.system_problem_relationships import SystemProblemRelationships
from engine.system_root_cause_reasoning import SystemRootCauseReasoning
from engine.system_wide_intelligence import SystemWideIntelligence
from engine.v1_0_platform import (
    V1CanonicalComponents,
    V1ProductionTechnicianPlatform,
)
from engine.windows_diagnostic_engine_registry import (
    WindowsDiagnosticEngineRegistry,
)
from packaging.remediation_authorization import RemediationAuthorization


def test_v1_platform_exposes_existing_canonical_components():
    platform = V1ProductionTechnicianPlatform()

    assert platform.components.diagnostic_case_type is DiagnosticCase
    assert (
        platform.components.diagnostic_registry_type
        is WindowsDiagnosticEngineRegistry
    )
    assert (
        platform.components.system_intelligence_type
        is SystemWideIntelligence
    )
    assert (
        platform.components.system_investigation_type
        is SystemLevelInvestigation
    )
    assert (
        platform.components.system_relationships_type
        is SystemProblemRelationships
    )
    assert (
        platform.components.system_root_cause_type
        is SystemRootCauseReasoning
    )
    assert (
        platform.components.system_recommendations_type
        is SystemLevelRecommendations
    )
    assert platform.components.fleet_type is Fleet
    assert (
        platform.components.remediation_authorization_type
        is RemediationAuthorization
    )


def test_v1_platform_instantiates_existing_intelligence_components():
    platform = V1ProductionTechnicianPlatform()

    assert isinstance(
        platform.system_intelligence,
        SystemWideIntelligence,
    )
    assert isinstance(
        platform.system_investigation,
        SystemLevelInvestigation,
    )
    assert isinstance(
        platform.system_relationships,
        SystemProblemRelationships,
    )
    assert isinstance(
        platform.system_root_cause,
        SystemRootCauseReasoning,
    )
    assert isinstance(
        platform.system_recommendations,
        SystemLevelRecommendations,
    )


def test_v1_platform_uses_existing_diagnostic_registry():
    platform = V1ProductionTechnicianPlatform()

    assert isinstance(
        platform.diagnostic_registry,
        WindowsDiagnosticEngineRegistry,
    )


def test_v1_platform_uses_existing_fleet_boundary():
    platform = V1ProductionTechnicianPlatform(
        fleet_name="V1 Production Fleet"
    )

    assert isinstance(platform.fleet, Fleet)
    assert platform.fleet.name == "V1 Production Fleet"


def test_v1_platform_creates_canonical_diagnostic_case():
    platform = V1ProductionTechnicianPlatform()

    case = platform.create_case()

    assert isinstance(case, DiagnosticCase)
    assert platform.canonical_case_type is DiagnosticCase


def test_v1_platform_does_not_create_a_second_case_type():
    platform = V1ProductionTechnicianPlatform()

    assert type(platform.create_case()) is DiagnosticCase


def test_v1_platform_preserves_remediation_authorization_boundary():
    platform = V1ProductionTechnicianPlatform()

    assert (
        platform.remediation_authorization_type
        is RemediationAuthorization
    )


def test_v1_canonical_components_are_declarative():
    components = V1CanonicalComponents()

    assert components.diagnostic_case_type is DiagnosticCase
    assert components.system_intelligence_type is SystemWideIntelligence
    assert components.system_root_cause_type is SystemRootCauseReasoning


def test_v1_platform_does_not_replace_existing_intelligence():
    platform = V1ProductionTechnicianPlatform()

    assert platform.system_intelligence.__class__ is SystemWideIntelligence
    assert platform.system_investigation.__class__ is SystemLevelInvestigation
    assert platform.system_relationships.__class__ is SystemProblemRelationships
    assert platform.system_root_cause.__class__ is SystemRootCauseReasoning
    assert (
        platform.system_recommendations.__class__
        is SystemLevelRecommendations
    )


def test_v1_platform_has_no_fleet_intelligence_duplicate():
    platform = V1ProductionTechnicianPlatform()

    assert not hasattr(platform, "fleet_intelligence")
    assert isinstance(platform.fleet, Fleet)


def test_v1_platform_components_have_expected_constructor_contracts():
    platform = V1ProductionTechnicianPlatform()

    assert callable(platform.components.diagnostic_case_type)
    assert callable(platform.components.diagnostic_registry_type)
    assert callable(platform.components.system_intelligence_type)
    assert callable(platform.components.system_investigation_type)
    assert callable(platform.components.system_relationships_type)
    assert callable(platform.components.system_root_cause_type)
    assert callable(platform.components.system_recommendations_type)
    assert callable(platform.components.fleet_type)
    assert callable(platform.components.remediation_authorization_type)


def test_v1_platform_default_fleet_name_is_stable():
    platform = V1ProductionTechnicianPlatform()

    assert platform.fleet.name == "Default Fleet"
