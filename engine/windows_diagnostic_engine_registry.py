from engine.analyzer import Analyzer
from engine.network_diagnostic_pipeline import NetworkDiagnosticPipeline
from engine.windows_services_diagnostic import WindowsServicesDiagnostic
from engine.windows_storage_diagnostic import WindowsStorageDiagnostic
from engine.windows_startup_diagnostic import WindowsStartupDiagnostic
from engine.windows_system_diagnostic import WindowsSystemDiagnostic


class WindowsDiagnosticEngineRegistry:
    _ENGINES = {
        "PROCESS": Analyzer,
        "MEMORY": Analyzer,
        "NETWORK": NetworkDiagnosticPipeline,
        "STORAGE": WindowsStorageDiagnostic,
        "SERVICES": WindowsServicesDiagnostic,
        "STARTUP": WindowsStartupDiagnostic,
        "SYSTEM": WindowsSystemDiagnostic,
    }

    @classmethod
    def supported_domains(cls):
        return tuple(cls._ENGINES.keys())

    @classmethod
    def has_engine(cls, domain):
        normalized = cls._normalize_domain(domain)
        if normalized is None:
            return False
        return cls._ENGINES.get(normalized) is not None

    @classmethod
    def get_engine(cls, domain):
        normalized = cls._normalize_domain(domain)
        if normalized is None:
            return None
        return cls._ENGINES.get(normalized)

    @staticmethod
    def _normalize_domain(domain):
        if not isinstance(domain, str):
            return None

        normalized = domain.strip().upper()

        if not normalized:
            return None

        return normalized