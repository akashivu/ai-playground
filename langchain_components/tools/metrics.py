from __future__ import annotations

from typing import Protocol


class MetricsSink(Protocol):
    

    def record_duration(self, tool_name: str, duration_ms: float) -> None: ...

    def increment_success(self, tool_name: str) -> None: ...

    def increment_failure(self, tool_name: str) -> None: ...

    def increment_timeout(self, tool_name: str) -> None: ...


class NoOpMetricsSink:
    

    def record_duration(self, tool_name: str, duration_ms: float) -> None:
        pass

    def increment_success(self, tool_name: str) -> None:
        pass

    def increment_failure(self, tool_name: str) -> None:
        pass

    def increment_timeout(self, tool_name: str) -> None:
        pass


class InMemoryMetricsSink:
    

    def __init__(self) -> None:
        self.durations_ms: dict[str, list[float]] = {}
        self.success_total: dict[str, int] = {}
        self.failure_total: dict[str, int] = {}
        self.timeout_total: dict[str, int] = {}

    def record_duration(self, tool_name: str, duration_ms: float) -> None:
        self.durations_ms.setdefault(tool_name, []).append(duration_ms)

    def increment_success(self, tool_name: str) -> None:
        self.success_total[tool_name] = self.success_total.get(tool_name, 0) + 1

    def increment_failure(self, tool_name: str) -> None:
        self.failure_total[tool_name] = self.failure_total.get(tool_name, 0) + 1

    def increment_timeout(self, tool_name: str) -> None:
        self.timeout_total[tool_name] = self.timeout_total.get(tool_name, 0) + 1