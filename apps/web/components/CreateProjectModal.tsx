"use client";

import React, { useState } from "react";

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onProjectCreated: (project: any) => void;
}

export default function CreateProjectModal({ isOpen, onClose, onProjectCreated }: CreateProjectModalProps) {
  const [title, setTitle] = useState("");
  const [topic, setTopic] = useState("");
  const [contentPack, setContentPack] = useState("history");
  const [aspectRatio, setAspectRatio] = useState("9:16");
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title || !topic) return;

    setLoading(true);

    try {
      // Connect to API Gateway
      const res = await fetch("http://localhost:8000/api/v1/projects", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          topic,
          content_pack_name: contentPack,
          aspect_ratio: aspectRatio,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        onProjectCreated(data);
      } else {
        // Fallback local creation if gateway offline
        const fallbackProject = {
          id: `proj-${Math.random().toString(36).substring(2, 9)}`,
          title,
          topic,
          content_pack_name: contentPack,
          aspect_ratio: aspectRatio,
          status: "draft",
          created_at: new Date().toISOString(),
        };
        onProjectCreated(fallbackProject);
      }
    } catch (err) {
      // Local fallback creation
      const fallbackProject = {
        id: `proj-${Math.random().toString(36).substring(2, 9)}`,
        title,
        topic,
        content_pack_name: contentPack,
        aspect_ratio: aspectRatio,
        status: "draft",
        created_at: new Date().toISOString(),
      };
      onProjectCreated(fallbackProject);
    } finally {
      setLoading(false);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="glass-card max-w-lg w-full rounded-2xl p-6 relative border border-slate-700/80 shadow-2xl">
        <h2 className="text-xl font-bold mb-4 text-white">Create New Story Project</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
              Project Title
            </label>
            <input
              type="text"
              required
              placeholder="e.g. The Invention of Printing Press"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full bg-slate-900/90 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
              Topic & Prompt Details
            </label>
            <textarea
              required
              rows={3}
              placeholder="e.g. How Johannes Gutenberg created movable type printing and changed humanity..."
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              className="w-full bg-slate-900/90 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                Content Pack
              </label>
              <select
                value={contentPack}
                onChange={(e) => setContentPack(e.target.value)}
                className="w-full bg-slate-900/90 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none"
              >
                <option value="history">History & Culture</option>
                <option value="technology">Technology & AI</option>
                <option value="science">Science & Space</option>
                <option value="documentary">Dark Documentary</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                Aspect Ratio
              </label>
              <select
                value={aspectRatio}
                onChange={(e) => setAspectRatio(e.target.value)}
                className="w-full bg-slate-900/90 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none"
              >
                <option value="9:16">9:16 (Reels/Shorts)</option>
                <option value="16:9">16:9 (Landscape Doc)</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-sm font-medium text-slate-400 hover:text-slate-200 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="gradient-button px-5 py-2 rounded-xl text-sm font-bold text-white shadow-lg"
            >
              {loading ? "Initializing..." : "Create Project"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
