"use client";

import React, { useState } from "react";

export default function AssetsPage() {
  const [filter, setFilter] = useState("all");

  const assets = [
    { id: "ast-1", name: "gutenberg_press_render.png", type: "image", provider: "FLUX.1", url: "https://cdn.storyforge.ai/images/flux-1.png", size: "2.4 MB" },
    { id: "ast-2", name: "movable_type_printing.mp4", type: "video", provider: "Google Veo", url: "https://cdn.storyforge.ai/videos/veo-1.mp4", size: "14.8 MB" },
    { id: "ast-3", name: "history_narration_voice.mp3", type: "audio", provider: "Kokoro TTS", url: "https://cdn.storyforge.ai/audio/kokoro-1.mp3", size: "1.1 MB" },
  ];

  const filteredAssets = filter === "all" ? assets : assets.filter((a) => a.type === filter);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div>
          <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">Media Storage</span>
          <h1 className="text-2xl font-extrabold text-white mt-0.5">Cloudinary Asset Library</h1>
        </div>

        <div className="flex space-x-2 bg-slate-900 border border-slate-800 rounded-xl p-1">
          {["all", "image", "video", "audio"].map((t) => (
            <button
              key={t}
              onClick={() => setFilter(t)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold capitalize transition ${
                filter === t ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {filteredAssets.map((asset) => (
          <div key={asset.id} className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 text-[10px] font-bold uppercase">
                  {asset.type}
                </span>
                <span className="text-[11px] font-medium text-slate-400">{asset.size}</span>
              </div>
              <h3 className="font-bold text-sm text-white line-clamp-1 mb-1">{asset.name}</h3>
              <p className="text-[11px] text-slate-400 font-mono">Provider: {asset.provider}</p>
            </div>

            <div className="pt-4 mt-4 border-t border-slate-800 flex justify-end">
              <a
                href={asset.url}
                target="_blank"
                rel="noreferrer"
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition"
              >
                View Asset &rarr;
              </a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
