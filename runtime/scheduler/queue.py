"""Async Task Queue Manager with Priority Handling and Retry Policies."""

import asyncio
from datetime import datetime
from typing import Any, Callable, Coroutine, Dict, List, Optional
import uuid

TaskFunc = Callable[[Dict[str, Any]], Coroutine[Any, Any, Any]]


class QueueTask:
    """Represents a background queue task unit."""

    def __init__(
        self,
        job_name: str,
        payload: Dict[str, Any],
        priority: int = 5,
        max_retries: int = 3,
        task_id: Optional[str] = None,
    ):
        self.task_id = task_id or f"task-{uuid.uuid4().hex[:8]}"
        self.job_name = job_name
        self.payload = payload
        self.priority = priority  # Lower number = higher priority
        self.max_retries = max_retries
        self.retry_count = 0
        self.status = "pending"  # pending, running, completed, failed
        self.result: Any = None
        self.error: Optional[str] = None
        self.created_at = datetime.utcnow().isoformat()
        self.completed_at: Optional[str] = None

    def __lt__(self, other: "QueueTask") -> bool:
        return self.priority < other.priority

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "job_name": self.job_name,
            "payload": self.payload,
            "priority": self.priority,
            "max_retries": self.max_retries,
            "retry_count": self.retry_count,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }


class TaskQueueManager:
    """Manages background task queues, concurrency, and task status tracking."""

    def __init__(self, concurrency: int = 5):
        self.concurrency = concurrency
        self._queue: asyncio.PriorityQueue[QueueTask] = asyncio.PriorityQueue()
        self._handlers: Dict[str, TaskFunc] = {}
        self._tasks_db: Dict[str, QueueTask] = {}

    def register_handler(self, job_name: str, handler: TaskFunc) -> None:
        """Register a handler function for a specific job name."""
        self._handlers[job_name] = handler

    async def enqueue(
        self, job_name: str, payload: Dict[str, Any], priority: int = 5, max_retries: int = 3
    ) -> QueueTask:
        """Enqueue a new task for async background processing."""
        task = QueueTask(job_name=job_name, payload=payload, priority=priority, max_retries=max_retries)
        self._tasks_db[task.task_id] = task
        await self._queue.put(task)
        return task

    def get_task_status(self, task_id: str) -> Optional[QueueTask]:
        """Retrieve task by ID."""
        return self._tasks_db.get(task_id)

    async def process_next(self) -> Optional[QueueTask]:
        """Process a single task from the priority queue."""
        if self._queue.empty():
            return None

        task = await self._queue.get()
        task.status = "running"
        handler = self._handlers.get(task.job_name)

        if not handler:
            task.status = "failed"
            task.error = f"No registered handler for job '{task.job_name}'"
            task.completed_at = datetime.utcnow().isoformat()
            return task

        try:
            task.result = await handler(task.payload)
            task.status = "completed"
            task.completed_at = datetime.utcnow().isoformat()
        except Exception as exc:
            task.retry_count += 1
            if task.retry_count <= task.max_retries:
                task.status = "pending"
                await self._queue.put(task)  # Re-enqueue for retry
            else:
                task.status = "failed"
                task.error = str(exc)
                task.completed_at = datetime.utcnow().isoformat()

        return task
