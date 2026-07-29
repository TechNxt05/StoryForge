"""Performance Optimizer Unit Tests."""

import time
import asyncio
import pytest
from runtime.performance import PerformanceOptimizer


@pytest.mark.asyncio
async def test_performance_cache_hit_latency() -> None:
    optimizer = PerformanceOptimizer()
    optimizer.set_cached("test-key", {"data": "cached_payload"})

    start_time = time.perf_counter()
    cached = optimizer.get_cached("test-key")
    latency_ms = (time.perf_counter() - start_time) * 1000

    assert cached == {"data": "cached_payload"}
    assert latency_ms < 50.0  # Production target sub-50ms latency


@pytest.mark.asyncio
async def test_performance_batch_execution() -> None:
    optimizer = PerformanceOptimizer()

    async def sample_task(val: int) -> int:
        await asyncio.sleep(0.01)
        return val * 2

    tasks = [lambda v=i: sample_task(v) for i in range(5)]
    results = await optimizer.execute_batch(tasks, max_concurrency=3)

    assert results == [0, 2, 4, 6, 8]

    stats = optimizer.get_cache_stats()
    assert "hit_ratio" in stats
