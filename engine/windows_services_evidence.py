# ==========================================
# Windows Technician v0.9
# WINDOWS SERVICES EVIDENCE
# ==========================================

from copy import deepcopy


class WindowsServicesEvidence:
    """
    Immutable-style evidence container for Windows
    service observations.

    This class represents observed service information only.

    It does NOT:
    - start services
    - stop services
    - enable services
    - disable services
    - authorize remediation
    - execute remediation
    - create DiagnosticCase objects
    - manage technician workflow
    """

    def __init__(self, services=None):
        if services is None:
            services = []

        if not isinstance(services, list):
            raise ValueError(
                "services must be a list."
            )

        self.services = deepcopy(services)

    @property
    def service_count(self):
        return len(self.services)

    def get_service(self, name):
        if not isinstance(name, str):
            return None

        normalized_name = name.strip()

        if not normalized_name:
            return None

        for service in self.services:
            if not isinstance(service, dict):
                continue

            service_name = service.get("name")

            if not isinstance(service_name, str):
                continue

            if (
                service_name.strip().lower()
                == normalized_name.lower()
            ):
                return deepcopy(service)

        return None