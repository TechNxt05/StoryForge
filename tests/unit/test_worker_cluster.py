"""Worker Cluster Unit Tests."""

import pytest
from apps.worker.src import DistributedWorkerCluster, WorkerNode


def test_worker_node_availability() -> None:
    node = WorkerNode(node_id="node-1", queues=["rendering_queue"], max_concurrency=2)
    assert node.is_available("rendering_queue") is True
    assert node.is_available("generation_queue") is False

    node.active_slots = 2
    assert node.is_available("rendering_queue") is False


def test_distributed_worker_cluster_dispatch() -> None:
    cluster = DistributedWorkerCluster()

    # Register worker node 2
    n2 = WorkerNode(node_id="worker-node-2", queues=["generation_queue"], max_concurrency=4)
    cluster.register_node(n2)

    dispatch_res = cluster.dispatch_task("generation_queue", {"task_name": "generate_image"})
    assert dispatch_res["status"] == "dispatched"
    assert dispatch_res["assigned_node_id"] in ["worker-local-1", "worker-node-2"]

    # Release slot
    cluster.complete_task(dispatch_res["assigned_node_id"])
    status = cluster.get_cluster_status()
    assert status["total_nodes"] == 2
    assert status["active_slots"] == 0
