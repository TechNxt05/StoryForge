"""Core StoryForge Runtime Engine."""

from typing import Any, Dict, List
from .interfaces import IArtifact, IWorkflow
from .registry.store import CapabilityRegistry
from .execution.runner import ExecutionRunner, StepExecutionResult


class StoryForgeRuntimeEngine:
    """Central orchestration engine for executing storytelling workflows and capabilities."""

    def __init__(self) -> None:
        self.registry = CapabilityRegistry()
        self.runner = ExecutionRunner()

    async def execute_capability(
        self, capability_name: str, kwargs: Dict[str, Any], step_id: str = "step-01"
    ) -> StepExecutionResult:
        """Resolve a capability by name and execute it with input arguments."""
        capability = self.registry.get_capability(capability_name)
        return await self.runner.execute_capability(step_id=step_id, capability=capability, kwargs=kwargs)

    async def run_workflow(self, workflow: IWorkflow, input_data: Dict[str, Any]) -> List[IArtifact]:
        """Execute a storytelling workflow end-to-end and return generated artifacts."""
        return await workflow.run(input_data)
