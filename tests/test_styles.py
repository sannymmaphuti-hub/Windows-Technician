from gui.styles import APPLICATION_STYLE


def test_application_style_contains_semantic_severity_states():
    assert "statusSeverity" in APPLICATION_STYLE

    assert "healthy" in APPLICATION_STYLE
    assert "warning" in APPLICATION_STYLE
    assert "critical" in APPLICATION_STYLE
    assert "info" in APPLICATION_STYLE

def test_application_style_contains_dashboard_surface_states():
    assert "DashboardHeader" in APPLICATION_STYLE
    assert "HealthSummary" in APPLICATION_STYLE
    assert "DiagnosticContent" in APPLICATION_STYLE