"""Runtime Engine Gateway Router for StoryForge."""

from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from ..schemas import (
    CapabilityExecuteRequest,
    PlanGenerateRequest,
    PlanNodeResponse,
    PlanResponse,
    TaskStatusResponse,
)

from ..auth import get_current_user
from runtime.planner import AgentPlannerEngine
from runtime.scheduler import TaskQueueManager
from runtime.registry.store import CapabilityRegistry
from runtime.execution import ExecutionRunner

# Capabilities can call paid/rate-limited services, so require a signed-in user.
router = APIRouter(prefix="/api/v1/runtime", tags=["Runtime Engine"], dependencies=[Depends(get_current_user)])

planner_engine = AgentPlannerEngine()
queue_manager = TaskQueueManager()
runner = ExecutionRunner()


@router.post("/plan", response_model=PlanResponse)
async def generate_plan(req: PlanGenerateRequest) -> PlanResponse:
    """Generate a validated storytelling DAG plan for an objective."""
    plan = await planner_engine.create_plan(
        goal=req.goal, context={"content_pack": req.content_pack, "aspect_ratio": req.aspect_ratio}
    )

    steps = [
        PlanNodeResponse(
            node_id=node.node_id,
            capability_name=node.capability_name,
            dependencies=node.dependencies,
            input_params=node.input_params,
            output_keys=node.output_keys,
            status=node.status,
        )
        for node in plan.nodes.values()
    ]

    return PlanResponse(plan_id=plan.plan_id, goal=plan.goal, steps=steps)


@router.post("/execute", response_model=Dict[str, Any])
async def execute_capability(req: CapabilityExecuteRequest) -> Dict[str, Any]:
    """Submit capability execution or enqueue background job."""
    if req.run_in_background:
        task = await queue_manager.enqueue(job_name=req.capability_name, payload=req.kwargs)
        return {"status": "enqueued", "task_id": task.task_id}
    else:
        try:
            cap = CapabilityRegistry.get_capability(req.capability_name)
        except KeyError:
            raise HTTPException(status_code=404, detail=f"Capability '{req.capability_name}' not registered.")

        step_result = await runner.execute_capability(step_id="step-api", capability=cap, kwargs=req.kwargs)
        return {
            "status": "completed" if step_result.success else "failed",
            "capability_name": req.capability_name,
            "result": step_result.output,
            "error": step_result.error,
            "duration_ms": step_result.duration_ms,
        }


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str) -> TaskStatusResponse:
    """Query background task progress and status."""
    task = queue_manager.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task '{task_id}' not found.")
    return TaskStatusResponse(
        task_id=task.task_id,
        job_name=task.job_name,
        status=task.status,
        result=task.result,
        error=task.error,
        created_at=task.created_at,
        completed_at=task.completed_at,
    )
