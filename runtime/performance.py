"""Performance Optimization Engine for StoryForge Runtime."""

import asyncio
import functools
import time
from typing import Any, Callable, Dict, List, Optional


class PerformanceOptimizer:
    """Provides caching, task batching, and async execution pool tuning for high-throughput runtime execution."""

    def __init__(self, cache_size: int = 1000, default_ttl_seconds: int = 3600):
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_size = cache_size
        self.default_ttl_seconds = default_ttl_seconds
        self._metrics = {"hits": 0, "misses": 0}

    def get_cached(self, key: str) -> Optional[Any]:
        """Retrieve cached value if present and not expired."""
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            if time.time() < entry["expires_at"]:
                self._metrics["hits"] += 1
                return entry["value"]
            else:
                del self._memory_cache[key]

        self._metrics["misses"] += 1
        return None

    def set_cached(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Store value in LRU memory cache."""
        if len(self._memory_cache) >= self.cache_size:
            # Evict oldest entry
            oldest_key = next(iter(self._memory_cache))
            del self._memory_cache[oldest_key]

        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds
        self._memory_cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl,
        }

    def get_cache_stats(self) -> Dict[str, Any]:
        """Return cache hit/miss ratio and total cached entries."""
        total = self._metrics["hits"] + self._metrics["misses"]
        hit_ratio = (self._metrics["hits"] / total) if total > 0 else 0.0
        return {
            "hits": self._metrics["hits"],
            "misses": self._metrics["misses"],
            "hit_ratio": round(hit_ratio, 4),
            "cached_entries": len(self._memory_cache),
        }

    async def execute_batch(self, coros: List[Callable[[], Any]], max_concurrency: int = 10) -> List[Any]:
        """Execute a batch of async tasks concurrently with bounded semaphore throttling."""
        semaphore = asyncio.Semaphore(max_concurrency)

        async def worker(task_fn: Callable[[], Any]) -> Any:
            async with semaphore:
                return await task_fn()

        return await asyncio.gather(*[worker(fn) for fn in coros])


# Global performance optimizer singleton
performance_engine = PerformanceOptimizer()
