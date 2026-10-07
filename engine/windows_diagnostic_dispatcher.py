from engine.windows_diagnostic_capability import (
    WindowsDiagnosticCapability,
)
from engine.windows_diagnostic_execution_adapter import (
    WindowsDiagnosticExecutionAdapter,
)


_UNSET = object()


class WindowsDiagnosticDispatcher:
    _EVIDENCE_AWARE_DOMAINS = {
        "NETWORK",
        "STORAGE",
        "SERVICES",
        "STARTUP",
        "SYSTEM",
    }

    def __init__(self):
        self.adapters = {}
        self._initialize_adapters()

    def _initialize_adapters(self):
        for domain in (
            "PROCESS",
            "MEMORY",
            "NETWORK",
            "STORAGE",
            "SERVICES",
            "STARTUP",
            "SYSTEM",
        ):
            self.adapters[domain] = (
                WindowsDiagnosticExecutionAdapter(domain)
            )

    @staticmethod
    def _normalize_domain(domain):
        if not isinstance(domain, str):
            return None

        normalized = domain.strip().upper()

        if not normalized:
            return None

        return normalized

    def has_domain(self, domain):
        normalized = self._normalize_domain(domain)

        if normalized is None:
            return False

        return normalized in self.adapters

    def get_adapter(self, domain):
        normalized = self._normalize_domain(domain)

        if normalized is None:
            return None

        return self.adapters.get(normalized)

    def dispatch(self, domain, evidence=_UNSET):
        normalized = self._normalize_domain(domain)

        if normalized is None:
            raise ValueError(
                f"Invalid Windows diagnostic domain: {domain!r}"
            )

        if not WindowsDiagnosticCapability.is_supported(
            normalized
        ):
            raise ValueError(
                "Unsupported Windows diagnostic domain: "
                f"{normalized!r}"
            )

        adapter = self.get_adapter(normalized)

        if adapter is None:
            raise ValueError(
                "Windows diagnostic domain is not implemented: "
                f"{normalized}"
            )

        if (
            evidence is _UNSET
            and normalized in self._EVIDENCE_AWARE_DOMAINS
        ):
            return adapter.execute()

        if evidence is _UNSET:
            return adapter.execute(evidence=None)

        return adapter.execute(evidence=evidence)