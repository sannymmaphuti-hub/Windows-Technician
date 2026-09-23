# ==========================================
# WINDOWS TECHNICIAN v0.6
# DASHBOARD VIEW MODEL
# ==========================================

from copy import deepcopy


class DashboardViewModel:
    def __init__(self, diagnostic_view, execution_state="READY"):

        self.status = diagnostic_view.status
        self.execution_state = execution_state
        execution_state_map = {
            "READY": {
                "label": "Ready",
                "severity": "info"
            },
            "RUNNING": {
                "label": "Analyzing...",
                "severity": "info"
            },
            "COMPLETED": {
                "label": "Diagnostics Complete",
                "severity": "healthy"
            },
            "ERROR": {
                "label": "Diagnostic Failed",
                "severity": "critical"
            }
        }

        execution_display = execution_state_map.get(
            self.execution_state,
            {
                "label": "Unknown",
                "severity": "info"
            }
        )

        self.execution_label = execution_display["label"]
        self.execution_severity = execution_display["severity"]
        self.health_status = self.status

        if self.status == "NORMAL":
            self.health_label = "Healthy"
            self.health_severity = "healthy"
        elif self.status == "WARNING":
            self.health_label = "Needs Attention"
            self.health_severity = "warning"
        elif self.status == "CRITICAL":
            self.health_label = "Critical"
            self.health_severity = "critical"
        else:
            self.health_label = "Unknown"
            self.health_severity = "info"

        self.total_findings = diagnostic_view.total_findings
        self.findings = deepcopy(diagnostic_view.findings)

        if self.findings:
            self.primary_insight = max(
                self.findings,
                key=lambda finding: finding.get("priority_score", 0)
            )
        else:
            self.primary_insight = None

        self.correlations = deepcopy(diagnostic_view.correlations)

    

        self.root_causes = deepcopy(
            diagnostic_view.root_causes
        )

        self.remediation_actions = deepcopy(
            diagnostic_view.remediation_actions
        )

        self.remediation_audit = deepcopy(
            diagnostic_view.remediation_audit
        )

        self.recommendations = deepcopy(
            diagnostic_view.recommendations
        )
        self.network_diagnostic_case = deepcopy(
            diagnostic_view.network_diagnostic_case
        )

        self.network_case_explanation = deepcopy(
            diagnostic_view.network_case_explanation
        )

        if self.recommendations:
            priority_order = {
                "CRITICAL": 3,
                "HIGH": 2,
                "MEDIUM": 1,
                "LOW": 0
            }

            self.primary_recommendation = max(
                self.recommendations,
                key=lambda recommendation: priority_order.get(
                    recommendation.get("priority", "").upper(),
                    -1
                )
            )
        else:
            self.primary_recommendation = None

        self.primary_root_cause = deepcopy(
            diagnostic_view.primary_root_cause
        )

        self.warning_count = sum(
            1
            for finding in self.findings
            if finding.get("severity") == "WARNING"
        )

        self.info_count = sum(
            1
            for finding in self.findings
            if finding.get("severity") == "INFO"
        )

        evidence = diagnostic_view.evidence

        cpu = evidence.get("CPU", {})
        memory = evidence.get("MEMORY", {})
        storage = evidence.get("STORAGE", {})

        self.cpu_usage_percent = cpu.get(
            "usage_percent"
        )

        self.cpu_status = cpu.get(
            "status"
        )

        self.memory_usage_percent = memory.get(
            "usage_percent"
        )

        self.memory_total_gb = memory.get(
            "total_gb"
        )

        self.memory_used_gb = memory.get(
            "used_gb"
        )

        self.memory_available_gb = memory.get(
            "available_gb"
        )

        self.storage_devices = deepcopy(
            storage.get("devices", [])
        )
        if self.storage_devices:
            primary_storage = self.storage_devices[0]

            storage_usage_percent = primary_storage.get(
                "usage_percent"
            )
            storage_used_gb = primary_storage.get(
                "used_gb"
            )
            storage_total_gb = primary_storage.get(
                "total_gb"
            )
            storage_free_gb = primary_storage.get(
                "free_gb"
            )

            self.storage_usage_display = (
                f"{storage_usage_percent:.1f}%"
                if storage_usage_percent is not None
                else "N/A"
            )

            if (
                storage_used_gb is not None
                and storage_total_gb is not None
            ):
                self.storage_capacity_display = (
                    f"{storage_used_gb:.2f} GB / "
                    f"{storage_total_gb:.2f} GB"
                )
            else:
                self.storage_capacity_display = "N/A"

            self.storage_free_display = (
                f"{storage_free_gb:.2f} GB free"
                if storage_free_gb is not None
                else "N/A"
            )

        else:
            self.storage_usage_display = "N/A"
            self.storage_capacity_display = "N/A"
            self.storage_free_display = "N/A"
            
        self.cpu_usage_display = (
            f"{self.cpu_usage_percent:.1f}%"
            if self.cpu_usage_percent is not None
            else "N/A"
        )

        self.memory_usage_display = (
            f"{self.memory_usage_percent:.1f}%"
            if self.memory_usage_percent is not None
            else "N/A"
        )

        if (
            self.memory_used_gb is not None
            and self.memory_total_gb is not None
        ):
            self.memory_capacity_display = (
                f"{self.memory_used_gb:.2f} GB / "
                f"{self.memory_total_gb:.2f} GB"
            )
        else:
            self.memory_capacity_display = "N/A"
