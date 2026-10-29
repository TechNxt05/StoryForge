"use client";

import React from "react";
import { mediaUrl, Scene } from "../lib/api";

export interface EditableScene extends Scene {
  regenerateImage?: boolean;
}

interface SceneEditorProps {
  scenes: EditableScene[];
  onChange: (scenes: EditableScene[]) => void;
  disabled: boolean;
}

const fieldClass =
  "w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 disabled:opacity-60";

/** Edit narration, visuals and captions for each scene. Changes are saved by the parent. */
export default function SceneEditor({ scenes, onChange, disabled }: SceneEditorProps) {
  const update = (index: number, patch: Partial<EditableScene>) =>
    onChange(scenes.map((s, i) => (i === index ? { ...s, ...patch } : s)));

  const move = (index: number, delta: number) => {
    const target = index + delta;
    if (target < 0 || target >= scenes.length) return;
    const next = [...scenes];
    [next[index], next[target]] = [next[target], next[index]];
    onChange(next);
  };

  const remove = (index: number) => onChange(scenes.filter((_, i) => i !== index));

  const add = () =>
    onChange([
      ...scenes,
      { heading: `Scene ${scenes.length + 1}`, narration: "", visual_prompt: "", on_screen_text: "" },
    ]);

  return (
    <div className="space-y-4">
      {scenes.map((scene, i) => {
        const words = scene.narration.trim() ? scene.narration.trim().split(/\s+/).length : 0;
        return (
          <div key={i} className="glass-card rounded-2xl border border-slate-800 p-4 flex flex-col sm:flex-row gap-4">
            <div className="sm:w-36 shrink-0">
              <div className="relative aspect-[9/16] sm:aspect-[3/4] max-h-56 rounded-xl overflow-hidden bg-slate-950 border border-slate-800">
                {scene.image_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={mediaUrl(scene.image_url)} alt={`Scene ${i + 1}`} loading="lazy" className="w-full h-full object-cover" />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-[11px] text-slate-500 p-3 text-center">
                    Image generated on next render
                  </div>
                )}
                <span className="absolute top-2 left-2 px-1.5 py-0.5 rounded bg-black/70 text-[10px] font-bold text-white">{i + 1}</span>
              </div>
              {scene.image_url && (
                <label className="mt-2 flex items-center gap-1.5 text-[11px] text-slate-400 cursor-pointer">
                  <input
                    type="checkbox"
                    disabled={disabled}
                    checked={!!scene.regenerateImage}
                    onChange={(e) => update(i, { regenerateImage: e.target.checked })}
                    className="accent-indigo-500"
                  />
                  New image on render
                </label>
              )}
              {scene.image_provider && <p className="text-[10px] text-slate-500 mt-1 font-mono">{scene.image_provider}</p>}
            </div>

            <div className="flex-1 space-y-3 min-w-0">
              <div className="flex items-center gap-2">
                <input
                  aria-label={`Scene ${i + 1} heading`}
                  value={scene.heading}
                  disabled={disabled}
                  maxLength={200}
                  onChange={(e) => update(i, { heading: e.target.value })}
                  className="flex-1 min-w-0 bg-transparent text-sm font-bold text-white focus:outline-none border-b border-transparent focus:border-indigo-500"
                />
                <div className="flex items-center gap-1 shrink-0">
                  <IconButton label="Move up" onClick={() => move(i, -1)} disabled={disabled || i === 0}>↑</IconButton>
                  <IconButton label="Move down" onClick={() => move(i, 1)} disabled={disabled || i === scenes.length - 1}>↓</IconButton>
                  <IconButton label="Delete scene" onClick={() => remove(i)} disabled={disabled || scenes.length <= 1}>✕</IconButton>
                </div>
              </div>

              <div>
                <label className="text-[11px] text-slate-400 font-semibold flex justify-between">
                  <span>Narration</span>
                  <span className="font-normal text-slate-500">
                    {words} words{scene.duration ? ` · ${scene.duration.toFixed(1)}s spoken` : ` · ~${Math.round(words / 2.5)}s`}
                  </span>
                </label>
                <textarea
                  rows={3}
                  value={scene.narration}
                  disabled={disabled}
                  maxLength={1500}
                  onChange={(e) => update(i, { narration: e.target.value })}
                  className={fieldClass}
                />
              </div>

              <div>
                <label className="text-[11px] text-slate-400 font-semibold">Image prompt</label>
                <textarea
                  rows={2}
                  value={scene.visual_prompt}
                  disabled={disabled}
                  maxLength={1500}
                  onChange={(e) => update(i, { visual_prompt: e.target.value })}
                  className={fieldClass}
                />
              </div>

              <div>
                <label className="text-[11px] text-slate-400 font-semibold">On-screen title (optional)</label>
                <input
                  value={scene.on_screen_text}
                  disabled={disabled}
                  maxLength={80}
                  onChange={(e) => update(i, { on_screen_text: e.target.value })}
                  className={fieldClass}
                />
              </div>
            </div>
          </div>
        );
      })}

      {scenes.length < 12 && (
        <button
          onClick={add}
          disabled={disabled}
          className="w-full py-3 rounded-2xl border border-dashed border-slate-700 text-xs font-semibold text-slate-400 hover:text-indigo-300 hover:border-indigo-500/50 transition disabled:opacity-50"
        >
          + Add scene
        </button>
      )}
    </div>
  );
}

function IconButton({ label, onClick, disabled, children }: { label: string; onClick: () => void; disabled: boolean; children: React.ReactNode }) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      onClick={onClick}
      disabled={disabled}
      className="h-7 w-7 rounded-lg bg-slate-800 text-slate-300 text-xs hover:bg-slate-700 disabled:opacity-30 disabled:hover:bg-slate-800"
    >
      {children}
    </button>
  );
}
