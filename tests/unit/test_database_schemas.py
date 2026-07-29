"""Database Schemas & Models Unit Tests."""

from apps.api.src.database.postgres import (
    User,
    Workspace,
    Project,
    Story,
    Asset,
    Subscription,
    AuditLog,
)
from apps.api.src.database.mongo import MongoCollectionNames, get_mongo_db
from apps.api.src.database.redis import get_redis_url
from apps.api.src.database.qdrant import QdrantCollections, get_qdrant_client


def test_postgres_table_names() -> None:
    """Verify SQLAlchemy declarative model table names."""
    assert User.__tablename__ == "users"
    assert Workspace.__tablename__ == "workspaces"
    assert Project.__tablename__ == "projects"
    assert Story.__tablename__ == "stories"
    assert Asset.__tablename__ == "assets"
    assert Subscription.__tablename__ == "subscriptions"
    assert AuditLog.__tablename__ == "audit_logs"


def test_mongo_collections() -> None:
    """Verify MongoDB collection names."""
    db_config = get_mongo_db()
    assert MongoCollectionNames.SCRIPT_REVISIONS in db_config["collections"]
    assert MongoCollectionNames.STORYBOARDS in db_config["collections"]
    assert MongoCollectionNames.WORKFLOW_TRAJECTORIES in db_config["collections"]


def test_redis_config() -> None:
    """Verify Redis URL config builder."""
    url = get_redis_url()
    assert "redis://" in url


def test_qdrant_collections() -> None:
    """Verify Qdrant vector database collections setup."""
    client_config = get_qdrant_client()
    assert QdrantCollections.STORY_KNOWLEDGE in client_config["collections"]
    assert QdrantCollections.SCRIPT_CHUNKS in client_config["collections"]
    assert client_config["vector_size"] == 1536
