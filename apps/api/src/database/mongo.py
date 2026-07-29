"""MongoDB Connection Pool & Document Models for StoryForge."""

import os
from typing import Any


def get_mongo_uri() -> str:
    return os.getenv("MONGODB_URI", "mongodb://localhost:27017/storyforge")


class MongoCollectionNames:
    SCRIPT_REVISIONS = "script_revisions"
    STORYBOARDS = "storyboards"
    WORKFLOW_TRAJECTORIES = "workflow_trajectories"
    RAW_RESEARCH_ARTIFACTS = "raw_research_artifacts"


def get_mongo_db() -> dict[str, Any]:
    """MongoDB connection configuration skeleton."""
    return {
        "uri": get_mongo_uri(),
        "database_name": "storyforge",
        "collections": [
            MongoCollectionNames.SCRIPT_REVISIONS,
            MongoCollectionNames.STORYBOARDS,
            MongoCollectionNames.WORKFLOW_TRAJECTORIES,
            MongoCollectionNames.RAW_RESEARCH_ARTIFACTS,
        ],
    }
