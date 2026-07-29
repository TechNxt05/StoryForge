"""Planner Engine Unit Tests."""

import pytest
from runtime.planner import AgentPlannerEngine, DAGPlan, TaskNode


def test_task_node_creation() -> None:
    node = TaskNode(
        node_id="step-1",
        capability_name="research",
        dependencies=[],
        input_params={"topic": "AI"},
        output_keys=["facts"],
    )
    data = node.to_dict()
    assert data["node_id"] == "step-1"
    assert data["capability_name"] == "research"


def test_dag_topological_sort() -> None:
    plan = DAGPlan(plan_id="plan-1", goal="Create Video")

    n1 = TaskNode(node_id="n1", capability_name="cap1")
    n2 = TaskNode(node_id="n2", capability_name="cap2", dependencies=["n1"])
    n3 = TaskNode(node_id="n3", capability_name="cap3", dependencies=["n1"])
    n4 = TaskNode(node_id="n4", capability_name="cap4", dependencies=["n2", "n3"])

    plan.add_node(n1)
    plan.add_node(n2)
    plan.add_node(n3)
    plan.add_node(n4)

    assert plan.validate_dag() is True

    stages = plan.get_execution_order()
    assert len(stages) == 3
    assert [node.node_id for node in stages[0]] == ["n1"]
    assert set(node.node_id for node in stages[1]) == {"n2", "n3"}
    assert [node.node_id for node in stages[2]] == ["n4"]


def test_dag_cycle_detection() -> None:
    plan = DAGPlan(plan_id="cycle-plan", goal="Test Cycle")

    n1 = TaskNode(node_id="n1", capability_name="cap1", dependencies=["n2"])
    n2 = TaskNode(node_id="n2", capability_name="cap2", dependencies=["n1"])

    plan.add_node(n1)
    plan.add_node(n2)

    assert plan.validate_dag() is False
    with pytest.raises(ValueError, match="circular dependencies"):
        plan.get_execution_order()


@pytest.mark.asyncio
async def test_agent_planner_engine() -> None:
    planner = AgentPlannerEngine()
    plan = await planner.create_plan(goal="Rise of Quantum Computing", context={"content_pack": "tech"})

    assert plan.validate_dag() is True
    stages = plan.get_execution_order()
    assert len(stages) >= 4

    steps = await planner.generate_plan_steps("Quantum Computing")
    assert len(steps) == 6
    assert steps[0]["node_id"] == "step-1-research"
