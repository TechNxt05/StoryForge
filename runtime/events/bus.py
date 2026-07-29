"""Async Event Bus Implementation for StoryForge Runtime."""

import asyncio
from typing import Any, Callable, Coroutine, Dict, List
from ..interfaces import IEventBus
from .models import StoryForgeEvent

EventHandler = Callable[[StoryForgeEvent], Coroutine[Any, Any, None]]


class EventBus(IEventBus):
    """In-memory and async Pub/Sub Event Bus for routing system events."""

    def __init__(self) -> None:
        self._subscribers: Dict[str, List[EventHandler]] = {}

    def subscribe(self, topic: str, handler: EventHandler) -> None:
        """Subscribe a coroutine handler to a specific topic or wildcard ('*')."""
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)

    def unsubscribe(self, topic: str, handler: EventHandler) -> None:
        """Unsubscribe a handler from a topic."""
        if topic in self._subscribers and handler in self._subscribers[topic]:
            self._subscribers[topic].remove(handler)

    async def publish_event(self, event: StoryForgeEvent) -> None:
        """Publish a StoryForgeEvent to matching subscribers."""
        handlers_to_call: List[EventHandler] = []

        # Direct topic match
        if event.topic in self._subscribers:
            handlers_to_call.extend(self._subscribers[event.topic])

        # Global wildcard subscribers
        if "*" in self._subscribers:
            handlers_to_call.extend(self._subscribers["*"])

        # Execute handlers concurrently
        if handlers_to_call:
            await asyncio.gather(*(handler(event) for handler in handlers_to_call), return_exceptions=True)

    async def publish(self, topic: str, message: dict[str, Any]) -> None:
        """Implementation of IEventBus interface publish method."""
        event = StoryForgeEvent(event_type="raw_message", topic=topic, payload=message)
        await self.publish_event(event)

    def clear(self) -> None:
        """Clear all subscribers."""
        self._subscribers.clear()
