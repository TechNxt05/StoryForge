"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { Asset, getAssets, mediaUrl } from "../../lib/api";
import { useRequireAuth } from "../../lib/useRequireAuth";

const FILTERS = ["all", "video", "image"] as const;

export default function AssetsPage() {
  const ready = useRequireAuth();
  const [filter, setFilter] = useState<(typeof FILTERS)[number]>("all");
  const [assets, setAssets] = useState<Asset[] | null>(null);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<Asset | null>(null);

  useEffect(() => {
    if (!ready) return;
    setAssets(null);
    getAssets(filter === "all" ? undefined : filter)
      .then((res) => setAssets(res.assets))
      .catch((err) => setError(err.message));
  }, [ready, filter]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-white">Asset library</h1>
          <p className="text-xs text-slate-400 mt-1">Every video and scene image generated for your projects.</p>
        </div>
        <div className="flex gap-1 bg-slate-900 border border-slate-800 rounded-xl p-1 self-start">
          {FILTERS.map((t) => (
            <button
              key={t}
              onClick={() => setFilter(t)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold capitalize transition ${filter === t ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-slate-200"}`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">{error}</div>}

      {assets === null && !error ? (
        <div className="text-center py-12 text-slate-400 text-sm animate-pulse">Loading assets…</div>
      ) : assets && assets.length === 0 ? (
        <div className="glass-card rounded-2xl p-12 text-center border border-slate-800 text-sm text-slate-400">
          Nothing here yet. Assets appear after a video finishes generating.
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {assets?.map((asset) => (
            <button
              key={asset.id}
              onClick={() => setSelected(asset)}
              className="glass-card rounded-2xl overflow-hidden border border-slate-800 text-left hover:border-indigo-500/50 transition"
            >
              <div className="aspect-video bg-slate-950 relative">
                {asset.asset_type === "image" ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={mediaUrl(asset.storage_url)} alt="" loading="lazy" className="w-full h-full object-cover" />
                ) : (
                  <video src={mediaUrl(asset.storage_url)} preload="metadata" muted className="w-full h-full object-cover" />
                )}
                <span className="absolute top-2 left-2 px-1.5 py-0.5 rounded bg-black/70 text-[10px] font-bold uppercase text-indigo-200">{asset.asset_type}</span>
              </div>
              <div className="p-3">
                <p className="text-xs font-semibold text-white line-clamp-1">{asset.project_title}</p>
                <p className="text-[11px] text-slate-500 font-mono mt-0.5">
                  {asset.provider_name}
                  {asset.file_size_bytes ? ` · ${(asset.file_size_bytes / 1e6).toFixed(1)} MB` : ""}
                </p>
              </div>
            </button>
          ))}
        </div>
      )}

      {selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-4" onClick={() => setSelected(null)}>
          <div className="glass-card max-w-3xl w-full rounded-2xl p-5 border border-slate-700 shadow-2xl" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4 gap-4">
              <h3 className="font-bold text-sm text-white truncate">{selected.project_title}</h3>
              <button onClick={() => setSelected(null)} aria-label="Close" className="text-slate-400 hover:text-white text-lg">✕</button>
            </div>
            <div className="rounded-xl overflow-hidden bg-black flex items-center justify-center max-h-[70vh]">
              {selected.asset_type === "image" ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={mediaUrl(selected.storage_url)} alt="" className="max-h-[70vh] object-contain" />
              ) : (
                <video src={mediaUrl(selected.storage_url)} controls autoPlay className="max-h-[70vh] w-full" />
              )}
            </div>
            {typeof selected.metadata_json.prompt === "string" && (
              <p className="text-xs text-slate-400 mt-3 line-clamp-3">{selected.metadata_json.prompt}</p>
            )}
            <div className="flex justify-between items-center text-xs mt-4">
              <Link href={`/studio/${selected.project_id}`} className="text-indigo-300 hover:underline font-semibold">Open project →</Link>
              <a href={mediaUrl(selected.storage_url)} target="_blank" rel="noreferrer" className="text-indigo-300 hover:underline font-semibold">Open file ↗</a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
