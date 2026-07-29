"""Directed Acyclic Graph (DAG) Task Graph Models and Topological Resolver."""

from typing import Any, Dict, List, Set


class TaskNode:
    """Represents a single executable node in an agent task graph."""

    def __init__(
        self,
        node_id: str,
        capability_name: str,
        dependencies: List[str] | None = None,
        input_params: Dict[str, Any] | None = None,
        output_keys: List[str] | None = None,
    ):
        self.node_id = node_id
        self.capability_name = capability_name
        self.dependencies = dependencies or []
        self.input_params = input_params or {}
        self.output_keys = output_keys or []
        self.status = "pending"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "capability_name": self.capability_name,
            "dependencies": self.dependencies,
            "input_params": self.input_params,
            "output_keys": self.output_keys,
            "status": self.status,
        }


class DAGPlan:
    """Collection of TaskNodes forming a Directed Acyclic Graph plan."""

    def __init__(self, plan_id: str, goal: str):
        self.plan_id = plan_id
        self.goal = goal
        self.nodes: Dict[str, TaskNode] = {}

    def add_node(self, node: TaskNode) -> None:
        """Add a task node to the DAG plan."""
        self.nodes[node.node_id] = node

    def validate_dag(self) -> bool:
        """Check whether the plan forms a valid DAG without circular dependencies."""
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def is_cyclic(node_id: str) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)

            node = self.nodes.get(node_id)
            if node:
                for dep in node.dependencies:
                    if dep not in visited:
                        if is_cyclic(dep):
                            return True
                    elif dep in rec_stack:
                        return True

            rec_stack.remove(node_id)
            return False

        for node_id in self.nodes:
            if node_id not in visited:
                if is_cyclic(node_id):
                    return False
        return True

    def get_execution_order(self) -> List[List[TaskNode]]:
        """Return task nodes grouped in topological execution stages."""
        if not self.validate_dag():
            raise ValueError(f"Plan '{self.plan_id}' contains circular dependencies in DAG.")

        resolved: Set[str] = set()
        stages: List[List[TaskNode]] = []

        remaining = set(self.nodes.keys())
        while remaining:
            # Nodes whose dependencies are all resolved
            ready_nodes = [
                self.nodes[nid]
                for nid in remaining
                if all(dep in resolved for dep in self.nodes[nid].dependencies)
            ]

            if not ready_nodes:
                raise ValueError("Unresolvable dependency deadlock detected.")

            stages.append(ready_nodes)
            for node in ready_nodes:
                resolved.add(node.node_id)
                remaining.remove(node.node_id)

        return stages
