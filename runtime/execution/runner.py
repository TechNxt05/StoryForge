"""Step Execution Runner for StoryForge Runtime."""

import time
from typing import Any, Dict
from ..interfaces import ICapability


class StepExecutionResult:
    """Encapsulates the output of a capability step execution."""

    def __init__(self, step_id: str, success: bool, output: Any, duration_ms: float, error: str | None = None):
        self.step_id = step_id
        self.success = success
        self.output = output
        self.duration_ms = duration_ms
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "success": self.success,
            "output": self.output,
            "duration_ms": self.duration_ms,
            "error": self.error,
        }


class ExecutionRunner:
    """Executes single or sequential capability steps with timing and error isolation."""

    @staticmethod
    async def execute_capability(
        step_id: str, capability: ICapability, kwargs: Dict[str, Any]
    ) -> StepExecutionResult:
        start_time = time.perf_counter()
        try:
            output = await capability.execute(**kwargs)
            duration_ms = (time.perf_counter() - start_time) * 1000
            return StepExecutionResult(step_id=step_id, success=True, output=output, duration_ms=duration_ms)
        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            return StepExecutionResult(
                step_id=step_id, success=False, output=None, duration_ms=duration_ms, error=str(exc)
            )
