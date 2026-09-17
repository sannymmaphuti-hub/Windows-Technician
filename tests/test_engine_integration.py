# ==========================================
# Windows Technician v0.5
# ENGINE INTEGRATION TEST
# ==========================================

from engine.factory import create_diagnostic_engine


def test_production_engine_can_analyze_system():

    analyzer = create_diagnostic_engine()

    result = analyzer.analyze()

    assert "evidence" in result
    assert "diagnosis" in result


def test_production_engine_collects_all_domains():

    analyzer = create_diagnostic_engine()

    result = analyzer.analyze()

    evidence = result["evidence"]

    assert "CPU" in evidence
    assert "MEMORY" in evidence
    assert "STORAGE" in evidence
    assert "NETWORK" in evidence
    assert "GPU" in evidence


def test_production_engine_returns_valid_diagnosis():

    analyzer = create_diagnostic_engine()

    result = analyzer.analyze()

    diagnosis = result["diagnosis"]

    assert diagnosis["status"] in (
        "NORMAL",
        "WARNING",
        "CRITICAL"
    )

    assert isinstance(
        diagnosis["total_findings"],
        int
    )

    assert isinstance(
        diagnosis["findings"],
        list
    )

    assert isinstance(
        diagnosis["recommendations"],
        list
    )

def test_production_engine_info_finding_does_not_produce_info_status():

    analyzer = create_diagnostic_engine()

    info_finding = {
        "category": "TEST",
        "severity": "INFO",
        "message": "Informational test finding"
    }

    status = analyzer._calculate_overall_status(
        [info_finding]
    )

    assert status == "NORMAL"

