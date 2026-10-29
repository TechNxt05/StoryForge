"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createProject, getMeta, Meta } from "../lib/api";

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const inputClass =
  "w-full bg-slate-900/90 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500";
const labelClass = "block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1";

const LANGUAGES = ["English", "Hindi", "Spanish", "French", "German", "Portuguese"];

export default function CreateProjectModal({ isOpen, onClose }: CreateProjectModalProps) {
  const router = useRouter();
  const [meta, setMeta] = useState<Meta | null>(null);
  const [title, setTitle] = useState("");
  const [topic, setTopic] = useState("");
  const [notes, setNotes] = useState("");
  const [contentPack, setContentPack] = useState("history");
  const [aspectRatio, setAspectRatio] = useState("9:16");
  const [duration, setDuration] = useState(45);
  const [voice, setVoice] = useState("en-US-AndrewNeural");
  const [language, setLanguage] = useState("English");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    if (!isOpen || meta) return;
    getMeta()
      .then((m) => {
        setMeta(m);
        setVoice(m.default_voice);
      })
      .catch((err) => setErrorMsg(err.message));
  }, [isOpen, meta]);

  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");
    try {
      const project = await createProject({
        title: title.trim(),
        topic: topic.trim(),
        content_pack_name: contentPack,
        aspect_ratio: aspectRatio,
        notes,
        target_seconds: duration,
        voice,
        language,
      });
      router.push(`/studio/${project.id}`);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Could not create the project.");
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-start md:items-center justify-center bg-black/70 backdrop-blur-sm p-4 overflow-y-auto" onClick={onClose}>
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="create-title"
        className="glass-card max-w-2xl w-full rounded-2xl p-6 relative border border-slate-700/80 shadow-2xl my-8"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="create-title" className="text-xl font-bold mb-1 text-white">
          New video
        </h2>
        <p className="text-xs text-slate-400 mb-5">Generation starts right away and usually takes 2–5 minutes on free providers.</p>

        {errorMsg && (
          <div role="alert" className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-medium">
            {errorMsg}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="p-title" className={labelClass}>Title</label>
            <input id="p-title" type="text" required maxLength={200} placeholder="e.g. The Invention of the Printing Press" value={title} onChange={(e) => setTitle(e.target.value)} className={inputClass} />
          </div>

          <div>
            <label htmlFor="p-topic" className={labelClass}>What is the video about?</label>
            <textarea id="p-topic" required minLength={3} maxLength={2000} rows={3} placeholder="e.g. How Gutenberg's movable type spread knowledge across Europe" value={topic} onChange={(e) => setTopic(e.target.value)} className={inputClass} />
          </div>

          <div>
            <label htmlFor="p-notes" className={labelClass}>
              Notes &amp; reference material <span className="normal-case font-normal text-slate-500">(optional)</span>
            </label>
            <textarea
              id="p-notes"
              rows={3}
              maxLength={6000}
              placeholder="Facts to include, tone, audience, a call to action, or paste source text. The writer follows these closely."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              className={inputClass}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label htmlFor="p-pack" className={labelClass}>Style</label>
              <select id="p-pack" value={contentPack} onChange={(e) => setContentPack(e.target.value)} className={inputClass}>
                {(meta?.content_packs || [{ id: "history", label: "History & Culture" }]).map((p) => (
                  <option key={p.id} value={p.id}>{p.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="p-aspect" className={labelClass}>Format</label>
              <select id="p-aspect" value={aspectRatio} onChange={(e) => setAspectRatio(e.target.value)} className={inputClass}>
                {(meta?.aspect_ratios || [{ id: "9:16", label: "9:16 Vertical" }]).map((a) => (
                  <option key={a.id} value={a.id}>{a.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="p-voice" className={labelClass}>Narrator voice</label>
              <select id="p-voice" value={voice} onChange={(e) => setVoice(e.target.value)} className={inputClass}>
                {(meta?.voices || []).map((v) => (
                  <option key={v.id} value={v.id}>{v.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="p-lang" className={labelClass}>Script language</label>
              <select id="p-lang" value={language} onChange={(e) => setLanguage(e.target.value)} className={inputClass}>
                {LANGUAGES.map((l) => (
                  <option key={l} value={l}>{l}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="p-duration" className={`${labelClass} flex justify-between`}>
              <span>Target length</span>
              <span className="text-indigo-300 normal-case">{duration}s</span>
            </label>
            <input id="p-duration" type="range" min={15} max={90} step={5} value={duration} onChange={(e) => setDuration(Number(e.target.value))} className="w-full accent-indigo-500" />
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <button type="button" onClick={onClose} className="px-4 py-2 rounded-xl text-sm font-medium text-slate-400 hover:text-slate-200 transition">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="gradient-button px-5 py-2 rounded-xl text-sm font-bold text-white shadow-lg disabled:opacity-50">
              {loading ? "Creating…" : "Create & generate"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
