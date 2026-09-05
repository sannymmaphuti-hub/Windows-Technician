import pytest

from application.diagnostic_view import DiagnosticView
from application.dashboard_view_model import DashboardViewModel


@pytest.fixture
def dashboard_view_model():
    result = {
        "evidence": {
            "CPU": {
                "usage_percent": 25.0,
                "status": "NORMAL",
            },
            "MEMORY": {
                "usage_percent": 40.0,
                "total_gb": 16.0,
                "used_gb": 6.4,
                "available_gb": 9.6,
            },
            "STORAGE": {
                "devices": [
                    {
                        "usage_percent": 50.0,
                        "used_gb": 250.0,
                        "total_gb": 500.0,
                        "free_gb": 250.0,
                    }
                ]
            },
        },
        "diagnosis": {
            "status": "NORMAL",
            "total_findings": 1,
            "findings": [
                {
                    "issue": "Memory usage is within normal limits.",
                    "severity": "INFO",
                    "priority_score": 10,
                }
            ],
            "correlations": [],
            "root_causes": [],
            "recommendations": [
                {
                    "recommendation": (
                        "Close unnecessary background applications."
                    ),
                    "priority": "LOW",
                }
            ],
        },
        "diagnostic_case": {
            "root_cause_candidates": [],
            "primary_root_cause": None,
        },
        "case_decision": {},
    }

    diagnostic_view = DiagnosticView(result)

    return DashboardViewModel(
        diagnostic_view,
        execution_state="COMPLETED",
    )