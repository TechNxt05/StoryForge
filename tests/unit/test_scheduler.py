"""Task Scheduler Unit Tests."""

import asyncio
import pytest
from runtime.scheduler import TaskQueueManager, TaskScheduler


@pytest.mark.asyncio
async def test_task_queue_execution() -> None:
    qm = TaskQueueManager()

    async def mock_render(payload: dict) -> str:
        return f"Rendered {payload['video_id']}"

    qm.register_handler("render_video", mock_render)
    task = await qm.enqueue("render_video", {"video_id": "v101"}, priority=1)

    processed = await qm.process_next()
    assert processed is not None
    assert processed.status == "completed"
    assert processed.result == "Rendered v101"


@pytest.mark.asyncio
async def test_task_priority_ordering() -> None:
    qm = TaskQueueManager()

    executed_order = []

    async def mock_handler(payload: dict) -> None:
        executed_order.append(payload["name"])

    qm.register_handler("job", mock_handler)

    # Enqueue low priority first, then high priority
    await qm.enqueue("job", {"name": "low_priority"}, priority=10)
    await qm.enqueue("job", {"name": "high_priority"}, priority=1)

    await qm.process_next()
    await qm.process_next()

    assert executed_order == ["high_priority", "low_priority"]


@pytest.mark.asyncio
async def test_task_scheduler_delayed_job() -> None:
    qm = TaskQueueManager()
    scheduler = TaskScheduler(queue_manager=qm)

    await scheduler.schedule_job(job_id="job-abc", cron_or_delay="0.1")
    await asyncio.sleep(0.2)

    assert qm.get_task_status("job-abc") is None  # Enqueued with generated task_id
    assert not qm._queue.empty()


@pytest.mark.asyncio
async def test_task_scheduler_cancel_job() -> None:
    scheduler = TaskScheduler()
    await scheduler.schedule_job(job_id="job-to-cancel", cron_or_delay="5.0")

    canceled = await scheduler.cancel_job("job-to-cancel")
    assert canceled is True

    canceled_again = await scheduler.cancel_job("job-to-cancel")
    assert canceled_again is False
