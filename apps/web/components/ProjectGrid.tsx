"use client";

import React from "react";
import Link from "next/link";

interface Project {
  id: string;
  title: string;
  topic: string;
  content_pack_name: string;
  aspect_ratio?: string;
  status: string;
  created_at: string;
}

interface ProjectGridProps {
  projects: Project[];
}

export default function ProjectGrid({ projects }: ProjectGridProps) {
  if (projects.length === 0) {
    return (
      <div className="glass-card rounded-2xl p-12 text-center border border-slate-800">
        <div className="h-12 w-12 rounded-2xl bg-indigo-500/20 text-indigo-400 mx-auto flex items-center justify-center font-bold text-xl mb-4">
          🎬
        </div>
        <h3 className="text-lg font-bold text-slate-200">No Story Projects Yet</h3>
        <p className="text-sm text-slate-400 max-w-sm mx-auto mt-1">
          Click &quot;New Story Project&quot; above to initialize your autonomous multi-agent video pipeline.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {projects.map((project) => (
        <div key={project.id} className="glass-card rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="px-2.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-[11px] font-semibold uppercase tracking-wider">
                {project.content_pack_name || "general"}
              </span>
              <span className="text-[11px] font-medium text-slate-400">
                {project.aspect_ratio || "9:16"}
              </span>
            </div>

            <h3 className="font-bold text-lg text-white mb-1 line-clamp-1">{project.title}</h3>
            <p className="text-slate-400 text-xs line-clamp-2 mb-4">{project.topic}</p>
          </div>

          <div className="pt-4 border-t border-slate-800/60 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className={`h-2 w-2 rounded-full ${project.status === 'completed' ? 'bg-emerald-400' : 'bg-amber-400 animate-pulse'}`}></span>
              <span className={`text-xs font-semibold capitalize ${project.status === 'completed' ? 'text-emerald-400' : 'text-amber-400'}`}>{project.status}</span>
            </div>

            <Link
              href={`/studio/${project.id}`}
              className="px-3 py-1.5 rounded-lg bg-indigo-600/30 hover:bg-indigo-600/50 border border-indigo-500/40 text-indigo-300 text-xs font-semibold transition flex items-center space-x-1"
            >
              <span>Open Studio</span>
              <span>&rarr;</span>
            </Link>
          </div>
        </div>
      ))}
    </div>
  );
}
