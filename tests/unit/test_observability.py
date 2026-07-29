"""Observability Stack Unit Tests."""

import pytest
from packages.observability.src.python_telemetry import PythonTracerSpan, PythonMetricsCollector


def test_python_tracer_span() -> None:
    span = PythonTracerSpan("test_agent_execution", {"agent_id": "agent-101"})
    assert span.span_name == "test_agent_execution"
    assert span.attributes["agent_id"] == "agent-101"

    duration = span.end()
    assert duration >= 0.0


def test_python_metrics_collector() -> None:
    collector = PythonMetricsCollector()

    v1 = collector.increment("rendered_videos_total", 1.0)
    assert v1 == 1.0

    v2 = collector.increment("rendered_videos_total", 2.0)
    assert v2 == 3.0

    prom_str = collector.export_prometheus_format()
    assert "storyforge_rendered_videos_total 3.0" in prom_str
