"use client";

import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import PipelineProgress from "../../../components/PipelineProgress";
import VideoPreviewPlayer from "../../../components/VideoPreviewPlayer";
import SceneEditor, { EditableScene } from "../../../components/SceneEditor";
import EditorChat from "../../../components/EditorChat";
import {
  ApiError,
  chatEdit,
  deleteProject,
  getProject,
  Project,
  saveScenes,
  startGeneration,
} from "../../../lib/api";
import { useRequireAuth } from "../../../lib/useRequireAuth";

const EDITABLE_KEYS = ["heading", "narration", "visual_prompt", "on_screen_text"] as const;

function sceneKey(scenes: EditableScene[]): string {
  return JSON.stringify(scenes.map((s) => EDITABLE_KEYS.map((k) => s[k])));
}

export default function StudioPage() {
  const ready = useRequireAuth();
  const router = useRouter();
  const params = useParams();
  const projectId = params?.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [loadError, setLoadError] = useState("");
  const [actionError, setActionError] = useState("");
  const [scenes, setScenes] = useState<EditableScene[]>([]);
  const [savedKey, setSavedKey] = useState(() => sceneKey([]));
  const [busyAction, setBusyAction] = useState<"" | "save" | "render" | "regenerate" | "delete">("");
  const [chatBusy, setChatBusy] = useState(false);
  const [chatError, setChatError] = useState("");
  const dirtyRef = useRef(false);

  const jobActive = project?.job?.status === "queued" || project?.job?.status === "running";
  const dirty = sceneKey(scenes) !== savedKey;
  dirtyRef.current = dirty;

  const applyProject = useCallback((p: Project, forceScenes = false) => {
    setProject(p);
    // Don't clobber unsaved edits with polling results.
    if (forceScenes || !dirtyRef.current) {
      const next = p.script?.scenes || [];
      setScenes(next);
      setSavedKey(sceneKey(next));
    }
  }, []);

  const load = useCallback(async () => {
    try {
      applyProject(await getProject(projectId));
      setLoadError("");
    } catch (err) {
      setLoadError(err instanceof ApiError && err.status === 404 ? "This project doesn't exist or belongs to another account." : (err as Error).message);
    }
  }, [projectId, applyProject]);

  useEffect(() => {
    if (ready && projectId) load();
  }, [ready, projectId, load]);

  useEffect(() => {
    if (!jobActive) return;
    const id = setInterval(load, 3000);
    return () => clearInterval(id);
  }, [jobActive, load]);

  const run = async (action: typeof busyAction, fn: () => Promise<void>) => {
    setBusyAction(action);
    setActionError("");
    try {
      await fn();
    } catch (err) {
      setActionError((err as Error).message);
    } finally {
      setBusyAction("");
    }
  };

  const persistScenes = async () => {
    const payload = scenes.map((s) => ({
      heading: s.heading.trim() || "Scene",
      narration: s.narration.trim(),
      visual_prompt: s.visual_prompt.trim() || s.narration.trim(),
      on_screen_text: s.on_screen_text.trim(),
    }));
    if (payload.some((s) => !s.narration)) throw new Error("Every scene needs narration text.");
    const updated = await saveScenes(projectId, payload);
    applyProject(updated, true);
    return updated;
  };

  const handleSave = () => run("save", async () => void (await persistScenes()));

  const handleRender = () =>
    run("render", async () => {
      const regen = scenes.flatMap((s, i) => (s.regenerateImage ? [i] : []));
      if (dirty) await persistScenes();
      applyProject(await startGeneration(projectId, "rerender", regen), true);
    });

  const handleRegenerate = () => {
    const hasScript = (project?.script?.scenes?.length || 0) > 0;
    if (hasScript && !window.confirm("Write a brand-new script and images from scratch? Your current script edits will be replaced.")) return;
    run("regenerate", async () => applyProject(await startGeneration(projectId, "full"), true));
  };

  const handleDelete = () => {
    if (!window.confirm("Delete this project and its video? This can't be undone.")) return;
    run("delete", async () => {
      await deleteProject(projectId);
      router.push("/");
    });
  };

  const handleChat = async (message: string) => {
    setChatBusy(true);
    setChatError("");
    try {
      if (dirty) await persistScenes();
      const res = await chatEdit(projectId, message);
      applyProject(res.project, true);
    } catch (err) {
      setChatError((err as Error).message);
    } finally {
      setChatBusy(false);
    }
  };

  const script = project?.script;
  const totalWords = useMemo(() => scenes.reduce((n, s) => n + (s.narration.trim() ? s.narration.trim().split(/\s+/).length : 0), 0), [scenes]);

  if (loadError) {
    return (
      <div className="max-w-lg mx-auto glass-card rounded-2xl p-8 text-center border border-slate-800">
        <p className="text-sm text-rose-300 mb-4">{loadError}</p>
        <div className="flex justify-center gap-3">
          <button onClick={load} className="px-4 py-2 rounded-xl bg-slate-800 text-xs font-semibold">Retry</button>
          <Link href="/" className="px-4 py-2 rounded-xl gradient-button text-xs font-bold text-white">Back to projects</Link>
        </div>
      </div>
    );
  }

  if (!project) {
    return <div className="text-center py-16 text-slate-400 text-sm animate-pulse">Loading project…</div>;
  }

  const locked = jobActive || busyAction !== "";
  const hasScript = scenes.length > 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-end justify-between pb-4 border-b border-slate-800 gap-4">
        <div className="min-w-0">
          <Link href="/" className="text-xs font-semibold text-indigo-400 hover:text-indigo-300">← All projects</Link>
          <h1 className="text-2xl font-extrabold text-white mt-1 break-words">{project.title}</h1>
          <p className="text-xs text-slate-400 mt-1 line-clamp-2">{project.topic}</p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button onClick={handleDelete} disabled={locked} className="px-3 py-2 rounded-xl text-xs font-semibold text-rose-300 hover:bg-rose-500/10 disabled:opacity-40">
            Delete
          </button>
          <button onClick={handleRegenerate} disabled={locked} className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 disabled:opacity-40">
            {hasScript ? "New script" : "Generate video"}
          </button>
          {hasScript && (
            <button onClick={handleRender} disabled={locked} className="gradient-button px-5 py-2 rounded-xl text-xs font-bold text-white shadow-lg disabled:opacity-50">
              {jobActive ? "Rendering…" : busyAction === "render" ? "Starting…" : dirty ? "Save & re-render" : "Re-render video"}
            </button>
          )}
        </div>
      </div>

      {actionError && (
        <div role="alert" className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">{actionError}</div>
      )}

      {project.job && <PipelineProgress job={project.job} />}

      {script?.warning && !jobActive && (
        <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-200 text-xs">
          No AI writer was reachable, so a basic script was assembled from Wikipedia. Add a free Gemini or Groq key in your server
          settings for much better scripts.
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <VideoPreviewPlayer
            video={project.video}
            poster={project.thumbnail_url}
            aspectRatio={project.aspect_ratio}
            title={project.title}
            busy={jobActive}
            stale={project.stale}
          />
          <EditorChat history={project.chat || []} onSendMessage={handleChat} isProcessing={chatBusy} disabled={!hasScript || locked} error={chatError} />

          {script?.sources && script.sources.length > 0 && (
            <div className="glass-card rounded-2xl p-5 border border-slate-800">
              <h3 className="font-bold text-sm text-slate-300 uppercase tracking-wider mb-3">Research sources</h3>
              <ul className="space-y-1.5">
                {script.sources.map((s) => (
                  <li key={s.url}>
                    <a href={s.url} target="_blank" rel="noreferrer" className="text-xs text-indigo-300 hover:underline">{s.title} ↗</a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="lg:col-span-3 space-y-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="font-bold text-sm text-slate-300 uppercase tracking-wider">Script &amp; scenes</h2>
              {hasScript && (
                <p className="text-[11px] text-slate-500 mt-0.5">
                  {scenes.length} scenes · {totalWords} words · ~{Math.round(totalWords / 2.5)}s
                  {script?.provider && ` · written by ${script.provider}`}
                </p>
              )}
            </div>
            {hasScript && (
              <button
                onClick={handleSave}
                disabled={!dirty || locked}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 disabled:opacity-40"
              >
                {busyAction === "save" ? "Saving…" : dirty ? "Save changes" : "Saved"}
              </button>
            )}
          </div>

          {hasScript ? (
            <SceneEditor scenes={scenes} onChange={setScenes} disabled={locked} />
          ) : (
            <div className="glass-card rounded-2xl p-10 text-center border border-slate-800 text-sm text-slate-400">
              {jobActive ? "The script will appear here as soon as it's written." : "No script yet. Click “Generate video” to start."}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
