from engine.diagnostic_engine import DiagnosticEngine

from engine.rules.storage_rule import StorageFreeSpaceRule

from engine.recommendation_engine import RecommendationEngine

def test_engine_starts_empty():

    engine = DiagnosticEngine()

    assert engine.get_findings() == []


def test_engine_can_add_finding():

    engine = DiagnosticEngine()

    finding = {
        "category": "CPU",
        "severity": "WARNING",
        "message": "Elevated CPU utilization."
    }

    engine.add_finding(finding)

    assert len(engine.get_findings()) == 1
    assert engine.get_findings()[0] == finding


def test_engine_summary():

    engine = DiagnosticEngine()

    engine.add_finding({
        "category": "MEMORY",
        "severity": "WARNING",
        "message": "High memory usage."
    })

    summary = engine.get_summary()

    assert summary["total_findings"] == 1
    assert len(summary["findings"]) == 1


def test_engine_clear():

    engine = DiagnosticEngine()

    engine.add_finding({
        "category": "CPU",
        "severity": "WARNING",
        "message": "High CPU."
    })

    engine.clear_findings()

    assert engine.get_findings() == []

def test_engine_status_with_no_findings():

    engine = DiagnosticEngine()

    assert engine.get_overall_status() == "NORMAL"


def test_engine_status_warning():

    engine = DiagnosticEngine()

    engine.add_finding({
        "category": "CPU",
        "severity": "WARNING",
        "message": "Elevated CPU utilization."
    })

    assert engine.get_overall_status() == "WARNING"


def test_engine_status_critical():

    engine = DiagnosticEngine()

    engine.add_finding({
        "category": "MEMORY",
        "severity": "CRITICAL",
        "message": "Critically high memory usage."
    })

    assert engine.get_overall_status() == "CRITICAL"


def test_engine_status_uses_highest_severity():

    engine = DiagnosticEngine()

    engine.add_finding({
        "category": "CPU",
        "severity": "INFO",
        "message": "CPU operating normally."
    })

    engine.add_finding({
        "category": "MEMORY",
        "severity": "WARNING",
        "message": "High memory usage."
    })

    engine.add_finding({
        "category": "STORAGE",
        "severity": "CRITICAL",
        "message": "Storage health problem detected."
    })

    assert engine.get_overall_status() == "CRITICAL"

import pytest


def test_invalid_finding_type():

    engine = DiagnosticEngine()

    with pytest.raises(ValueError):
        engine.add_finding("invalid finding")


def test_missing_required_field():

    engine = DiagnosticEngine()

    finding = {
        "category": "CPU",
        "severity": "WARNING"
    }

    with pytest.raises(ValueError):
        engine.add_finding(finding)


def test_invalid_severity():

    engine = DiagnosticEngine()

    finding = {
        "category": "CPU",
        "severity": "BANANA",
        "message": "Invalid severity."
    }

    with pytest.raises(ValueError):
        engine.add_finding(finding)


def test_invalid_message_type():

    engine = DiagnosticEngine()

    finding = {
        "category": "CPU",
        "severity": "WARNING",
        "message": 123
    }

    with pytest.raises(ValueError):
        engine.add_finding(finding)

from engine.rules.cpu_rule import CPUUsageRule

def test_engine_starts_with_no_rules():

    engine = DiagnosticEngine()

    assert engine.rules == []


def test_engine_can_add_rule():

    engine = DiagnosticEngine()

    rule = CPUUsageRule()

    engine.add_rule(rule)

    assert len(engine.rules) == 1
    assert engine.rules[0] == rule


def test_engine_runs_rule_and_collects_finding():

    engine = DiagnosticEngine()

    rule = CPUUsageRule()

    engine.add_rule(rule)

    evidence = {
        "CPU": {
            "usage_percent": 90
        }
    }

    findings = engine.run_rules(evidence)

    assert len(findings) == 1
    assert findings[0]["category"] == "CPU"
    assert findings[0]["severity"] == "WARNING"


def test_engine_ignores_rule_with_no_finding():

    engine = DiagnosticEngine()

    rule = CPUUsageRule()

    engine.add_rule(rule)

    evidence = {
        "CPU": {
            "usage_percent": 40
        }
    }

    findings = engine.run_rules(evidence)

    assert findings == []


def test_engine_rejects_invalid_rule():

    engine = DiagnosticEngine()

    with pytest.raises(ValueError):

        engine.add_rule("not a rule")

from engine.rules.memory_rule import MemoryUsageRule

def test_engine_can_run_multiple_rules():

    engine = DiagnosticEngine()

    cpu_rule = CPUUsageRule()
    memory_rule = MemoryUsageRule()

    engine.add_rule(cpu_rule)
    engine.add_rule(memory_rule)

    evidence = {
        "CPU": {
            "usage_percent": 90
        },

        "MEMORY": {
            "usage_percent": 90
        }
    }

    findings = engine.run_rules(evidence)

    assert len(findings) == 2

    categories = {
        finding["category"]
        for finding in findings
    }

    assert "CPU" in categories
    assert "MEMORY" in categories

def test_engine_combined_rules_detect_critical_status():

    engine = DiagnosticEngine()

    cpu_rule = CPUUsageRule()
    memory_rule = MemoryUsageRule()

    engine.add_rule(cpu_rule)
    engine.add_rule(memory_rule)

    evidence = {
        "CPU": {
            "usage_percent": 97
        },

        "MEMORY": {
            "usage_percent": 97
        }
    }

    engine.run_rules(evidence)

    assert len(engine.get_findings()) == 2
    assert engine.get_overall_status() == "CRITICAL"

def test_engine_routes_evidence_by_rule_category():

    engine = DiagnosticEngine()

    cpu_rule = CPUUsageRule()
    memory_rule = MemoryUsageRule()

    engine.add_rule(cpu_rule)
    engine.add_rule(memory_rule)

    evidence = {
        "CPU": {
            "usage_percent": 90
        },

        "MEMORY": {
            "usage_percent": 40
        }
    }

    findings = engine.run_rules(evidence)

    assert len(findings) == 1
    assert findings[0]["category"] == "CPU"
    assert findings[0]["severity"] == "WARNING"

def test_engine_can_evaluate_cpu_memory_and_storage():

    engine = DiagnosticEngine()

    cpu_rule = CPUUsageRule()
    memory_rule = MemoryUsageRule()
    storage_rule = StorageFreeSpaceRule()

    engine.add_rule(cpu_rule)
    engine.add_rule(memory_rule)
    engine.add_rule(storage_rule)

    evidence = {
        "CPU": {
            "usage_percent": 90
        },

        "MEMORY": {
            "usage_percent": 85
        },

        "STORAGE": {
            "free_percent": 15
        }
    }

    findings = engine.run_rules(evidence)

    assert len(findings) == 3

    categories = {
        finding["category"]
        for finding in findings
    }

    assert "CPU" in categories
    assert "MEMORY" in categories
    assert "STORAGE" in categories

def test_engine_three_domains_detects_critical_status():

    engine = DiagnosticEngine()

    engine.add_rule(CPUUsageRule())
    engine.add_rule(MemoryUsageRule())
    engine.add_rule(StorageFreeSpaceRule())

    evidence = {
        "CPU": {
            "usage_percent": 85
        },

        "MEMORY": {
            "usage_percent": 88
        },

        "STORAGE": {
            "free_percent": 5
        }
    }

    engine.run_rules(evidence)

    assert len(engine.get_findings()) == 3

    assert engine.get_overall_status() == "CRITICAL"

def test_engine_three_domains_only_reports_problematic_domains():

    engine = DiagnosticEngine()

    engine.add_rule(CPUUsageRule())
    engine.add_rule(MemoryUsageRule())
    engine.add_rule(StorageFreeSpaceRule())

    evidence = {
        "CPU": {
            "usage_percent": 40
        },

        "MEMORY": {
            "usage_percent": 90
        },

        "STORAGE": {
            "free_percent": 40
        }
    }

    findings = engine.run_rules(evidence)

    assert len(findings) == 1

    assert findings[0]["category"] == "MEMORY"
    assert findings[0]["severity"] == "WARNING"

def test_engine_diagnose_returns_complete_result():

    engine = DiagnosticEngine()

    engine.add_rule(CPUUsageRule())
    engine.add_rule(MemoryUsageRule())
    engine.add_rule(StorageFreeSpaceRule())

    evidence = {
        "CPU": {
            "usage_percent": 90
        },

        "MEMORY": {
            "usage_percent": 85
        },

        "STORAGE": {
            "free_percent": 15
        }
    }

    result = engine.diagnose(evidence)

    assert result["status"] == "WARNING"
    assert result["total_findings"] == 3
    assert len(result["findings"]) == 3

def test_engine_diagnose_returns_critical_result():

    engine = DiagnosticEngine()

    engine.add_rule(CPUUsageRule())
    engine.add_rule(MemoryUsageRule())
    engine.add_rule(StorageFreeSpaceRule())

    evidence = {
        "CPU": {
            "usage_percent": 97
        },

        "MEMORY": {
            "usage_percent": 85
        },

        "STORAGE": {
            "free_percent": 30
        }
    }

    result = engine.diagnose(evidence)

    assert result["status"] == "CRITICAL"
    assert result["total_findings"] == 2

def test_engine_diagnose_clears_previous_findings():

    engine = DiagnosticEngine()

    engine.add_rule(CPUUsageRule())

    first_evidence = {
        "CPU": {
            "usage_percent": 95
        }
    }

    first_result = engine.diagnose(first_evidence)

    assert first_result["total_findings"] == 1
    assert first_result["status"] == "CRITICAL"

    second_evidence = {
        "CPU": {
            "usage_percent": 40
        }
    }

    second_result = engine.diagnose(second_evidence)

    assert second_result["total_findings"] == 0
    assert second_result["status"] == "NORMAL"

def test_engine_diagnose_includes_recommendations():

    recommendation_engine = RecommendationEngine()

    engine = DiagnosticEngine(
        recommendation_engine
    )

    engine.add_rule(CPUUsageRule())
    engine.add_rule(MemoryUsageRule())
    engine.add_rule(StorageFreeSpaceRule())

    evidence = {
        "CPU": {
            "usage_percent": 90
        },

        "MEMORY": {
            "usage_percent": 85
        },

        "STORAGE": {
            "free_percent": 15
        }
    }

    result = engine.diagnose(evidence)

    assert result["status"] == "WARNING"
    assert result["total_findings"] == 3

    assert len(
        result["recommendations"]
    ) == 3

def test_engine_diagnose_includes_critical_recommendation():

    recommendation_engine = RecommendationEngine()

    engine = DiagnosticEngine(
        recommendation_engine
    )

    engine.add_rule(CPUUsageRule())

    evidence = {
        "CPU": {
            "usage_percent": 97
        }
    }

    result = engine.diagnose(evidence)

    assert result["status"] == "CRITICAL"

    assert len(
        result["recommendations"]
    ) == 1

    assert (
        result["recommendations"][0]["category"]
        == "CPU"
    )

    assert (
        result["recommendations"][0]["severity"]
        == "CRITICAL"
    )

def test_engine_diagnose_normal_system_has_no_recommendations():

    recommendation_engine = RecommendationEngine()

    engine = DiagnosticEngine(
        recommendation_engine
    )

    engine.add_rule(CPUUsageRule())
    engine.add_rule(MemoryUsageRule())
    engine.add_rule(StorageFreeSpaceRule())

    evidence = {
        "CPU": {
            "usage_percent": 30
        },

        "MEMORY": {
            "usage_percent": 40
        },

        "STORAGE": {
            "free_percent": 50
        }
    }

    result = engine.diagnose(evidence)

    assert result["status"] == "NORMAL"
    assert result["total_findings"] == 0
    assert result["recommendations"] == []

def test_engine_accepts_valid_confidence():

    engine = DiagnosticEngine()

    finding = {
        "category": "CPU",
        "severity": "WARNING",
        "message": "Elevated CPU utilization.",
        "confidence": 0.85
    }

    engine.add_finding(finding)

    assert len(engine.get_findings()) == 1
    assert engine.get_findings()[0]["confidence"] == 0.85

def test_engine_rejects_confidence_above_one():

    engine = DiagnosticEngine()

    finding = {
        "category": "CPU",
        "severity": "CRITICAL",
        "message": "Critically high CPU utilization.",
        "confidence": 1.5
    }

    try:
        engine.add_finding(finding)
        assert False
    except ValueError:
        assert True

def test_engine_rejects_negative_confidence():

    engine = DiagnosticEngine()

    finding = {
        "category": "CPU",
        "severity": "WARNING",
        "message": "Elevated CPU utilization.",
        "confidence": -0.2
    }

    try:
        engine.add_finding(finding)
        assert False
    except ValueError:
        assert True

def test_engine_classifies_high_confidence():

    engine = DiagnosticEngine()

    finding = {
        "category": "CPU",
        "severity": "CRITICAL",
        "message": "Critically high CPU utilization.",
        "confidence": 0.95
    }

    engine.add_finding(finding)

    result = engine.get_findings()[0]

    assert result["confidence_level"] == "HIGH"

def test_engine_classifies_medium_confidence():

    engine = DiagnosticEngine()

    finding = {
        "category": "MEMORY",
        "severity": "WARNING",
        "message": "High memory usage.",
        "confidence": 0.65
    }

    engine.add_finding(finding)

    result = engine.get_findings()[0]

    assert result["confidence_level"] == "MEDIUM"

def test_engine_classifies_low_confidence():

    engine = DiagnosticEngine()

    finding = {
        "category": "STORAGE",
        "severity": "INFO",
        "message": "Storage activity detected.",
        "confidence": 0.30
    }

    engine.add_finding(finding)

    result = engine.get_findings()[0]

    assert result["confidence_level"] == "LOW"

def test_engine_allows_finding_without_confidence():

    engine = DiagnosticEngine()

    finding = {
        "category": "CPU",
        "severity": "INFO",
        "message": "CPU operating normally."
    }

    engine.add_finding(finding)

    result = engine.get_findings()[0]

    assert "confidence_level" not in result

def test_engine_accepts_multiple_findings_from_rule():

    class MultiFindingRule:

        category = "TEST"

        def evaluate(self, evidence):

            return [
                {
                    "category": "TEST",
                    "severity": "WARNING",
                    "message": "Finding one."
                },
                {
                    "category": "TEST",
                    "severity": "CRITICAL",
                    "message": "Finding two."
                }
            ]

    engine = DiagnosticEngine()

    engine.add_rule(
        MultiFindingRule()
    )

    result = engine.diagnose({
        "TEST": {}
    })

    assert result["total_findings"] == 2

    assert len(
        result["findings"]
    ) == 2


def test_engine_still_accepts_single_finding():

    class SingleFindingRule:

        category = "TEST"

        def evaluate(self, evidence):

            return {
                "category": "TEST",
                "severity": "INFO",
                "message": "Single finding."
            }

    engine = DiagnosticEngine()

    engine.add_rule(
        SingleFindingRule()
    )

    result = engine.diagnose({
        "TEST": {}
    })

    assert result["total_findings"] == 1
def test_engine_diagnose_accepts_external_findings():

    engine = DiagnosticEngine()

    external_finding = {
        "category": "PROCESS",
        "severity": "CRITICAL",
        "message": "chrome.exe is a significant CPU contributor.",
        "process": "chrome.exe",
        "pid": 1234
    }

    result = engine.diagnose(
        {},
        additional_findings=[
            external_finding
        ]
    )

    assert result["total_findings"] == 1
    assert result["findings"][0]["category"] == "PROCESS"
    assert result["status"] == "CRITICAL"

def test_engine_diagnose_result_contains_diagnostic_case_sections():

    engine = DiagnosticEngine()

    engine.add_rule(CPUUsageRule())

    evidence = {
        "CPU": {
            "usage_percent": 90
        }
    }

    result = engine.diagnose(evidence)

    assert "evidence" in result
    assert "findings" in result
    assert "correlations" in result
    assert "root_causes" in result
    assert "recommendations" in result
    assert "status" in result

def test_engine_diagnose_does_not_share_evidence_with_input():

    evidence = {
        "CPU": {
            "usage_percent": 90
        }
    }

    engine = DiagnosticEngine()

    engine.add_rule(CPUUsageRule())

    result = engine.diagnose(evidence)

    assert result["evidence"] == evidence
    assert result["evidence"] is not evidence
    assert result["evidence"]["CPU"] is not evidence["CPU"]

def test_engine_diagnose_does_not_share_nested_evidence_data():

    evidence = {
        "CPU": {
            "usage_percent": 90,
            "details": {
                "source": "system_monitor"
            }
        }
    }

    engine = DiagnosticEngine()

    engine.add_rule(CPUUsageRule())

    result = engine.diagnose(evidence)

    assert result["evidence"] == evidence

    assert (
        result["evidence"]["CPU"]
        is not evidence["CPU"]
    )

    assert (
        result["evidence"]["CPU"]["details"]
        is not evidence["CPU"]["details"]
    )

def test_engine_diagnose_does_not_share_findings_with_internal_state():

    engine = DiagnosticEngine()

    engine.add_rule(CPUUsageRule())

    evidence = {
        "CPU": {
            "usage_percent": 90
        }
    }

    result = engine.diagnose(evidence)

    assert result["findings"] == engine.get_findings()

    assert (
        result["findings"]
        is not engine.get_findings()
    )

def test_engine_diagnose_does_not_share_nested_finding_data():

    class NestedFindingRule:

        category = "CPU"

        def evaluate(self, evidence):

            return {
                "category": "CPU",
                "severity": "WARNING",
                "message": "CPU pressure detected.",
                "details": {
                    "source": "cpu_monitor",
                    "usage_percent": 90
                }
            }

    engine = DiagnosticEngine()

    engine.add_rule(
        NestedFindingRule()
    )

    result = engine.diagnose({
        "CPU": {
            "usage_percent": 90
        }
    })

    assert result["findings"] == engine.get_findings()

    assert (
        result["findings"][0]
        is not engine.get_findings()[0]
    )

    assert (
        result["findings"][0]["details"]
        is not engine.get_findings()[0]["details"]
    )

def test_engine_diagnose_does_not_share_recommendations_with_engine():

    class FakeRecommendationEngine:

        def get_recommendations(self, findings):

            return [
                {
                    "category": "CPU",
                    "severity": "WARNING",
                    "action": "Investigate CPU usage.",
                    "details": {
                        "source": "recommendation_engine"
                    }
                }
            ]

    recommendation_engine = FakeRecommendationEngine()

    engine = DiagnosticEngine(
        recommendation_engine
    )

    engine.add_rule(CPUUsageRule())

    result = engine.diagnose({
        "CPU": {
            "usage_percent": 90
        }
    })

    recommendations = (
        recommendation_engine.get_recommendations(
            engine.get_findings()
        )
    )

    assert result["recommendations"] == recommendations

    assert (
        result["recommendations"]
        is not recommendations
    )

    assert (
        result["recommendations"][0]
        is not recommendations[0]
    )

    assert (
        result["recommendations"][0]["details"]
        is not recommendations[0]["details"]
    )

def test_engine_diagnose_result_contains_empty_case_sections():

    engine = DiagnosticEngine()

    engine.add_rule(CPUUsageRule())

    result = engine.diagnose({
        "CPU": {
            "usage_percent": 90
        }
    })

    assert "correlations" in result
    assert "root_causes" in result

    assert result["correlations"] == []
    assert result["root_causes"] == []

def test_engine_diagnose_preserves_correlations_and_root_causes():

    engine = DiagnosticEngine()

    engine.add_rule(CPUUsageRule())

    evidence = {
        "CPU": {
            "usage_percent": 90
        }
    }

    correlation = {
        "type": "CPU_MEMORY",
        "strength": "HIGH",
        "message": "CPU and memory pressure are correlated."
    }

    root_cause = {
        "category": "SYSTEM",
        "severity": "WARNING",
        "message": "System resource pressure may be contributing to performance degradation."
    }

    result = engine.diagnose(
        evidence,
        correlations=[correlation],
        root_causes=[root_cause]
    )

    assert result["correlations"] == [correlation]
    assert result["root_causes"] == [root_cause]

def test_engine_diagnose_does_not_share_nested_correlation_or_root_cause_data():

    evidence = {
        "CPU": {
            "usage_percent": 90
        }
    }

    correlation = {
        "type": "CPU_MEMORY",
        "strength": "HIGH",
        "details": {
            "cpu": 90,
            "memory": 85
        }
    }

    root_cause = {
        "category": "SYSTEM",
        "severity": "WARNING",
        "message": "System resource pressure detected.",
        "details": {
            "source": "resource_analysis"
        }
    }

    engine = DiagnosticEngine()

    engine.add_rule(CPUUsageRule())

    result = engine.diagnose(
        evidence,
        correlations=[correlation],
        root_causes=[root_cause]
    )

    assert result["correlations"] == [correlation]
    assert result["root_causes"] == [root_cause]

    assert result["correlations"] is not [correlation]
    assert result["root_causes"] is not [root_cause]

    assert (
        result["correlations"][0]
        is not correlation
    )

    assert (
        result["root_causes"][0]
        is not root_cause
    )

    assert (
        result["correlations"][0]["details"]
        is not correlation["details"]
    )

    assert (
        result["root_causes"][0]["details"]
        is not root_cause["details"]
    )

def test_engine_analyze_preserves_correlations_and_root_causes():

    correlation = {
        "type": "CPU_MEMORY",
        "strength": "HIGH",
        "message": "CPU and memory pressure are correlated."
    }

    root_cause = {
        "category": "SYSTEM",
        "severity": "WARNING",
        "message": "System resource pressure may be contributing to degradation."
    }

    engine = DiagnosticEngine()

    engine.add_rule(CPUUsageRule())

    result = engine.analyze(
        {
            "CPU": {
                "usage_percent": 90
            }
        },
        correlations=[correlation],
        root_causes=[root_cause]
    )

    assert result["correlations"] == [correlation]
    assert result["root_causes"] == [root_cause]

def test_engine_diagnose_automatically_generates_correlations():

    from engine.correlation_engine import CorrelationEngine
    from engine.resource_contention_rule import ResourceContentionRule

    correlation_engine = CorrelationEngine()

    correlation_engine.register_rule(
        ResourceContentionRule()
    )

    engine = DiagnosticEngine(
        correlation_engine=correlation_engine
    )

    engine.add_rule(CPUUsageRule())
    engine.add_rule(MemoryUsageRule())

    evidence = {
        "CPU": {
            "usage_percent": 92
        },

        "MEMORY": {
            "usage_percent": 88
        }
    }

    result = engine.diagnose(evidence)

    assert len(result["correlations"]) == 1

    correlation = result["correlations"][0]

    assert (
        correlation.correlation_type
        == "RESOURCE_CONTENTION"
    )

    assert (
        correlation.strength
        == "MEDIUM"
    )
