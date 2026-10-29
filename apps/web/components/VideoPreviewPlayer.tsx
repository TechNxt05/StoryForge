"use client";

import React from "react";
import { mediaUrl, VideoInfo } from "../lib/api";

interface VideoPreviewPlayerProps {
  video: VideoInfo | null;
  poster?: string | null;
  aspectRatio: string;
  title: string;
  busy: boolean;
  stale: boolean;
}

function formatBytes(bytes: number): string {
  return bytes > 1e6 ? `${(bytes / 1e6).toFixed(1)} MB` : `${Math.round(bytes / 1e3)} KB`;
}

export default function VideoPreviewPlayer({ video, poster, aspectRatio, title, busy, stale }: VideoPreviewPlayerProps) {
  const frame = aspectRatio === "9:16" ? "aspect-[9/16] max-w-[320px]" : aspectRatio === "1:1" ? "aspect-square max-w-[420px]" : "aspect-video";
  const src = mediaUrl(video?.url);

  return (
    <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col items-center">
      <div className="w-full flex items-center justify-between mb-4 gap-2">
        <h3 className="font-bold text-sm text-slate-300 uppercase tracking-wider">Preview</h3>
        {video && (
          <span className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 text-[11px] font-semibold">
            {video.width}×{video.height} · {Math.round(video.duration)}s
          </span>
        )}
      </div>

      <div className={`relative w-full mx-auto rounded-xl overflow-hidden bg-slate-950 border border-slate-800 ${frame}`}>
        {src ? (
          <video key={src} src={src} poster={mediaUrl(poster) || undefined} controls playsInline preload="metadata" className="absolute inset-0 w-full h-full object-contain bg-black" />
        ) : (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 text-xs text-slate-500 p-6 text-center">
            {busy ? (
              <>
                <div className="h-8 w-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
                <span>Your video is being generated…</span>
              </>
            ) : (
              <span>No video yet. Click “Generate video”.</span>
            )}
          </div>
        )}
      </div>

      {stale && video && !busy && (
        <p className="mt-3 text-[11px] text-amber-300 text-center">The script changed since this render. Re-render to update the video.</p>
      )}

      {src && (
        <div className="w-full flex items-center justify-between mt-4 gap-3 text-xs">
          <span className="text-slate-500">
            {formatBytes(video!.bytes)} · {video!.storage === "local" ? "server storage" : video!.storage}
          </span>
          <a
            href={src}
            download={`${title.replace(/[^\w-]+/g, "_").slice(0, 60) || "storyforge"}.mp4`}
            target="_blank"
            rel="noreferrer"
            className="px-3 py-1.5 rounded-lg bg-emerald-600/20 border border-emerald-500/40 text-emerald-300 font-semibold hover:bg-emerald-600/30 transition"
          >
            Download MP4
          </a>
        </div>
      )}
    </div>
  );
}
