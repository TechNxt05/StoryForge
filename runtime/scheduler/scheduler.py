"""Task Scheduler Engine for StoryForge Runtime."""

import asyncio
from typing import Dict, Optional
from ..interfaces import IScheduler
from .queue import TaskQueueManager, QueueTask


class TaskScheduler(IScheduler):
    """Schedules one-shot or recurring background tasks."""

    def __init__(self, queue_manager: Optional[TaskQueueManager] = None):
        self.queue_manager = queue_manager or TaskQueueManager()
        self._scheduled_jobs: Dict[str, asyncio.Task[None]] = {}

    async def schedule_job(self, job_id: str, cron_or_delay: str) -> None:
        """Schedule a job by ID with a delay in seconds or cron directive."""
        # Simple integer delay representation check (e.g. "5" -> 5 seconds)
        try:
            delay_seconds = float(cron_or_delay)
        except ValueError:
            delay_seconds = 1.0  # Default fallback for cron directives

        async def _delayed_execution() -> None:
            await asyncio.sleep(delay_seconds)
            await self.queue_manager.enqueue(
                job_name="scheduled_job", payload={"job_id": job_id}, priority=3
            )

        async_task = asyncio.create_task(_delayed_execution())
        self._scheduled_jobs[job_id] = async_task

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a scheduled job if pending."""
        if job_id in self._scheduled_jobs:
            task = self._scheduled_jobs[job_id]
            task.cancel()
            del self._scheduled_jobs[job_id]
            return True
        return False
