"""Production controller connecting dashboard requests to diagnostics."""

from engine.problem_solving_engine import ProductionProblemSolvingEngine
from engine.technician_workflow import TechnicianWorkflow
from engine.v1_0_platform import V1ProductionTechnicianPlatform
from engine.system_health_model import SystemHealthModel
from engine.v1_0_investigation_pipeline import V1InvestigationPipeline


class DashboardDiagnosticController:
    """Compose and execute one authorized-by-design diagnostic investigation.

    Diagnosis is performed through the existing production engine.
    This controller never authorizes or executes remediation.
    """

    def __init__(self, platform_factory=V1ProductionTechnicianPlatform):
        if not callable(platform_factory):
            raise TypeError("platform_factory must be callable.")
        self._platform_factory = platform_factory
        self.last_case = None
        self.last_workflow = None
        self.last_engine = None
        self.last_summary = None

    @staticmethod
    def _read(objects, *names):
        for obj in objects:
            if obj is None:
                continue
            for name in names:
                try:
                    value = getattr(obj, name, None)
                    if callable(value):
                        value = value()
                except Exception:
                    continue
                if value is not None:
                    return value
        return None

    @classmethod
    def _items(cls, objects, *names):
        value = cls._read(objects, *names)
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, (tuple, set)):
            return list(value)
        return [value]

    @staticmethod
    def _display_item(item):
        """Normalize diagnostic evidence without discarding its structure."""
        if item is None or isinstance(item, (str, int, float, bool)):
            return item

        if isinstance(item, dict):
            return {
                str(key): DashboardDiagnosticController._display_item(value)
                for key, value in item.items()
            }

        if isinstance(item, (list, tuple)):
            return [
                DashboardDiagnosticController._display_item(value)
                for value in item
            ]

        if isinstance(item, set):
            return [
                DashboardDiagnosticController._display_item(value)
                for value in sorted(item, key=str)
            ]

        values = getattr(item, "__dict__", None)
        if isinstance(values, dict):
            return {
                str(key): DashboardDiagnosticController._display_item(value)
                for key, value in values.items()
                if not str(key).startswith("_")
            }

        return str(item)

    def run_diagnostics(self):
        """Run all registered Windows diagnostic domains and return results."""
        platform = self._platform_factory()
        case = platform.create_case()
        workflow = TechnicianWorkflow(case)

        engine = ProductionProblemSolvingEngine(
            case=case,
            workflow=workflow,
            diagnostic_registry=platform.diagnostic_registry,
        )

        self.last_case = case
        self.last_workflow = workflow
        self.last_engine = engine

        domains = list(
            platform.diagnostic_registry.supported_domains()
        )

        summary = engine.solve(domains)
        self.last_summary = summary

        result = summary.get("result")
        failures = summary.get("domain_failures") or summary.get("failures") or {}
        domain_results = summary.get("domain_results") or {}

        sources = (result, case)

        findings = self._items(
            sources, "findings", "system_findings"
        )
        correlations = self._items(
            sources, "correlations", "relationships"
        )
        root_causes = self._items(
            sources, "root_causes", "root_cause_candidates"
        )
        recommendations = self._items(
            sources, "recommendations"
        )

        # Aggregate actual domain-level diagnostic outputs. Some engines
        # return dictionaries, while others return WindowsDiagnosticResult.
        # Preserve the existing aggregate data and avoid duplicate entries.
        def append_unique(target, values):
            def freeze(value):
                if isinstance(value, dict):
                    return (
                        "dict",
                        tuple(sorted(
                            ((str(key), freeze(item)) for key, item in value.items()),
                            key=lambda pair: pair[0],
                        )),
                    )
                if isinstance(value, (list, tuple)):
                    return ("sequence", tuple(freeze(item) for item in value))
                if isinstance(value, set):
                    return ("set", tuple(sorted(
                        (freeze(item) for item in value), key=repr
                    )))
                try:
                    hash(value)
                    return ("value", value)
                except TypeError:
                    return ("repr", repr(value))

            def recommendation_key(item):
                if not isinstance(item, dict):
                    return freeze(item)

                kind = str(item.get("type", "")).strip().upper()
                priority = str(item.get("priority", "")).strip().upper()

                action = " ".join(str(
                    item.get("action")
                    or item.get("recommended_action")
                    or item.get("recommendation")
                    or item.get("text")
                    or ""
                ).split()).casefold()

                finding = item.get("finding")
                if isinstance(finding, dict):
                    finding_identity = (
                        finding.get("finding_id")
                        or finding.get("id")
                        or finding.get("finding_type")
                        or finding.get("type")
                        or finding.get("category")
                    )
                else:
                    finding_identity = None

                if action:
                    return (
                        "recommendation",
                        kind,
                        action,
                        str(finding_identity or "").strip().casefold(),
                    )

                return (
                    "recommendation",
                    freeze({
                        key: value
                        for key, value in item.items()
                        if key not in {"rationale", "domain", "domains"}
                    }),
                )
            if values is None:
                return
            items = values if isinstance(values, (list, tuple, set)) else [values]
            seen = {recommendation_key(item) for item in target}

            for item in items:
                if item is None:
                    continue
                key = recommendation_key(item)
                if key not in seen:
                    target.append(item)
                    seen.add(key)

        for domain_payload in domain_results.values():
            if isinstance(domain_payload, dict):
                diagnosis = domain_payload.get("diagnosis")
                diagnosis = diagnosis if isinstance(diagnosis, dict) else {}

                domain_findings = (
                    domain_payload.get("findings")
                    or domain_payload.get("system_findings")
                    or diagnosis.get("findings")
                )
                append_unique(findings, domain_findings)

                domain_correlations = (
                    domain_payload.get("correlations")
                    or diagnosis.get("correlations")
                )
                append_unique(correlations, domain_correlations)

                domain_root_causes = (
                    domain_payload.get("root_causes")
                    or domain_payload.get("root_cause_candidates")
                    or domain_payload.get("candidates")
                    or diagnosis.get("root_causes")
                )
                append_unique(root_causes, domain_root_causes)

                domain_recommendations = (
                    domain_payload.get("recommendations")
                    or diagnosis.get("recommendations")
                    or domain_payload.get("recommendation")
                )
                append_unique(recommendations, domain_recommendations)
            else:
                append_unique(
                    findings,
                    self._items((domain_payload,), "findings", "system_findings"),
                )
                append_unique(
                    correlations,
                    self._items((domain_payload,), "correlations", "relationships"),
                )
                append_unique(
                    root_causes,
                    self._items(
                        (domain_payload,),
                        "root_causes",
                        "root_cause_candidates",
                    ),
                )
                append_unique(
                    recommendations,
                    self._items((domain_payload,), "recommendations"),
                )

        # Run canonical system-level intelligence on observed domain evidence.
        if result is not None:
            system_domains = {}
            system_evidence = []

            for domain_name, payload in domain_results.items():
                if isinstance(payload, dict):
                    raw_findings = (
                        payload.get("findings")
                        or payload.get("system_findings")
                        or []
                    )
                    diagnosis = payload.get("diagnosis")
                    if not raw_findings and isinstance(diagnosis, dict):
                        raw_findings = diagnosis.get("findings") or []

                    if not raw_findings:
                        raw_findings = [
                            payload[key]
                            for key in (
                                "process_finding",
                                "memory_finding",
                                "memory_temporal_finding",
                                "memory_diagnostic_finding",
                            )
                            if payload.get(key) is not None
                        ]
                else:
                    raw_findings = self._items(
                        (payload,), "findings", "system_findings"
                    )

                source_domain = str(domain_name).upper()
                system_domains.setdefault(
                    source_domain, {"findings": []}
                )

                for finding in raw_findings:
                    finding_data = self._display_item(finding)
                    if not isinstance(finding_data, dict):
                        continue

                    finding_type = str(
                        finding_data.get("finding_type", "")
                    ).strip().upper()

                    # Route canonical finding types to their semantic
                    # domains rather than blindly trusting the adapter
                    # that happened to return them.
                    if finding_type in {
                        "HIGH_PROCESS_MEMORY",
                        "HIGH_COMMIT_USAGE",
                    }:
                        evidence_domain = "PROCESS"
                    elif finding_type in {
                        "MEMORY_PRESSURE",
                        "MEMORY_EXHAUSTION",
                    }:
                        evidence_domain = "MEMORY"
                    else:
                        evidence_domain = source_domain

                    system_domains.setdefault(
                        evidence_domain, {"findings": []}
                    )
                    system_domains[evidence_domain]["findings"].append(
                        finding_data
                    )

                    system_evidence.append({
                        "domain": evidence_domain,
                        "finding": finding_data,
                    })

            if system_evidence:
                pipeline = V1InvestigationPipeline(
                    system_intelligence=getattr(
                        platform, "system_intelligence", None
                    ),
                    investigation=getattr(
                        platform, "system_investigation", None
                    ),
                    relationships=getattr(
                        platform, "system_relationships", None
                    ),
                    root_cause=getattr(
                        platform, "system_root_cause", None
                    ),
                    recommendations=getattr(
                        platform, "system_recommendations", None
                    ),
                )
                intelligence_result = pipeline.run(
                    domains=system_domains,
                    system_data={
                        "findings": system_evidence,
                        "patterns": [],
                    },
                    evidence=system_evidence,
                    case=case,
                )
                relationship_result = intelligence_result.get(
                    "relationships", {}
                )
                relationship_items = (
                    relationship_result.get("relationships", [])
                    if isinstance(relationship_result, dict)
                    else []
                )

                root_cause_result = intelligence_result.get(
                    "root_cause", {}
                )
                root_cause_items = (
                    root_cause_result.get("root_causes", [])
                    if isinstance(root_cause_result, dict)
                    else []
                )

                recommendation_result = intelligence_result.get(
                    "recommendations", {}
                )
                recommendation_items = (
                    recommendation_result.get("recommendations", [])
                    if isinstance(recommendation_result, dict)
                    else []
                )
                append_unique(correlations, relationship_items)
                append_unique(root_causes, root_cause_items)

                canonical_recommendation_domains = {
                    str(item.get("domain", "")).strip().upper()
                    for item in recommendation_items
                    if isinstance(item, dict)
                    and str(item.get("type", "")).strip().upper() == "FINDING"
                    and str(item.get("domain", "")).strip()
                }

                if canonical_recommendation_domains:
                    recommendations[:] = [
                        item
                        for item in recommendations
                        if not (
                            isinstance(item, dict)
                            and str(item.get("category", "")).strip().upper()
                                in canonical_recommendation_domains
                            and item.get("recommendation") is not None
                            and not item.get("action")
                            and not item.get("recommended_action")
                            and not item.get("finding")
                        )
                    ]

                append_unique(recommendations, recommendation_items)
        # Interpret observed findings without changing diagnostic status
        # or authorizing, scheduling, or executing remediation.
        health_domains = {}
        for domain, payload in domain_results.items():
            domain_findings = self._items(
                (payload,), "findings", "system_findings"
            )

            # Some diagnostic adapters expose findings under diagnosis.
            if isinstance(payload, dict):
                if not domain_findings:
                    diagnosis = payload.get("diagnosis")
                    if isinstance(diagnosis, dict):
                        domain_findings = (
                            diagnosis.get("findings") or []
                        )

                # Preserve domain-specific findings exposed by adapters.
                if not domain_findings:
                    for finding_key in (
                        "process_finding",
                        "memory_finding",
                        "memory_temporal_finding",
                        "memory_diagnostic_finding",
                    ):
                        finding = payload.get(finding_key)
                        if finding is not None:
                            domain_findings.append(finding)

            health_domains[str(domain)] = {
                "findings": [
                    self._display_item(item)
                    for item in domain_findings
                ]
            }

        # Use aggregate findings only when domain-level findings are absent.
        if not any(
            payload["findings"]
            for payload in health_domains.values()
        ):
            aggregate_findings = [
                self._display_item(item) for item in findings
            ]
            if aggregate_findings:
                if health_domains:
                    first_domain = next(iter(health_domains))
                    health_domains[first_domain]["findings"] = aggregate_findings
                else:
                    health_domains["SYSTEM"] = {
                        "findings": aggregate_findings
                    }

        system_health = SystemHealthModel().evaluate(health_domains)

        # Scoring reflects observed findings; coverage reflects completion.
        failed_domains = set(failures)
        completed_domains = set(domain_results)
        requested_domains = set(domains)

        incomplete_domains = (
            requested_domains - completed_domains
        ) | failed_domains

        for domain in incomplete_domains:
            system_health["domain_health"][str(domain)] = "UNKNOWN"

        if incomplete_domains:
            system_health["coverage"] = "PARTIAL"

            # Incomplete evidence cannot establish that the whole
            # system is healthy. Preserve any observed adverse status.
            if system_health.get("status") == "HEALTHY":
                system_health["status"] = "UNKNOWN"

        primary_cause = self._read(
            sources, "primary_root_cause", "primary_cause", "root_cause"
        )
        if not root_causes and primary_cause is not None:
            root_causes = [primary_cause]

        successful = result is not None
        partial = successful and bool(failures)

        if successful and partial:
            health_status = "PARTIAL"
        elif successful:
            health_status = "DIAGNOSED"
        else:
            health_status = "DIAGNOSTICS FAILED"

        intelligence = {
            "health": {
                "status": health_status,
                "score": system_health["health_score"],
                "system_status": system_health["status"],
                "coverage": system_health["coverage"],
                "domain_health": system_health["domain_health"],
            },
            "system_findings": [
                self._display_item(item) for item in findings
            ],
            "relationships": [
                self._display_item(item) for item in correlations
            ],
            "root_causes": [
                self._display_item(item) for item in root_causes
            ],
            "recommendations": [
                self._display_item(item) for item in recommendations
            ],
        }

        return {
            "success": successful,
            "partial": partial,
            "domains_requested": domains,
            "domains_completed": len(domain_results),
            "failures": failures,
            "workflow_state": getattr(
                summary.get("workflow_state"), "name",
                str(summary.get("workflow_state", "UNKNOWN")),
            ),
            "intelligence": intelligence,
            "summary": summary,
        }


__all__ = ["DashboardDiagnosticController"]
