"use client";

import React, { useCallback, useEffect, useState } from "react";
import CreateProjectModal from "../components/CreateProjectModal";
import ProjectGrid from "../components/ProjectGrid";
import { getProjects, ProjectSummary } from "../lib/api";
import { useRequireAuth } from "../lib/useRequireAuth";

export default function StudioDashboard() {
  const ready = useRequireAuth();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [projects, setProjects] = useState<ProjectSummary[]>([]);

  const loadProjects = useCallback(async () => {
    try {
      const res = await getProjects();
      setProjects(res.projects);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load projects.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (ready) loadProjects();
  }, [ready, loadProjects]);

  // Keep cards for in-progress projects fresh.
  const anyActive = projects.some((p) => p.status === "queued" || p.status === "generating");
  useEffect(() => {
    if (!anyActive) return;
    const id = setInterval(loadProjects, 5000);
    return () => clearInterval(id);
  }, [anyActive, loadProjects]);

  const completed = projects.filter((p) => p.status === "completed");
  const totalSeconds = completed.reduce((sum, p) => sum + (p.video?.duration || 0), 0);

  return (
    <div className="space-y-8">
      <div className="glass-card rounded-3xl p-6 md:p-10 relative overflow-hidden">
        <div className="absolute -right-10 -bottom-10 h-64 w-64 bg-indigo-600/20 rounded-full blur-3xl pointer-events-none" />
        <div className="max-w-2xl relative">
          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight mb-3">
            Turn any topic into a <span className="gradient-text">narrated short video</span>
          </h1>
          <p className="text-slate-300 text-sm md:text-base leading-relaxed mb-6">
            StoryForge researches your topic, writes the script, generates an image for every scene, narrates it with a
            natural voice and renders a captioned MP4 — using free AI providers.
          </p>
          <button onClick={() => setIsModalOpen(true)} className="gradient-button px-6 py-3 rounded-2xl font-bold text-white shadow-xl">
            + New video
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Stat label="Projects" value={projects.length} />
        <Stat label="Videos rendered" value={completed.length} accent="text-emerald-400" />
        <Stat label="Minutes of video" value={(totalSeconds / 60).toFixed(1)} accent="text-indigo-400" />
        <Stat label="In progress" value={projects.filter((p) => p.status === "queued" || p.status === "generating").length} accent="text-amber-400" />
      </div>

      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-white">Your projects</h2>
        </div>

        {error && (
          <div className="mb-4 p-4 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center justify-between gap-4">
            <span>{error}</span>
            <button onClick={loadProjects} className="px-3 py-1.5 rounded-lg bg-slate-800 text-xs font-semibold text-slate-200 shrink-0">
              Retry
            </button>
          </div>
        )}

        {!ready || loading ? (
          <div className="text-center py-12 text-slate-400 text-sm animate-pulse">Loading projects…</div>
        ) : (
          <ProjectGrid projects={projects} onCreate={() => setIsModalOpen(true)} />
        )}
      </div>

      <CreateProjectModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
    </div>
  );
}

function Stat({ label, value, accent = "text-white" }: { label: string; value: React.ReactNode; accent?: string }) {
  return (
    <div className="glass-card rounded-2xl p-5 border border-slate-800">
      <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">{label}</span>
      <p className={`text-2xl font-extrabold mt-1 ${accent}`}>{value}</p>
    </div>
  );
}
