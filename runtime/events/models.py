"""StoryForge Event Models for Async Pub/Sub Messaging."""

import uuid
from datetime import datetime
from typing import Any, Dict


class StoryForgeEvent:
    """Base event model for all system events."""

    def __init__(self, event_type: str, topic: str, payload: Dict[str, Any], event_id: str | None = None):
        self.event_id = event_id or str(uuid.uuid4())
        self.event_type = event_type
        self.topic = topic
        self.payload = payload
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "topic": self.topic,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }


class JobProgressEvent(StoryForgeEvent):
    """Event emitted during background task execution."""

    def __init__(self, task_id: str, project_id: str, step_name: str, percent_complete: float, message: str):
        super().__init__(
            event_type="job_progress",
            topic=f"job.{task_id}.progress",
            payload={
                "task_id": task_id,
                "project_id": project_id,
                "step_name": step_name,
                "percent_complete": percent_complete,
                "message": message,
            },
        )


class AgentMessageEvent(StoryForgeEvent):
    """Event emitted for inter-agent communication."""

    def __init__(self, sender_agent: str, receiver_agent: str, message_type: str, content: Dict[str, Any]):
        super().__init__(
            event_type="agent_message",
            topic=f"agent.{receiver_agent}.inbox",
            payload={
                "sender_agent": sender_agent,
                "receiver_agent": receiver_agent,
                "message_type": message_type,
                "content": content,
            },
        )


class ArtifactCreatedEvent(StoryForgeEvent):
    """Event emitted when a media or text artifact is generated."""

    def __init__(self, project_id: str, artifact_id: str, artifact_type: str, storage_url: str):
        super().__init__(
            event_type="artifact_created",
            topic=f"project.{project_id}.artifacts",
            payload={
                "project_id": project_id,
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "storage_url": storage_url,
            },
        )
