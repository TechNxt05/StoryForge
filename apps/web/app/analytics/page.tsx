"use client";

import React, { useEffect, useMemo, useState } from "react";
import { getProjects, ProjectSummary } from "../../lib/api";
import { useRequireAuth } from "../../lib/useRequireAuth";

function countBy(items: string[]): [string, number][] {
  const counts = new Map<string, number>();
  items.forEach((i) => counts.set(i, (counts.get(i) || 0) + 1));
  return [...counts.entries()].sort((a, b) => b[1] - a[1]);
}

export default function AnalyticsPage() {
  const ready = useRequireAuth();
  const [projects, setProjects] = useState<ProjectSummary[] | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!ready) return;
    getProjects()
      .then((res) => setProjects(res.projects))
      .catch((err) => setError(err.message));
  }, [ready]);

  const stats = useMemo(() => {
    const list = projects || [];
    const done = list.filter((p) => p.status === "completed" && p.video);
    const finished = list.filter((p) => p.status === "completed" || p.status === "failed");
    const seconds = done.reduce((s, p) => s + (p.video?.duration || 0), 0);
    return {
      total: list.length,
      completed: done.length,
      successRate: finished.length ? Math.round((100 * done.length) / finished.length) : null,
      minutes: seconds / 60,
      avgLength: done.length ? seconds / done.length : 0,
      packs: countBy(list.map((p) => p.content_pack_name)),
      formats: countBy(list.map((p) => p.aspect_ratio)),
      llm: countBy(done.map((p) => p.providers?.llm || "unknown")),
      images: countBy(done.flatMap((p) => p.providers?.images || [])),
      voice: countBy(done.flatMap((p) => p.providers?.voice || [])),
    };
  }, [projects]);

  return (
    <div className="space-y-6">
      <div className="pb-4 border-b border-slate-800">
        <h1 className="text-2xl font-extrabold text-white">Analytics</h1>
        <p className="text-xs text-slate-400 mt-1">Computed from your projects. Every provider used is free, so cost is $0.</p>
      </div>

      {error && <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">{error}</div>}

      {projects === null && !error ? (
        <div className="text-center py-12 text-slate-400 text-sm animate-pulse">Loading…</div>
      ) : (
        <>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <Card label="Projects" value={stats.total} />
            <Card label="Videos rendered" value={stats.completed} accent="text-emerald-400" />
            <Card label="Success rate" value={stats.successRate === null ? "—" : `${stats.successRate}%`} accent="text-indigo-400" />
            <Card label="Avg. video length" value={stats.avgLength ? `${Math.round(stats.avgLength)}s` : "—"} accent="text-purple-400" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Breakdown title="Styles" rows={stats.packs} />
            <Breakdown title="Formats" rows={stats.formats} />
            <Breakdown title="Script writer (LLM)" rows={stats.llm} />
            <Breakdown title="Image providers" rows={stats.images} />
            <Breakdown title="Voice providers" rows={stats.voice} />
            <div className="glass-card rounded-2xl p-5 border border-slate-800">
              <h3 className="font-bold text-sm text-slate-300 uppercase tracking-wider mb-2">Total video</h3>
              <p className="text-3xl font-extrabold text-white">{stats.minutes.toFixed(1)} min</p>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function Card({ label, value, accent = "text-white" }: { label: string; value: React.ReactNode; accent?: string }) {
  return (
    <div className="glass-card rounded-2xl p-5 border border-slate-800">
      <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">{label}</span>
      <p className={`text-2xl font-extrabold mt-1 ${accent}`}>{value}</p>
    </div>
  );
}

function Breakdown({ title, rows }: { title: string; rows: [string, number][] }) {
  const max = Math.max(1, ...rows.map(([, n]) => n));
  return (
    <div className="glass-card rounded-2xl p-5 border border-slate-800">
      <h3 className="font-bold text-sm text-slate-300 uppercase tracking-wider mb-3">{title}</h3>
      {rows.length === 0 ? (
        <p className="text-xs text-slate-500">No data yet.</p>
      ) : (
        <ul className="space-y-2.5">
          {rows.map(([name, n]) => (
            <li key={name}>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-slate-200 capitalize">{name}</span>
                <span className="text-slate-400 tabular-nums">{n}</span>
              </div>
              <div className="h-1.5 rounded-full bg-slate-800 overflow-hidden">
                <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${(100 * n) / max}%` }} />
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
