"use client";

import React from "react";
import Link from "next/link";
import { mediaUrl, ProjectSummary } from "../lib/api";

const STATUS_STYLES: Record<ProjectSummary["status"], { dot: string; text: string; label: string }> = {
  draft: { dot: "bg-slate-400", text: "text-slate-300", label: "Draft" },
  queued: { dot: "bg-amber-400 animate-pulse", text: "text-amber-300", label: "Queued" },
  generating: { dot: "bg-indigo-400 animate-pulse", text: "text-indigo-300", label: "Generating" },
  completed: { dot: "bg-emerald-400", text: "text-emerald-300", label: "Ready" },
  failed: { dot: "bg-rose-400", text: "text-rose-300", label: "Failed" },
};

export default function ProjectGrid({ projects, onCreate }: { projects: ProjectSummary[]; onCreate: () => void }) {
  if (projects.length === 0) {
    return (
      <div className="glass-card rounded-2xl p-12 text-center border border-slate-800">
        <h3 className="text-lg font-bold text-slate-200">No projects yet</h3>
        <p className="text-sm text-slate-400 max-w-sm mx-auto mt-1 mb-5">
          Create your first video — pick a topic and StoryForge does the rest in a few minutes.
        </p>
        <button onClick={onCreate} className="gradient-button px-5 py-2.5 rounded-xl text-sm font-bold text-white">
          + New video
        </button>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
      {projects.map((project) => {
        const status = STATUS_STYLES[project.status] || STATUS_STYLES.draft;
        const active = project.status === "queued" || project.status === "generating";
        return (
          <Link
            key={project.id}
            href={`/studio/${project.id}`}
            className="glass-card rounded-2xl overflow-hidden flex flex-col border border-slate-800 hover:border-indigo-500/50 transition group"
          >
            <div className="relative aspect-video bg-slate-950 overflow-hidden">
              {project.thumbnail_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={mediaUrl(project.thumbnail_url)}
                  alt=""
                  loading="lazy"
                  className="w-full h-full object-cover opacity-80 group-hover:opacity-100 group-hover:scale-105 transition duration-500"
                />
              ) : (
                <div className="w-full h-full bg-gradient-to-br from-indigo-900/40 via-slate-900 to-purple-900/30" />
              )}
              <span className="absolute top-3 left-3 px-2 py-0.5 rounded-full bg-black/60 text-indigo-200 text-[10px] font-semibold uppercase tracking-wider">
                {project.content_pack_name}
              </span>
              <span className="absolute top-3 right-3 px-2 py-0.5 rounded-full bg-black/60 text-slate-200 text-[10px] font-semibold">
                {project.aspect_ratio}
                {project.video ? ` · ${Math.round(project.video.duration)}s` : ""}
              </span>
              {active && (
                <div className="absolute bottom-0 inset-x-0 h-1 bg-slate-900">
                  <div className="h-full gradient-button transition-all duration-700" style={{ width: `${Math.max(5, project.progress)}%` }} />
                </div>
              )}
            </div>

            <div className="p-5 flex-1 flex flex-col">
              <h3 className="font-bold text-base text-white mb-1 line-clamp-1">{project.title}</h3>
              <p className="text-slate-400 text-xs line-clamp-2 mb-4 flex-1">{project.topic}</p>
              <div className="flex items-center justify-between text-xs">
                <span className={`flex items-center gap-2 font-semibold ${status.text}`}>
                  <span className={`h-2 w-2 rounded-full ${status.dot}`} />
                  {status.label}
                  {active && ` · ${project.progress}%`}
                </span>
                <span className="text-indigo-300 font-semibold">Open →</span>
              </div>
            </div>
          </Link>
        );
      })}
    </div>
  );
}
