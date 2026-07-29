"""Shared runtime types and contracts."""
from typing import Any, TypedDict


class RuntimeContext(TypedDict):
    project_id: str
    session_id: str
    metadata: dict[str, Any]
