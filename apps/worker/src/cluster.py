"""Distributed Worker Cluster & Queue Load Balancer for StoryForge Worker."""

import time
import uuid
from typing import Any, Dict, List, Optional


class WorkerNode:
    """Represents a distributed worker node instance in the cluster."""

    def __init__(
        self,
        node_id: Optional[str] = None,
        queues: Optional[List[str]] = None,
        max_concurrency: int = 4,
    ):
        self.node_id = node_id or f"node-{uuid.uuid4().hex[:6]}"
        self.queues = queues or ["default_queue", "generation_queue", "rendering_queue"]
        self.max_concurrency = max_concurrency
        self.active_slots = 0
        self.last_heartbeat = time.time()
        self.status = "healthy"  # healthy, busy, offline

    def is_available(self, queue_name: str) -> bool:
        """Check if node can accept a task from a specific queue."""
        if self.status != "healthy":
            return False
        if queue_name not in self.queues:
            return False
        return self.active_slots < self.max_concurrency

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "queues": self.queues,
            "max_concurrency": self.max_concurrency,
            "active_slots": self.active_slots,
            "available_slots": self.max_concurrency - self.active_slots,
            "last_heartbeat": self.last_heartbeat,
            "status": self.status,
        }


class DistributedWorkerCluster:
    """Manages worker cluster nodes, queue routing, and load balancing."""

    def __init__(self) -> None:
        self.nodes: Dict[str, WorkerNode] = {}
        # Register a default local worker node
        self.register_node(WorkerNode(node_id="worker-local-1", max_concurrency=8))

    def register_node(self, node: WorkerNode) -> None:
        """Register or update a worker node in the cluster."""
        self.nodes[node.node_id] = node

    def dispatch_task(self, queue_name: str, task_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch task to the most available worker node supporting the target queue."""
        available_nodes = [
            n for n in self.nodes.values() if n.is_available(queue_name)
        ]

        if not available_nodes:
            # Fallback allocation to local worker node
            target_node = self.nodes.get("worker-local-1") or list(self.nodes.values())[0]
        else:
            # Sort by least busy (most available slots)
            available_nodes.sort(key=lambda n: n.max_concurrency - n.active_slots, reverse=True)
            target_node = available_nodes[0]

        target_node.active_slots += 1

        return {
            "status": "dispatched",
            "queue": queue_name,
            "assigned_node_id": target_node.node_id,
            "node_available_slots": target_node.max_concurrency - target_node.active_slots,
            "task_payload": task_payload,
        }

    def complete_task(self, node_id: str) -> None:
        """Release active slot on a worker node upon task completion."""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.active_slots = max(0, node.active_slots - 1)

    def get_cluster_status(self) -> Dict[str, Any]:
        """Retrieve overall cluster status metrics."""
        total_slots = sum(n.max_concurrency for n in self.nodes.values())
        used_slots = sum(n.active_slots for n in self.nodes.values())

        return {
            "total_nodes": len(self.nodes),
            "total_concurrency_slots": total_slots,
            "active_slots": used_slots,
            "available_slots": total_slots - used_slots,
            "nodes": [n.to_dict() for n in self.nodes.values()],
        }
