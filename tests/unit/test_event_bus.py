"""Event Bus Unit Tests."""

import pytest
from typing import List
from runtime.events import (
    EventBus,
    StoryForgeEvent,
    JobProgressEvent,
    AgentMessageEvent,
    ArtifactCreatedEvent,
)


@pytest.mark.asyncio
async def test_event_bus_topic_subscription() -> None:
    bus = EventBus()
    received: List[StoryForgeEvent] = []

    async def sample_handler(event: StoryForgeEvent) -> None:
        received.append(event)

    bus.subscribe("job.task-123.progress", sample_handler)

    event = JobProgressEvent(
        task_id="task-123",
        project_id="proj-456",
        step_name="script_writing",
        percent_complete=50.0,
        message="Generating script scene 3",
    )
    await bus.publish_event(event)

    assert len(received) == 1
    assert received[0].payload["task_id"] == "task-123"
    assert received[0].payload["percent_complete"] == 50.0


@pytest.mark.asyncio
async def test_event_bus_wildcard_subscription() -> None:
    bus = EventBus()
    received: List[StoryForgeEvent] = []

    async def wildcard_handler(event: StoryForgeEvent) -> None:
        received.append(event)

    bus.subscribe("*", wildcard_handler)

    event = ArtifactCreatedEvent(
        project_id="proj-1",
        artifact_id="art-100",
        artifact_type="image",
        storage_url="https://cloudinary.com/sample.png",
    )
    await bus.publish_event(event)

    assert len(received) == 1
    assert received[0].payload["artifact_id"] == "art-100"


@pytest.mark.asyncio
async def test_agent_message_event() -> None:
    event = AgentMessageEvent(
        sender_agent="researcher",
        receiver_agent="scriptwriter",
        message_type="research_summary",
        content={"facts": ["fact_1", "fact_2"]},
    )
    assert event.topic == "agent.scriptwriter.inbox"
    assert event.payload["sender_agent"] == "researcher"
    assert len(event.payload["content"]["facts"]) == 2
