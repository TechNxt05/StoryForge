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
  const [activeTab, setActiveTab] = useState<"slides" | "tracks">("slides");
  const [editingText, setEditingText] = useState<string>("");

  const selectedClip = clips.find((c) => c.id === selectedClipId);

  const handleSelectClip = (clip: TimelineClip) => {
    setSelectedClipId(clip.id);
    setEditingText(clip.name);
  };

  const handleTextChange = (newText: string) => {
    setEditingText(newText);
    if (selectedClip) {
      onClipUpdate({
        ...selectedClip,
        name: newText,
      });
    }
  };

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
      {/* Header & Controls */}
      <div className="flex justify-between items-center p-4 bg-slate-900 rounded-xl border border-slate-800">
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setActiveTab("slides")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
              activeTab === "slides"
                ? "bg-indigo-600 text-white"
                : "bg-slate-800 text-slate-400 hover:text-white"
            }`}
          >
            🎨 Canva Slide Deck
          </button>
          <button
            onClick={() => setActiveTab("tracks")}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
              activeTab === "tracks"
                ? "bg-indigo-600 text-white"
                : "bg-slate-800 text-slate-400 hover:text-white"
            }`}
          >
            🎚️ Multi-Track Editor
          </button>
        </div>

        <label className="cursor-pointer bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition">
          {isUploading ? "Uploading..." : "+ Upload Media"}
          <input type="file" className="hidden" accept="video/*,image/*" onChange={handleFileChange} disabled={isUploading} />
        </label>
      </div>

      {/* Tab 1: Canva-Style Slide Deck & Frame Distribution */}
      {activeTab === "slides" ? (
        <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-800 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Frame Distribution & Scene Deck ({clips.length} Frames)
            </h4>
            <span className="text-[11px] text-indigo-400">Click a slide to edit text & properties</span>
          </div>

          <div className="flex space-x-4 overflow-x-auto pb-4 pt-2">
            {clips.map((clip, idx) => (
              <div
                key={clip.id}
                onClick={() => handleSelectClip(clip)}
                className={`flex-none w-48 h-32 rounded-xl border-2 p-3 cursor-pointer transition flex flex-col justify-between relative overflow-hidden bg-slate-950 ${
                  selectedClipId === clip.id ? "border-indigo-500 ring-2 ring-indigo-500/30" : "border-slate-800 hover:border-slate-700"
                }`}
              >
                {/* Slide Number Badge */}
                <div className="flex justify-between items-center z-10">
                  <span className="px-2 py-0.5 rounded bg-indigo-500/20 border border-indigo-500/30 text-[10px] font-bold text-indigo-300">
                    Frame {idx + 1}
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">{clip.duration}s</span>
                </div>

                {/* Text Content / Title */}
                <p className="text-xs font-semibold text-slate-200 line-clamp-2 z-10 my-auto">
                  {clip.name}
                </p>

                {/* Type Badge */}
                <div className="z-10 flex justify-between items-center text-[10px] text-slate-400">
                  <span className="capitalize">{clip.type}</span>
                  <span>{clip.filters.brightness !== 0 ? "✨ Filtered" : ""}</span>
                </div>

                {/* Background Ambient Card Glow */}
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/20 via-transparent to-black pointer-events-none"></div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        /* Tab 2: Multi-Track Timeline */
        <div className="bg-slate-900/50 rounded-xl border border-slate-800 p-4 space-y-2 overflow-x-auto">
          <div className="flex items-center space-x-2">
            <div className="w-20 text-xs font-semibold text-slate-400">Video</div>
            <div className="flex-1 h-16 bg-slate-800 rounded-lg relative flex items-center p-1 space-x-1">
              {clips.filter((c) => c.type === "video" || c.type === "image").map((clip) => (
                <div
                  key={clip.id}
                  onClick={() => handleSelectClip(clip)}
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

          <div className="flex items-center space-x-2">
            <div className="w-20 text-xs font-semibold text-slate-400">Audio</div>
            <div className="flex-1 h-12 bg-slate-800 rounded-lg relative flex items-center p-1 space-x-1">
              {clips.filter((c) => c.type === "audio").map((clip) => (
                <div
                  key={clip.id}
                  onClick={() => handleSelectClip(clip)}
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
      )}

      {/* Slide & Clip Inspector */}
      {selectedClip ? (
        <div className="p-4 bg-slate-900 rounded-xl border border-slate-800 space-y-4">
          <div className="pb-2 border-b border-slate-800 flex justify-between items-center">
            <h4 className="text-sm font-bold text-slate-200">
              Inspector: <span className="text-indigo-400">{selectedClip.name}</span>
            </h4>
            <span className="text-xs text-slate-500 uppercase">{selectedClip.type} frame</span>
          </div>

          {/* Edit Slide Text / Title */}
          <div className="space-y-1">
            <label className="text-xs text-slate-400 font-semibold">Frame Text / Title</label>
            <input
              type="text"
              value={editingText}
              onChange={(e) => handleTextChange(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
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
        </div>
      ) : (
        <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-800 text-center text-sm text-slate-500">
          Select a frame card above to edit text, brightness, contrast, or volume.
        </div>
      )}
    </div>
  );
}
