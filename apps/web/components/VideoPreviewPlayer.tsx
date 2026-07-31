"use client";

import React, { useState } from "react";

interface VideoPreviewPlayerProps {
  videoUrl?: string;
  aspectRatio: string;
  title: string;
}

export default function VideoPreviewPlayer({
  videoUrl = "https://res.cloudinary.com/demo/video/upload/v1689255627/dog.mp4",
  aspectRatio = "9:16",
  title,
}: VideoPreviewPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [showSubtitles, setShowSubtitles] = useState(true);

  const isVertical = aspectRatio === "9:16";

  return (
    <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col items-center">
      <div className="w-full flex items-center justify-between mb-4">
        <h3 className="font-bold text-sm text-slate-300 uppercase tracking-wider">Live Video Render Preview</h3>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowSubtitles(!showSubtitles)}
            className={`px-2.5 py-1 rounded-lg text-xs font-semibold border transition ${
              showSubtitles
                ? "bg-indigo-500/20 border-indigo-500/40 text-indigo-300"
                : "bg-slate-800 border-slate-700 text-slate-400"
            }`}
          >
            Subtitles: {showSubtitles ? "ON" : "OFF"}
          </button>
          <span className="px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 text-xs font-semibold">
            {aspectRatio}
          </span>
        </div>
      </div>

      {/* Video Viewport */}
      <div
        className={`relative rounded-xl overflow-hidden bg-slate-950 border border-slate-800 flex flex-col justify-between p-4 shadow-2xl transition-all ${
          isVertical ? "w-64 h-[440px]" : "w-full max-w-xl h-[320px]"
        }`}
      >
        {/* Real HTML5 Video Stream */}
        {videoUrl ? (
          <video
            src={videoUrl}
            controls
            autoPlay={isPlaying}
            loop
            className="absolute inset-0 w-full h-full object-cover z-0"
          />
        ) : (
          <div className="absolute inset-0 bg-slate-900 flex items-center justify-center text-xs text-slate-500">
            Rendering video stream...
          </div>
        )}

        {/* Top Overlay Badge */}
        <div className="flex items-center justify-between z-10 pointer-events-none">
          <span className="px-2 py-0.5 rounded bg-black/60 backdrop-blur-md text-[10px] font-bold text-emerald-400 uppercase tracking-widest border border-emerald-500/30">
            1080p H.264
          </span>
          <span className="text-[10px] font-mono text-slate-400">60 FPS</span>
        </div>

        {/* Subtitle Highlight Overlay Mock */}
        {showSubtitles && (
          <div className="z-10 text-center mb-2 pointer-events-none">
            <span className="px-3 py-1 rounded-lg bg-black/80 backdrop-blur-md border border-yellow-500/40 text-xs font-bold text-yellow-300 shadow-lg inline-block">
              {title}
            </span>
          </div>
        )}

        {/* Background Ambient Gradient */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-black/40 pointer-events-none z-5"></div>
      </div>
    </div>
  );
}
