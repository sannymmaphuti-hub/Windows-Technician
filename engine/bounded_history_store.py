"""Thread-safe bounded in-memory history store."""

from collections import deque
from copy import deepcopy
from threading import RLock
from typing import Any, Iterable


class BoundedHistoryStore:
    """Retain the newest records up to a configured capacity."""

    SCHEMA_VERSION = "1.0"

    def __init__(
        self,
        capacity: int = 1000,
        initial_records: Iterable[Any] | None = None,
    ) -> None:
        self._validate_capacity(capacity)

        self._lock = RLock()
        self._capacity = capacity
        self._records: deque[Any] = deque()
        self._evicted_count = 0

        if initial_records is not None:
            for record in initial_records:
                self.append(record)

    @staticmethod
    def _validate_capacity(capacity: int) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int):
            raise TypeError("capacity must be an integer")
        if capacity < 1:
            raise ValueError("capacity must be at least 1")

    @property
    def capacity(self) -> int:
        return self._capacity

    def append(self, record: Any) -> None:
        """Append a detached record, evicting the oldest if necessary."""

        detached = deepcopy(record)

        with self._lock:
            if len(self._records) >= self._capacity:
                self._records.popleft()
                self._evicted_count += 1

            self._records.append(detached)

    def extend(self, records: Iterable[Any]) -> None:
        """Append multiple records using the same bounded retention rule."""

        for record in records:
            self.append(record)

    def snapshot(self) -> list[Any]:
        """Return a detached list of retained records."""

        with self._lock:
            return deepcopy(list(self._records))

    def projection(self) -> dict[str, Any]:
        """Return retention metadata and a detached record snapshot."""

        with self._lock:
            return {
                "schema_version": self.SCHEMA_VERSION,
                "capacity": self._capacity,
                "record_count": len(self._records),
                "evicted_count": self._evicted_count,
                "records": deepcopy(list(self._records)),
            }

    def clear(self) -> int:
        """Clear retained history and return the number of removed records.

        Clearing is an explicit administrative action. It does not reset the
        cumulative eviction counter.
        """

        with self._lock:
            removed = len(self._records)
            self._records.clear()
            return removed
