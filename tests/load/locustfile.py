"""Locust Load Testing Script for StoryForge API Gateway."""

import random
from locust import HttpUser, task, between


class CreatorUser(HttpUser):
    """Simulates concurrent creator users interacting with StoryForge API Gateway."""

    wait_time = between(1, 3)

    @task(3)
    def list_projects(self) -> None:
        """Simulate fetching recent story projects list."""
        self.client.get("/api/v1/projects", name="[GET] /api/v1/projects")

    @task(2)
    def create_project(self) -> None:
        """Simulate initializing a new story project."""
        payload = {
            "title": f"Load Test Story {random.randint(100, 999)}",
            "topic": "Quantum Computing and Artificial Intelligence",
            "content_pack_name": "technology",
            "aspect_ratio": "9:16",
        }
        self.client.post("/api/v1/projects", json=payload, name="[POST] /api/v1/projects")

    @task(1)
    def check_health(self) -> None:
        """Check API gateway health endpoint."""
        self.client.get("/health", name="[GET] /health")
