"""Scheduler runtime interface skeleton."""
from abc import ABC, abstractmethod


class IScheduler(ABC):
    @abstractmethod
    async def schedule_job(self, job_id: str, cron_or_delay: str) -> None:
        pass
