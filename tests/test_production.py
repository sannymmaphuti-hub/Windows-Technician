# ==========================================
# WINDOWS TECHNICIAN v0.1
# PRODUCTION ENGINE TEST
# ==========================================

from engine.production import run_diagnostics


def test_production_diagnostics_returns_result():

    result = run_diagnostics()

    assert isinstance(result, dict)

    assert "evidence" in result
    assert "diagnosis" in result


def test_production_diagnostics_returns_valid_status():

    result = run_diagnostics()

    diagnosis = result["diagnosis"]

    assert diagnosis["status"] in (
        "NORMAL",
        "WARNING",
        "CRITICAL"
    )


def test_production_diagnostics_returns_findings():

    result = run_diagnostics()

    diagnosis = result["diagnosis"]

    assert isinstance(
        diagnosis["findings"],
        list
    )

    assert isinstance(
        diagnosis["total_findings"],
        int
    )


def test_production_diagnostics_returns_recommendations():

    result = run_diagnostics()

    diagnosis = result["diagnosis"]

    assert isinstance(
        diagnosis["recommendations"],
        list
    )