"""Benchmark Runner for StoryForge API Gateway Latency & Throughput Metrics."""

import sys
import time
import asyncio
from pathlib import Path
from typing import Any, Dict, List

# Add monorepo root to Python module search path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import httpx
from apps.api.src.main import app


async def run_gateway_benchmarks(num_requests: int = 100) -> Dict[str, Any]:
    """Execute high-concurrency benchmark requests against API Gateway and report RPS and latency percentiles."""
    latencies_ms: List[float] = []
    errors: int = 0

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        start_total = time.perf_counter()

        for _ in range(num_requests):
            req_start = time.perf_counter()
            try:
                res = await client.get("/health")
                if res.status_code == 200:
                    latencies_ms.append((time.perf_counter() - req_start) * 1000)
                else:
                    errors += 1
            except Exception:
                errors += 1

        total_duration = time.perf_counter() - start_total

    latencies_ms.sort()
    rps = round(num_requests / total_duration, 2)
    p50 = round(latencies_ms[int(len(latencies_ms) * 0.50)], 2) if latencies_ms else 0.0
    p95 = round(latencies_ms[int(len(latencies_ms) * 0.95)], 2) if latencies_ms else 0.0

    report = {
        "total_requests": num_requests,
        "total_duration_seconds": round(total_duration, 3),
        "requests_per_second_rps": rps,
        "p50_latency_ms": p50,
        "p95_latency_ms": p95,
        "error_count": errors,
        "error_rate_pct": round((errors / num_requests) * 100, 2),
    }
    return report


if __name__ == "__main__":
    results = asyncio.run(run_gateway_benchmarks(100))
    print("STORYFORGE BENCHMARK REPORT:")
    for k, v in results.items():
        print(f"  {k}: {v}")
