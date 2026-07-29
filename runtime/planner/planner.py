"""Agent Planner Engine Implementation for StoryForge Runtime."""

import uuid
from typing import Any, Dict, List
from ..interfaces import IPlanner
from .interfaces import IPlannerEngine
from .dag import DAGPlan, TaskNode


class AgentPlannerEngine(IPlanner, IPlannerEngine):
    """LLM & Rule-Driven Agent Planner constructing validated DAG task plans."""

    async def create_plan(self, goal: str, context: Dict[str, Any]) -> DAGPlan:
        """Construct a validated DAGPlan for a given storytelling goal."""
        plan_id = f"plan-{uuid.uuid4().hex[:8]}"
        plan = DAGPlan(plan_id=plan_id, goal=goal)

        content_pack = context.get("content_pack", "technology")

        # Step 1: Research Node
        node_research = TaskNode(
            node_id="step-1-research",
            capability_name="deep_research",
            dependencies=[],
            input_params={"topic": goal, "content_pack": content_pack},
            output_keys=["research_facts"],
        )

        # Step 2: Story Structure Node
        node_structure = TaskNode(
            node_id="step-2-structure",
            capability_name="story_structure_planner",
            dependencies=["step-1-research"],
            input_params={"topic": goal},
            output_keys=["story_outline"],
        )

        # Step 3: Script Writing Node
        node_script = TaskNode(
            node_id="step-3-script",
            capability_name="scriptwriter",
            dependencies=["step-2-structure"],
            input_params={"aspect_ratio": context.get("aspect_ratio", "9:16")},
            output_keys=["script_scenes"],
        )

        # Step 4: Storyboard & Audio Nodes (Parallel Stage)
        node_storyboard = TaskNode(
            node_id="step-4a-storyboard",
            capability_name="storyboard_generator",
            dependencies=["step-3-script"],
            input_params={},
            output_keys=["storyboard_frames"],
        )

        node_audio = TaskNode(
            node_id="step-4b-audio",
            capability_name="tts_audio_synthesizer",
            dependencies=["step-3-script"],
            input_params={},
            output_keys=["narration_audio_url"],
        )

        # Step 5: Video Composition Node
        node_render = TaskNode(
            node_id="step-5-render",
            capability_name="video_renderer",
            dependencies=["step-4a-storyboard", "step-4b-audio"],
            input_params={},
            output_keys=["final_video_url"],
        )

        # Register all nodes
        for node in [node_research, node_structure, node_script, node_storyboard, node_audio, node_render]:
            plan.add_node(node)

        return plan

    async def generate_plan_steps(self, objective: str) -> List[Dict[str, Any]]:
        """Implementation of IPlannerEngine interface returning list of plan step dicts."""
        plan = await self.create_plan(goal=objective, context={})
        stages = plan.get_execution_order()
        steps: List[Dict[str, Any]] = []
        for stage in stages:
            for node in stage:
                steps.append(node.to_dict())
        return steps
