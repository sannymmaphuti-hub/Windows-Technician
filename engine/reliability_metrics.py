"""Read-only reliability and recovery metrics for Windows Technician V1.0."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from typing import Any


class ReliabilityMetricsCollector:
    """Calculate reliability metrics from an existing ReliabilityService.

    Metrics describe recorded state and decisions. They do not imply that
    an approved retry or recovery plan was actually executed.
    """

    TERMINAL_OPERATION_STATUSES = frozenset(
        {"SUCCEEDED", "FAILED", "CANCELLED"}
    )

    def __init__(self, reliability_service: Any) -> None:
        if reliability_service is None:
            raise TypeError("reliability_service is required.")

        if not callable(getattr(reliability_service, "projection", None)):
            raise TypeError(
                "reliability_service must provide projection()."
            )

        self._reliability_service = reliability_service

    @staticmethod
    def _mapping(value: Any) -> Mapping:
        return value if isinstance(value, Mapping) else {}

    @staticmethod
    def _status(value: Any) -> str:
        if value is None:
            return "UNKNOWN"

        value = getattr(value, "value", value)
        if not isinstance(value, str):
            return "UNKNOWN"

        value = value.strip().upper()
        return value or "UNKNOWN"

    @staticmethod
    def _records(value: Any) -> tuple[Any, ...]:
        """Read record collections without modifying the source."""
        if isinstance(value, Mapping):
            # A projection may be a status-count mapping rather than records.
            return tuple(value.values())

        if isinstance(value, (list, tuple)):
            return tuple(value)

        return ()

    @classmethod
    def _status_counts(cls, records: tuple[Any, ...]) -> dict[str, int]:
        counts = Counter()

        for record in records:
            if isinstance(record, Mapping):
                status = record.get("status")
            else:
                status = getattr(record, "status", None)

            counts[cls._status(status)] += 1

        return dict(sorted(counts.items()))

    @classmethod
    def _count_projection(cls, value: Any) -> dict[str, int]:
        """Normalize a status-to-count projection without guessing records."""
        mapping = cls._mapping(value)
        counts: dict[str, int] = {}

        for key, count in mapping.items():
            if not isinstance(key, str):
                continue

            if isinstance(count, bool) or not isinstance(count, int):
                continue

            if count < 0:
                continue

            counts[key.upper()] = count

        return dict(sorted(counts.items()))

    @staticmethod
    def _failure_category(record: Any) -> str:
        if isinstance(record, Mapping):
            category = record.get("category", record.get("failure_category"))
        else:
            category = getattr(
                record,
                "category",
                getattr(record, "failure_category", None),
            )

        if category is None:
            return "UNKNOWN"

        category = getattr(category, "value", category)
        if not isinstance(category, str) or not category.strip():
            return "UNKNOWN"

        return category.strip().upper()

    @staticmethod
    def _decision_status(record: Any) -> str:
        if isinstance(record, Mapping):
            status = record.get(
                "status",
                record.get("decision", record.get("outcome")),
            )
        else:
            status = getattr(
                record,
                "status",
                getattr(record, "decision", getattr(record, "outcome", None)),
            )

        return ReliabilityMetricsCollector._status(status)

    @classmethod
    def _category_counts(cls, records: tuple[Any, ...]) -> dict[str, int]:
        counts = Counter(
            cls._failure_category(record)
            for record in records
        )
        return dict(sorted(counts.items()))

    @classmethod
    def _decision_counts(cls, records: tuple[Any, ...]) -> dict[str, int]:
        counts = Counter(
            cls._decision_status(record)
            for record in records
        )
        return dict(sorted(counts.items()))

    def projection(self) -> dict[str, Any]:
        """Return a fresh snapshot of recorded reliability information."""
        source = self._reliability_service.projection()

        if not isinstance(source, Mapping):
            raise TypeError(
                "reliability_service.projection() must return a mapping."
            )

        # Canonical Phase 12 ReliabilityService projection.
        # Preserve compatibility with the generic projection shapes below.
        if all(
            key in source
            for key in (
                "operation_summary",
                "retry_summary",
                "recovery_summary",
            )
        ):
            operation_summary = self._mapping(
                source.get("operation_summary")
            )
            retry_summary = self._mapping(
                source.get("retry_summary")
            )
            recovery_summary = self._mapping(
                source.get("recovery_summary")
            )

            operation_counts = self._count_projection(
                operation_summary.get("by_status", {})
            )
            recovery_counts = self._count_projection(
                recovery_summary.get("by_status", {})
            )

            retry_total = retry_summary.get("decision_count", 0)
            if (
                isinstance(retry_total, bool)
                or not isinstance(retry_total, int)
            ):
                retry_total = 0
            retry_total = max(0, retry_total)

            approved_retries = retry_summary.get("approved_retries", 0)
            if (
                isinstance(approved_retries, bool)
                or not isinstance(approved_retries, int)
            ):
                approved_retries = 0
            approved_retries = max(0, min(approved_retries, retry_total))

            retry_counts = {}
            if retry_total:
                retry_counts["APPROVED"] = approved_retries
                denied = retry_total - approved_retries
                if denied:
                    retry_counts["NOT_APPROVED"] = denied

            recovery_total = recovery_summary.get("total", 0)
            if (
                isinstance(recovery_total, bool)
                or not isinstance(recovery_total, int)
            ):
                recovery_total = sum(recovery_counts.values())
            recovery_total = max(0, recovery_total)

            return {
                "operation_status_counts": dict(operation_counts),
                "failed_operation_count": operation_counts.get("FAILED", 0),
                "failure_categories": {},
                "retry_decision_counts": dict(retry_counts),
                "retry_decision_count": retry_total,
                "recovery_status_counts": dict(recovery_counts),
                "recovery_record_count": recovery_total,
                "recovery_approved_count": sum(
                    count
                    for status, count in recovery_counts.items()
                    if "APPROV" in status
                    or status in {"AUTHORIZED", "ALLOWED"}
                ),
                "recovery_denied_count": sum(
                    count
                    for status, count in recovery_counts.items()
                    if "DENIED" in status or "REJECT" in status
                ),
                "recovery_executed_count": sum(
                    count
                    for status, count in recovery_counts.items()
                    if "EXECUT" in status or "COMPLETED" in status
                ),
            }

        operations_section = self._mapping(source.get("operations"))
        history_section = self._mapping(
            source.get("recovery_history")
        )

        operation_records_value = operations_section.get(
            "records",
            operations_section.get("operations", ()),
        )
        operation_records = self._records(operation_records_value)

        # Some trackers expose counts rather than individual records.
        operation_counts = self._count_projection(
            operations_section.get("by_status", {})
        )

        if operation_records:
            operation_counts = self._status_counts(operation_records)

        failure_records = tuple(
            record
            for record in operation_records
            if self._status(
                record.get("status")
                if isinstance(record, Mapping)
                else getattr(record, "status", None)
            ) == "FAILED"
        )

        recovery_entries_value = history_section.get(
            "entries",
            (),
        )
        recovery_entries = self._records(recovery_entries_value)

        recovery_counts = self._count_projection(
            history_section.get("by_status", {})
        )

        if recovery_entries:
            recovery_counts = self._status_counts(recovery_entries)

        retry_section = self._mapping(source.get("retry_decisions"))
        retry_records = self._records(
            retry_section.get("entries", retry_section.get("decisions", ()))
        )
        retry_counts = self._count_projection(
            retry_section.get("by_status", {})
        )

        if retry_records:
            retry_counts = self._decision_counts(retry_records)

        recovery_total = history_section.get("total", len(recovery_entries))
        if isinstance(recovery_total, bool) or not isinstance(recovery_total, int):
            recovery_total = len(recovery_entries)
        recovery_total = max(0, recovery_total)

        retry_total = retry_section.get("total", len(retry_records))
        if isinstance(retry_total, bool) or not isinstance(retry_total, int):
            retry_total = len(retry_records)
        retry_total = max(0, retry_total)

        return {
            "operation_status_counts": dict(operation_counts),
            "failed_operation_count": operation_counts.get("FAILED", 0),
            "failure_categories": self._category_counts(failure_records),
            "retry_decision_counts": dict(retry_counts),
            "retry_decision_count": retry_total,
            "recovery_status_counts": dict(recovery_counts),
            "recovery_record_count": recovery_total,
            "recovery_approved_count": sum(
                count
                for status, count in recovery_counts.items()
                if "APPROV" in status or status in {"AUTHORIZED", "ALLOWED"}
            ),
            "recovery_denied_count": sum(
                count
                for status, count in recovery_counts.items()
                if "DENIED" in status or "REJECT" in status
            ),
            "recovery_executed_count": sum(
                count
                for status, count in recovery_counts.items()
                if "EXECUT" in status or "COMPLETED" in status
            ),
        }
