"""In-process background job runner for story generation.

Free hosting (e.g. Render free) gives one small instance, so jobs run as asyncio
tasks inside the API process, limited by a semaphore. Progress is persisted to
the project's metadata_json so the UI can poll it and so it survives page reloads.
"""

import asyncio
import copy
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from sqlalchemy import delete, select

from runtime import pipeline
from .database.postgres import Asset as DBAsset, AsyncSessionLocal, Project as DBProject

logger = logging.getLogger("storyforge.jobs")

_semaphore = asyncio.Semaphore(int(os.getenv("MAX_CONCURRENT_JOBS", "1")))
_tasks: Dict[str, asyncio.Task] = {}

ACTIVE_STATUSES = {"queued", "generating"}


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def is_running(project_id: str) -> bool:
    task = _tasks.get(project_id)
    return bool(task and not task.done())


async def update_project(project_id: str, mutate: Callable[[Dict[str, Any]], None], status: Optional[str] = None) -> None:
    """Apply `mutate` to a deep copy of metadata_json and save it (new object so SQLAlchemy sees the change)."""
    async with AsyncSessionLocal() as session:
        project = await session.get(DBProject, project_id)
        if not project:
            return
        meta = copy.deepcopy(project.metadata_json or {})
        mutate(meta)
        project.metadata_json = meta
        if status:
            project.status = status
        await session.commit()


def _fresh_steps() -> Dict[str, Dict[str, Any]]:
    return {name: {"label": label, "status": "pending"} for name, label in pipeline.STEPS}


async def start_generation(project_id: str, mode: str = "full", regenerate_images: Optional[List[int]] = None) -> None:
    """Queue a generation run. mode='full' writes a new script; 'rerender' reuses the current (edited) script."""
    if is_running(project_id):
        raise RuntimeError("A generation is already running for this project.")

    def queue(meta: Dict[str, Any]) -> None:
        meta["job"] = {
            "mode": mode,
            "status": "queued",
            "steps": _fresh_steps(),
            "queued_at": now_iso(),
            "error": None,
        }

    await update_project(project_id, queue, status="queued")
    _tasks[project_id] = asyncio.create_task(_run(project_id, mode, set(regenerate_images or [])))


async def _run(project_id: str, mode: str, regenerate_images: set[int]) -> None:
    async with _semaphore:
        async with AsyncSessionLocal() as session:
            project = await session.get(DBProject, project_id)
            if not project:
                return
            meta = copy.deepcopy(project.metadata_json or {})
            title, topic, pack = project.title, project.topic, project.content_pack_name

        settings = meta.get("settings", {})
        previous_script = meta.get("script")
        if mode == "rerender" and not (previous_script and previous_script.get("scenes")):
            mode = "full"

        def start(m: Dict[str, Any]) -> None:
            m["job"]["status"] = "running"
            m["job"]["started_at"] = now_iso()

        await update_project(project_id, start, status="generating")

        async def report(step: str, **fields: Any) -> None:
            script = fields.pop("script", None)
            scenes = fields.pop("scenes", None)

            def apply(m: Dict[str, Any]) -> None:
                entry = m["job"]["steps"].setdefault(step, {"label": step})
                if fields.get("status") == "running" and entry.get("status") != "running":
                    entry["started_at"] = now_iso()
                if fields.get("status") in ("completed", "skipped"):
                    entry["finished_at"] = now_iso()
                entry.update({k: v for k, v in fields.items() if v is not None})
                if script is not None:
                    m["script"] = copy.deepcopy(script)
                if scenes is not None and m.get("script"):
                    m["script"]["scenes"] = copy.deepcopy(scenes)

            await update_project(project_id, apply)

        try:
            result = await pipeline.run_pipeline(
                project_id=project_id,
                title=title,
                topic=topic,
                pack=pack,
                aspect_ratio=settings.get("aspect_ratio", "9:16"),
                notes=settings.get("notes", ""),
                target_seconds=int(settings.get("target_seconds", 45)),
                voice=settings.get("voice", "en-US-AndrewNeural"),
                language=settings.get("language", "English"),
                existing_script=previous_script if mode == "rerender" else None,
                previous_scenes=(previous_script or {}).get("scenes") if mode == "rerender" else None,
                regenerate_images=regenerate_images,
                report=report,
            )
        except Exception as exc:
            logger.exception("Generation failed for %s", project_id)
            message = str(exc)[:500] or type(exc).__name__

            def fail(m: Dict[str, Any]) -> None:
                m["job"]["status"] = "failed"
                m["job"]["error"] = message
                m["job"]["finished_at"] = now_iso()
                for step in m["job"]["steps"].values():
                    if step.get("status") == "running":
                        step["status"] = "failed"

            await update_project(project_id, fail, status="failed")
            return
        finally:
            _tasks.pop(project_id, None)

        def finish(m: Dict[str, Any]) -> None:
            m["script"] = result["script"]
            m["video"] = {**result["video"], "created_at": now_iso()}
            m["providers"] = result["providers"]
            m["job"]["status"] = "completed"
            m["job"]["finished_at"] = now_iso()
            m["stale"] = False
            history = m.setdefault("history", [])
            history.insert(0, {"url": result["video"]["url"], "duration": result["video"]["duration"], "at": now_iso()})
            del history[5:]

        await update_project(project_id, finish, status="completed")
        await _record_assets(project_id, result)


async def _record_assets(project_id: str, result: Dict[str, Any]) -> None:
    """Mirror the generated outputs into the assets table for the asset library."""
    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(DBAsset).where(DBAsset.project_id == project_id, DBAsset.provider_name != "user_upload")
        )
        video = result["video"]
        session.add(
            DBAsset(
                project_id=project_id,
                asset_type="video",
                provider_name=f"ffmpeg/{video['storage']}",
                storage_url=video["url"],
                file_size_bytes=int(video.get("bytes", 0)),
                mime_type="video/mp4",
                metadata_json={"duration": video["duration"], "width": video["width"], "height": video["height"]},
            )
        )
        for i, scene in enumerate(result["script"]["scenes"]):
            if not scene.get("image_url"):
                continue
            path = Path(scene.get("image_path", ""))
            session.add(
                DBAsset(
                    project_id=project_id,
                    asset_type="image",
                    provider_name=scene.get("image_provider", "unknown"),
                    storage_url=scene["image_url"],
                    file_size_bytes=path.stat().st_size if path.is_file() else 0,
                    mime_type="image/png" if path.suffix == ".png" else "image/jpeg",
                    metadata_json={"scene": i + 1, "prompt": scene.get("visual_prompt", "")},
                )
            )
        await session.commit()


async def recover_interrupted_jobs() -> int:
    """Mark jobs that were running when the server stopped as failed, so users can retry."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(DBProject).where(DBProject.status.in_(ACTIVE_STATUSES)))
        projects = result.scalars().all()
        for project in projects:
            meta = copy.deepcopy(project.metadata_json or {})
            job = meta.setdefault("job", {})
            job["status"] = "failed"
            job["error"] = "The server restarted while this video was generating (free instances sleep when idle). Please run it again."
            project.metadata_json = meta
            project.status = "failed"
        await session.commit()
        return len(projects)
