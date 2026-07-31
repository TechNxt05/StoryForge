"use client";

import React, { useState } from "react";

export interface TimelineClip {
  id: string;
  type: "video" | "audio" | "image";
  url: string;
  startOffset: number;
  duration: number;
  filters: {
    brightness: number;
    contrast: number;
    volume?: number;
  };
  name: string;
}

interface TimelineEditorProps {
  clips: TimelineClip[];
  onClipUpdate: (updatedClip: TimelineClip) => void;
  onUpload: (file: File) => Promise<void>;
  isUploading: boolean;
}

export default function TimelineEditor({ clips, onClipUpdate, onUpload, isUploading }: TimelineEditorProps) {
  const [selectedClipId, setSelectedClipId] = useState<string | null>(null);

  const selectedClip = clips.find((c) => c.id === selectedClipId);

  const handleFilterChange = (key: keyof TimelineClip["filters"], value: number) => {
    if (selectedClip) {
      onClipUpdate({
        ...selectedClip,
        filters: {
          ...selectedClip.filters,
          [key]: value,
        },
      });
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await onUpload(e.target.files[0]);
    }
  };

  return (
    <div className="flex flex-col space-y-4">
      {/* Upload & Controls */}
      <div className="flex justify-between items-center p-4 bg-slate-900 rounded-xl border border-slate-800">
        <h3 className="font-bold text-slate-200">Media Bin & Timeline</h3>
        <label className="cursor-pointer bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition">
          {isUploading ? "Uploading..." : "+ Upload Media"}
          <input type="file" className="hidden" accept="video/*,image/*" onChange={handleFileChange} disabled={isUploading} />
        </label>
      </div>

      {/* Timeline Tracks */}
      <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4 space-y-2 overflow-x-auto">
        {/* Video Track */}
        <div className="flex items-center space-x-2">
          <div className="w-20 text-xs font-semibold text-slate-400">Video</div>
          <div className="flex-1 h-16 bg-slate-800 rounded-lg relative flex items-center p-1 space-x-1">
            {clips.filter((c) => c.type === "video" || c.type === "image").map((clip) => (
              <div
                key={clip.id}
                onClick={() => setSelectedClipId(clip.id)}
                className={`h-full bg-indigo-500/20 border-2 rounded-md flex items-center px-2 cursor-pointer transition ${
                  selectedClipId === clip.id ? "border-indigo-400" : "border-indigo-500/30"
                }`}
                style={{ width: `${Math.max(clip.duration * 10, 40)}px` }}
              >
                <span className="text-[10px] text-indigo-200 truncate">{clip.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Audio Track */}
        <div className="flex items-center space-x-2">
          <div className="w-20 text-xs font-semibold text-slate-400">Audio</div>
          <div className="flex-1 h-12 bg-slate-800 rounded-lg relative flex items-center p-1 space-x-1">
            {clips.filter((c) => c.type === "audio").map((clip) => (
              <div
                key={clip.id}
                onClick={() => setSelectedClipId(clip.id)}
                className={`h-full bg-emerald-500/20 border-2 rounded-md flex items-center px-2 cursor-pointer transition ${
                  selectedClipId === clip.id ? "border-emerald-400" : "border-emerald-500/30"
                }`}
                style={{ width: `${Math.max(clip.duration * 10, 40)}px` }}
              >
                <span className="text-[10px] text-emerald-200 truncate">{clip.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Properties Inspector */}
      {selectedClip ? (
        <div className="p-4 bg-slate-900 rounded-xl border border-slate-800 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="col-span-1 md:col-span-3 pb-2 border-b border-slate-800">
            <h4 className="text-sm font-bold text-slate-200">
              Inspector: <span className="text-indigo-400">{selectedClip.name}</span>
            </h4>
          </div>

          <div className="space-y-2">
            <label className="text-xs text-slate-400 font-semibold flex justify-between">
              <span>Brightness</span>
              <span>{selectedClip.filters.brightness.toFixed(1)}</span>
            </label>
            <input
              type="range"
              min="-1"
              max="1"
              step="0.1"
              value={selectedClip.filters.brightness}
              onChange={(e) => handleFilterChange("brightness", parseFloat(e.target.value))}
              className="w-full accent-indigo-500"
            />
          </div>

          <div className="space-y-2">
            <label className="text-xs text-slate-400 font-semibold flex justify-between">
              <span>Contrast</span>
              <span>{selectedClip.filters.contrast.toFixed(1)}</span>
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={selectedClip.filters.contrast}
              onChange={(e) => handleFilterChange("contrast", parseFloat(e.target.value))}
              className="w-full accent-indigo-500"
            />
          </div>

          {(selectedClip.type === "video" || selectedClip.type === "audio") && (
            <div className="space-y-2">
              <label className="text-xs text-slate-400 font-semibold flex justify-between">
                <span>Volume</span>
                <span>{selectedClip.filters.volume?.toFixed(1) || 1.0}</span>
              </label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={selectedClip.filters.volume || 1.0}
                onChange={(e) => handleFilterChange("volume", parseFloat(e.target.value))}
                className="w-full accent-indigo-500"
              />
            </div>
          )}
        </div>
      ) : (
        <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-800 text-center text-sm text-slate-500">
          Select a clip in the timeline to adjust properties (Brightness, Contrast, Volume).
        </div>
      )}
    </div>
  );
}
