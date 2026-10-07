from engine.windows_diagnostic_domain_resolution import (
    WindowsDiagnosticDomainResolution,
)


_UNSET = object()


class WindowsDiagnosticExecutionAdapter:
    _EVIDENCE_DOMAINS = {
        "NETWORK",
        "STORAGE",
        "SERVICES",
        "STARTUP",
        "SYSTEM",
    }

    def __init__(self, domain, implementation=None):
        resolution = WindowsDiagnosticDomainResolution.resolve(
            domain
        )

        if not resolution.capability_supported:
            raise ValueError(
                f"Unsupported Windows diagnostic domain: {domain!r}"
            )

        if not resolution.implemented:
            raise ValueError(
                "Windows diagnostic domain is not implemented: "
                f"{resolution.domain}"
            )

        self.domain = resolution.domain

        self.implementation = (
            implementation
            if implementation is not None
            else self._create_implementation(resolution)
        )

    @staticmethod
    def _create_implementation(resolution):
        implementation_class = resolution.engine

        if implementation_class is None:
            raise ValueError(
                "No diagnostic implementation exists "
                f"for {resolution.domain}."
            )

        return implementation_class()

    def execute(self, evidence=_UNSET):
        if self.domain == "NETWORK":
            if evidence is _UNSET or evidence is None:
                raise ValueError(
                    "NETWORK diagnostic execution requires evidence."
                )

            return self.implementation.diagnose(evidence)

        if self.domain in {
            "STORAGE",
            "SERVICES",
            "STARTUP",
            "SYSTEM",
        }:
            if evidence is _UNSET:
                return self.implementation.analyze()

            return self.implementation.analyze(evidence)

        return self.implementation.analyze()