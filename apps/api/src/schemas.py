"""Pydantic v2 Request & Response Schemas for StoryForge API Gateway."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ProjectCreateRequest(BaseModel):
    title: str = Field(..., example="The Invention of Printing Press")
    topic: str = Field(..., example="How Gutenberg revolutionized information sharing")
    content_pack_name: str = Field(default="history", example="history")
    aspect_ratio: str = Field(default="9:16", example="9:16")


class ProjectResponse(BaseModel):
    id: str
    workspace_id: str
    creator_id: str
    title: str
    topic: str
    content_pack_name: str
    status: str
    created_at: str


class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total_count: int


class PlanGenerateRequest(BaseModel):
    goal: str = Field(..., example="Create a 60s Reel on Quantum Computers")
    content_pack: str = Field(default="technology", example="technology")
    aspect_ratio: str = Field(default="9:16", example="9:16")


class PlanNodeResponse(BaseModel):
    node_id: str
    capability_name: str
    dependencies: List[str]
    input_params: Dict[str, Any]
    output_keys: List[str]
    status: str


class PlanResponse(BaseModel):
    plan_id: str
    goal: str
    steps: List[PlanNodeResponse]


class CapabilityExecuteRequest(BaseModel):
    capability_name: str = Field(..., example="deep_research")
    kwargs: Dict[str, Any] = Field(default_factory=dict)
    run_in_background: bool = Field(default=False)


class TaskStatusResponse(BaseModel):
    task_id: str
    job_name: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None
