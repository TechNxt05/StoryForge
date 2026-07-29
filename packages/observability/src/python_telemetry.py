"""OpenTelemetry Tracing & Prometheus Exporter for StoryForge Python Runtime & API Gateway."""

import time
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("storyforge.observability")


class PythonTracerSpan:
    """Represents an OpenTelemetry trace span in Python."""

    def __init__(self, span_name: str, attributes: Optional[Dict[str, Any]] = None):
        self.span_name = span_name
        self.attributes = attributes or {}
        self.start_time = time.time()

    def end(self) -> float:
        duration_ms = round((time.time() - self.start_time) * 1000, 2)
        logger.info(f"[TraceSpan] {self.span_name} completed in {duration_ms}ms | Attributes: {self.attributes}")
        return duration_ms


class PythonMetricsCollector:
    """Prometheus metrics collector for Python services."""

    def __init__(self) -> None:
        self._counters: Dict[str, float] = {
            "requests_total": 0,
            "rendered_videos_total": 0,
            "agent_steps_executed_total": 0,
        }

    def increment(self, metric_name: str, value: float = 1.0) -> float:
        current = self._counters.get(metric_name, 0.0)
        updated = current + value
        self._counters[metric_name] = updated
        return updated

    def export_prometheus_format(self) -> str:
        lines = ["# HELP storyforge_python_metrics StoryForge Runtime Metrics"]
        for key, val in self._counters.items():
            lines.append(f"storyforge_{key} {val}")
        return "\n".join(lines)


# Global singleton exporter instances
tracer_instance = PythonTracerSpan
metrics_collector = PythonMetricsCollector()
