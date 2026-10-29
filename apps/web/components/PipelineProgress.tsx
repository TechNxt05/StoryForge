"use client";

import React, { useEffect, useState } from "react";
import { Job, JobStep } from "../lib/api";

const STEP_ORDER = ["research", "script", "images", "voice", "render", "publish"];

function elapsed(step: JobStep, now: number): string {
  if (!step.started_at) return "";
  const start = Date.parse(step.started_at);
  const end = step.finished_at ? Date.parse(step.finished_at) : now;
  const secs = Math.max(0, Math.round((end - start) / 1000));
  return secs >= 60 ? `${Math.floor(secs / 60)}m ${secs % 60}s` : `${secs}s`;
}

const STATUS: Record<string, { badge: string; icon: string }> = {
  completed: { badge: "bg-emerald-500/10 text-emerald-300 border-emerald-500/30", icon: "✓" },
  skipped: { badge: "bg-slate-700/30 text-slate-400 border-slate-600", icon: "↷" },
  running: { badge: "bg-indigo-500/10 text-indigo-300 border-indigo-500/30 animate-pulse", icon: "●" },
  failed: { badge: "bg-rose-500/10 text-rose-300 border-rose-500/30", icon: "✕" },
  pending: { badge: "bg-slate-800 text-slate-500 border-slate-700", icon: "○" },
};

/** Live view of the generation pipeline (research → script → images → voice → render → publish). */
export default function PipelineProgress({ job }: { job: Job }) {
  const [now, setNow] = useState(Date.now());
  const active = job.status === "queued" || job.status === "running";

  useEffect(() => {
    if (!active) return;
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, [active]);

  const steps = STEP_ORDER.filter((k) => job.steps[k]).map((k) => [k, job.steps[k]] as const);
  const done = steps.filter(([, s]) => s.status === "completed" || s.status === "skipped").length;
  const percent = steps.length ? Math.round((done / steps.length) * 100) : 0;

  const headline =
    job.status === "queued"
      ? "Waiting in queue — another video is rendering on this server"
      : job.status === "running"
        ? "Generating your video…"
        : job.status === "completed"
          ? "Last run completed"
          : "Last run failed";

  return (
    <div className="glass-card rounded-2xl p-5 md:p-6 border border-slate-800 space-y-4">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div>
          <h3 className="font-bold text-sm text-slate-200 uppercase tracking-wider">Pipeline</h3>
          <p className="text-xs text-slate-400 mt-1">{headline}</p>
        </div>
        <div className="w-full md:w-64 space-y-1.5">
          <div className="flex justify-between text-xs font-semibold">
            <span className="text-slate-300">{done} of {steps.length} steps</span>
            <span className="text-indigo-300">{percent}%</span>
          </div>
          <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
            <div className="h-full gradient-button transition-all duration-500 rounded-full" style={{ width: `${percent}%` }} />
          </div>
        </div>
      </div>

      {job.status === "failed" && job.error && (
        <div role="alert" className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
          {job.error}
        </div>
      )}

      <ol className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {steps.map(([key, step], idx) => {
          const style = STATUS[step.status] || STATUS.pending;
          return (
            <li key={key} className="rounded-xl p-3 bg-slate-950/50 border border-slate-800 min-w-0">
              <div className="flex items-center justify-between mb-1.5 gap-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Step {idx + 1}</span>
                <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold border ${style.badge}`}>
                  {style.icon} {step.status}
                </span>
              </div>
              <div className="font-bold text-xs text-white">{step.label}</div>
              {step.detail && <div className="text-[11px] text-slate-400 mt-1 line-clamp-2">{step.detail}</div>}
              <div className="mt-2 pt-2 border-t border-slate-800/80 flex items-center justify-between gap-2 text-[10px]">
                <span className="text-indigo-300 font-mono truncate" title={step.model || step.provider}>
                  {step.provider || "—"}
                </span>
                <span className="text-slate-500 font-mono shrink-0">{elapsed(step, now)}</span>
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
