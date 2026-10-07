import pytest

from engine.diagnostic_card_model import DiagnosticCardModel


def test_requires_dictionary():
    with pytest.raises(ValueError):
        DiagnosticCardModel(None)


def test_requires_dictionary_type():
    with pytest.raises(ValueError):
        DiagnosticCardModel("finding")


def test_empty_finding_has_safe_defaults():
    card = DiagnosticCardModel({})

    assert card.identifier() is None
    assert card.severity() == "UNKNOWN"
    assert card.category() == "SYSTEM"
    assert card.title() == "Diagnostic finding"
    assert card.explanation() == "No explanation available."
    assert card.evidence() == []
    assert card.next_step() == "Review this finding."


def test_reads_standard_finding_fields():
    card = DiagnosticCardModel(
        {
            "finding_id": "FINDING-001",
            "severity": "HIGH",
            "category": "MEMORY",
            "title": "High memory pressure",
            "explanation": "Available memory is low.",
            "evidence": [
                {"metric": "memory_percent", "value": 88},
            ],
            "next_step": "Review memory-intensive applications.",
        }
    )

    assert card.identifier() == "FINDING-001"
    assert card.severity() == "HIGH"
    assert card.category() == "MEMORY"
    assert card.title() == "High memory pressure"
    assert card.explanation() == "Available memory is low."
    assert card.evidence() == [
        {"metric": "memory_percent", "value": 88},
    ]
    assert card.next_step() == "Review memory-intensive applications."


def test_normalizes_severity():
    card = DiagnosticCardModel({"severity": "high"})

    assert card.severity() == "HIGH"


def test_supports_level_alias():
    card = DiagnosticCardModel({"level": "warning"})

    assert card.severity() == "WARNING"


def test_supports_title_aliases():
    assert DiagnosticCardModel({"name": "Memory issue"}).title() == (
        "Memory issue"
    )

    assert DiagnosticCardModel({"summary": "Startup issue"}).title() == (
        "Startup issue"
    )


def test_supports_explanation_aliases():
    assert DiagnosticCardModel(
        {"description": "The system is under pressure."}
    ).explanation() == "The system is under pressure."


def test_supports_evidence_aliases():
    card = DiagnosticCardModel(
        {
            "observations": [
                {"cpu": 95},
                {"memory": 90},
            ]
        }
    )

    assert len(card.evidence()) == 2


def test_supports_recommendation_aliases():
    card = DiagnosticCardModel(
        {
            "recommendation": "Review startup applications."
        }
    )

    assert card.next_step() == "Review startup applications."


def test_supports_category_aliases():
    card = DiagnosticCardModel({"domain": "PROCESS"})

    assert card.category() == "PROCESS"


def test_evidence_scalar_becomes_list():
    card = DiagnosticCardModel(
        {
            "evidence": "Memory usage reached 88%."
        }
    )

    assert card.evidence() == ["Memory usage reached 88%."]


def test_defensive_copy_of_evidence():
    source = {
        "evidence": [
            {"value": 88},
        ]
    }

    card = DiagnosticCardModel(source)

    evidence = card.evidence()
    evidence[0]["value"] = 100

    assert card.evidence()[0]["value"] == 88


def test_defensive_copy_of_source():
    source = {
        "title": "Memory pressure",
    }

    card = DiagnosticCardModel(source)

    source["title"] = "Changed"

    assert card.title() == "Memory pressure"


def test_to_dict_returns_complete_presentation_surface():
    card = DiagnosticCardModel(
        {
            "finding_id": "F-1",
            "severity": "CRITICAL",
            "category": "STORAGE",
            "title": "Disk pressure",
            "explanation": "Storage is nearly full.",
            "evidence": [{"free_percent": 3}],
            "next_step": "Review storage usage.",
        }
    )

    result = card.to_dict()

    assert result == {
        "finding_id": "F-1",
        "severity": "CRITICAL",
        "category": "STORAGE",
        "title": "Disk pressure",
        "explanation": "Storage is nearly full.",
        "evidence": [{"free_percent": 3}],
        "next_step": "Review storage usage.",
    }


def test_to_dict_is_defensive():
    card = DiagnosticCardModel(
        {
            "title": "Memory pressure",
            "evidence": [{"value": 88}],
        }
    )

    result = card.to_dict()

    result["evidence"][0]["value"] = 100

    assert card.evidence()[0]["value"] == 88


def test_presentation_model_has_no_execution_surface():
    declared_names = set(DiagnosticCardModel.__dict__)

    forbidden = (
        "diagnose",
        "analyze",
        "recommend",
        "remediate",
        "execute",
        "authorize",
    )

    for name in forbidden:
        assert not any(
            name in attribute.lower()
            for attribute in declared_names
        )
