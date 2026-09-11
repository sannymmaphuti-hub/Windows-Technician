# ==========================================
# WINDOWS TECHNICIAN v0.4
# DASHBOARD VIEW MODEL TESTS
# ==========================================

from application.diagnostic_view import DiagnosticView
from application.dashboard_view_model import DashboardViewModel



def make_dashboard_result():
    return {
        "evidence": {
            "CPU": {
                "usage_percent": 6.9,
                "frequency_mhz": 2208.0,
                "logical_processors": 4,
                "physical_cores": 2,
                "status": "NORMAL",
                "top_processes": []
            },
            "MEMORY": {
                "usage_percent": 82.4,
                "total_gb": 3.87,
                "used_gb": 3.19,
                "available_gb": 0.68
            },
            "STORAGE": {
                "devices": [
                    {
                        "device": "C:\\",
                        "usage_percent": 9.1,
                        "total_gb": 930.61,
                        "used_gb": 84.60,
                        "free_gb": 846.01
                    }
                ]
            }
        },
        "diagnosis": {
            "status": "WARNING",
            "total_findings": 2,
            "findings": [
                {
                    "category": "MEMORY",
                    "severity": "WARNING",
                    "issue": "High memory usage"
                },
                {
                    "category": "PROCESS",
                    "severity": "INFO",
                    "issue": "Normal process activity"
                }
            ],
            "correlations": [],
            "root_causes": [],
            "recommendations": [
                {
                    "action": "Close unnecessary applications",
                    "priority": "HIGH"
                }
            ]
        },
        "diagnostic_case": {
            "root_cause_candidates": [],
            "primary_root_cause": None,
            "process_intelligence": {},
            "memory_intelligence": {},
            "memory_history": [],
            "memory_trend_intelligence": {},
            "memory_temporal_intelligence": {},
            "memory_diagnostic_intelligence": {}
        },
        "case_decision": {}
    }


def test_dashboard_view_model_exposes_system_status():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(view)

    assert model.status == "WARNING"


def test_dashboard_view_model_exposes_finding_summary():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(view)

    assert model.total_findings == 2
    assert model.warning_count == 1
    assert model.info_count == 1


def test_dashboard_view_model_exposes_cpu_metrics():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(view)

    assert model.cpu_usage_percent == 6.9
    assert model.cpu_status == "NORMAL"


def test_dashboard_view_model_exposes_memory_metrics():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(view)

    assert model.memory_usage_percent == 82.4
    assert model.memory_total_gb == 3.87
    assert model.memory_used_gb == 3.19
    assert model.memory_available_gb == 0.68


def test_dashboard_view_model_exposes_storage_metrics():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(view)

    assert model.storage_devices == (
        make_dashboard_result()["evidence"]["STORAGE"]["devices"]
    )


def test_dashboard_view_model_exposes_diagnostic_information():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(view)

    assert model.findings == view.findings
    assert model.correlations == view.correlations
    assert model.root_causes == view.root_causes
    assert model.recommendations == view.recommendations
    assert model.primary_root_cause == view.primary_root_cause

def test_dashboard_view_model_handles_no_findings():
    result = make_dashboard_result()

    result["diagnosis"]["findings"] = []
    result["diagnosis"]["total_findings"] = 0

    view = DiagnosticView(result)
    view_model = DashboardViewModel(view)

    assert view_model.findings == []
    assert view_model.warning_count == 0
    assert view_model.info_count == 0


def test_dashboard_view_model_handles_empty_evidence():
    result = make_dashboard_result()

    result["evidence"] = {}

    view = DiagnosticView(result)
    view_model = DashboardViewModel(view)

    assert view_model.cpu_usage_percent is None
    assert view_model.cpu_status is None
    assert view_model.memory_usage_percent is None
    assert view_model.memory_total_gb is None
    assert view_model.memory_used_gb is None
    assert view_model.memory_available_gb is None
    assert view_model.storage_devices == []


def test_dashboard_view_model_handles_missing_diagnostic_information():
    result = make_dashboard_result()

    result["diagnosis"]["findings"] = []
    result["diagnosis"]["correlations"] = []
    result["diagnosis"]["root_causes"] = []
    result["diagnosis"]["recommendations"] = []

    result["diagnostic_case"]["primary_root_cause"] = None

    view = DiagnosticView(result)
    view_model = DashboardViewModel(view)

    assert view_model.findings == []
    assert view_model.correlations == []
    assert view_model.root_causes == []
    assert view_model.recommendations == []
    assert view_model.primary_root_cause is None

def test_dashboard_view_model_exposes_health_status():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(view)

    assert model.health_status == "WARNING"


def test_dashboard_view_model_exposes_health_label():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(view)

    assert model.health_label == "Needs Attention"


def test_dashboard_view_model_exposes_health_severity():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(view)

    assert model.health_severity == "warning"


def test_dashboard_view_model_maps_healthy_status():
    result = make_dashboard_result()
    result["diagnosis"]["status"] = "NORMAL"

    view = DiagnosticView(result)
    model = DashboardViewModel(view)

    assert model.health_status == "NORMAL"
    assert model.health_label == "Healthy"
    assert model.health_severity == "healthy"

def test_dashboard_view_model_exposes_primary_insight():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(view)

    assert model.primary_insight["category"] == "MEMORY"
    assert model.primary_insight["severity"] == "WARNING"
    assert model.primary_insight["issue"] == "High memory usage"


def test_dashboard_view_model_selects_highest_priority_finding():
    result = make_dashboard_result()

    result["diagnosis"]["findings"] = [
        {
            "category": "PROCESS",
            "severity": "INFO",
            "issue": "Normal process activity",
            "priority_score": 10
        },
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "issue": "High memory usage",
            "priority_score": 80
        }
    ]

    view = DiagnosticView(result)
    model = DashboardViewModel(view)

    assert model.primary_insight["category"] == "MEMORY"
    assert model.primary_insight["priority_score"] == 80


def test_dashboard_view_model_handles_no_primary_insight():
    result = make_dashboard_result()

    result["diagnosis"]["findings"] = []
    result["diagnosis"]["total_findings"] = 0

    view = DiagnosticView(result)
    model = DashboardViewModel(view)

    assert model.primary_insight is None

def test_dashboard_view_model_exposes_primary_recommendation():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(view)

    assert model.primary_recommendation["action"] == (
        "Close unnecessary applications"
    )
    assert model.primary_recommendation["priority"] == "HIGH"


def test_dashboard_view_model_selects_highest_priority_recommendation():
    result = make_dashboard_result()

    result["diagnosis"]["recommendations"] = [
        {
            "action": "Review running processes",
            "priority": "LOW"
        },
        {
            "action": "Close unnecessary applications",
            "priority": "HIGH"
        }
    ]

    view = DiagnosticView(result)
    model = DashboardViewModel(view)

    assert model.primary_recommendation["action"] == (
        "Close unnecessary applications"
    )
    assert model.primary_recommendation["priority"] == "HIGH"


def test_dashboard_view_model_handles_no_recommendations():
    result = make_dashboard_result()
    result["diagnosis"]["recommendations"] = []

    view = DiagnosticView(result)
    model = DashboardViewModel(view)

    assert model.primary_recommendation is None

def test_dashboard_view_model_exposes_memory_usage_display():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(view)

    assert model.memory_usage_display == "82.4%"


def test_dashboard_view_model_exposes_memory_capacity_display():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(view)

    assert model.memory_capacity_display == "3.19 GB / 3.87 GB"


def test_dashboard_view_model_exposes_cpu_usage_display():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(view)

    assert model.cpu_usage_display == "6.9%"

def test_dashboard_view_model_exposes_storage_usage_display():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(view)

    assert model.storage_usage_display == "9.1%"


def test_dashboard_view_model_exposes_storage_capacity_display():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(view)

    assert model.storage_capacity_display == "84.60 GB / 930.61 GB"


def test_dashboard_view_model_exposes_storage_free_display():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(view)

    assert model.storage_free_display == "846.01 GB free"


def test_dashboard_view_model_handles_no_storage_devices():
    result = make_dashboard_result()
    result["evidence"]["STORAGE"]["devices"] = []

    view = DiagnosticView(result)
    model = DashboardViewModel(view)

    assert model.storage_usage_display == "N/A"
    assert model.storage_capacity_display == "N/A"
    assert model.storage_free_display == "N/A"


def test_dashboard_view_model_exposes_execution_label():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(view)

    assert model.execution_label == "Ready"


def test_dashboard_view_model_exposes_execution_state():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(
        view,
        execution_state="READY"
    )

    assert model.execution_state == "READY"


def test_dashboard_view_model_maps_ready_execution_state():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(
        view,
        execution_state="READY"
    )

    assert model.execution_label == "Ready"
    assert model.execution_severity == "info"


def test_dashboard_view_model_maps_running_execution_state():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(
        view,
        execution_state="RUNNING"
    )

    assert model.execution_label == "Analyzing..."
    assert model.execution_severity == "info"


def test_dashboard_view_model_maps_completed_execution_state():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(
        view,
        execution_state="COMPLETED"
    )

    assert model.execution_label == "Diagnostics Complete"
    assert model.execution_severity == "healthy"


def test_dashboard_view_model_maps_error_execution_state():
    view = DiagnosticView(make_dashboard_result())
    model = DashboardViewModel(
        view,
        execution_state="ERROR"
    )

    assert model.execution_label == "Diagnostic Failed"
    assert model.execution_severity == "critical"

def test_dashboard_view_model_exposes_remediation_audit():
    result = {
        "diagnosis": {
            "status": "NORMAL",
            "total_findings": 0,
            "findings": [],
            "correlations": [],
            "root_causes": [],
            "recommendations": [],
        },
        "diagnostic_case": {
            "root_cause_candidates": [],
            "primary_root_cause": None,
        },
        "case_decision": {},
        "remediation_audit": [
            {
                "action_id": "action_001",
                "execution_status": "EXECUTED",
                "reason": None,
                "verification_result": None,
            }
        ],
    }

    diagnostic_view = DiagnosticView(result)

    dashboard_view_model = DashboardViewModel(
        diagnostic_view,
        execution_state="COMPLETED",
    )

    assert dashboard_view_model.remediation_audit == [
        {
            "action_id": "action_001",
            "execution_status": "EXECUTED",
            "reason": None,
            "verification_result": None,
        }
    ]

def test_dashboard_view_model_starts_with_empty_remediation_audit():
    result = {
        "diagnosis": {
            "status": "NORMAL",
            "total_findings": 0,
            "findings": [],
            "correlations": [],
            "root_causes": [],
            "recommendations": [],
        },
        "diagnostic_case": {
            "root_cause_candidates": [],
            "primary_root_cause": None,
        },
        "case_decision": {},
    }

    diagnostic_view = DiagnosticView(result)

    dashboard_view_model = DashboardViewModel(
        diagnostic_view,
        execution_state="COMPLETED",
    )

    assert dashboard_view_model.remediation_audit == []

def test_dashboard_view_model_exposes_diagnostic_view_remediation_audit():
    result = {
        "diagnosis": {
            "status": "NORMAL",
            "total_findings": 0,
            "findings": [],
            "correlations": [],
            "root_causes": [],
            "recommendations": [],
        },
        "diagnostic_case": {
            "root_cause_candidates": [],
            "primary_root_cause": None,
        },
        "case_decision": {},
        "remediation_audit": [
            {
                "action_id": "action_001",
                "execution_status": "EXECUTED",
                "reason": None,
                "verification_result": None,
            }
        ],
    }

    diagnostic_view = DiagnosticView(result)

    dashboard_view_model = DashboardViewModel(
        diagnostic_view,
        execution_state="COMPLETED",
    )

    assert dashboard_view_model.remediation_audit == [
        {
            "action_id": "action_001",
            "execution_status": "EXECUTED",
            "reason": None,
            "verification_result": None,
        }
    ]