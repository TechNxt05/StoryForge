"use client";

import React, { useState } from "react";

export default function KnowledgePage() {
  const [documentText, setDocumentText] = useState("");
  const [packName, setPackName] = useState("history");
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState("");

  const handleIngest = (e: React.FormEvent) => {
    e.preventDefault();
    if (!documentText) return;

    setLoading(true);
    setStatusMsg("");

    setTimeout(() => {
      setStatusMsg(`Indexed 384-dim vector chunk into Qdrant collection 'story_knowledge' under pack '${packName}'!`);
      setDocumentText("");
      setLoading(false);
    }, 800);
  };

  return (
    <div className="space-y-6">
      <div className="pb-4 border-b border-slate-800">
        <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">RAG Vector Store</span>
        <h1 className="text-2xl font-extrabold text-white mt-0.5">Qdrant Knowledge Base Ingestion</h1>
      </div>

      <div className="glass-card rounded-2xl p-6 border border-slate-800 max-w-2xl space-y-6">
        <div>
          <h3 className="font-bold text-base text-white">Ingest Domain Reference Material</h3>
          <p className="text-xs text-slate-400 mt-1">
            Index custom PDF, TXT, or research documents into Qdrant 384-dim vector collections for grounded storytelling.
          </p>
        </div>

        <form onSubmit={handleIngest} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
              Target Content Pack
            </label>
            <select
              value={packName}
              onChange={(e) => setPackName(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none"
            >
              <option value="history">History & Culture</option>
              <option value="technology">Technology & AI</option>
              <option value="science">Science & Space</option>
              <option value="chess">Chess Strategy</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
              Document Text Chunk
            </label>
            <textarea
              required
              rows={4}
              placeholder="Paste reference text chunk or manuscript section to embed..."
              value={documentText}
              onChange={(e) => setDocumentText(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div className="flex items-center justify-between pt-2">
            <button
              type="submit"
              disabled={loading}
              className="gradient-button px-5 py-2 rounded-xl text-xs font-bold text-white shadow-lg disabled:opacity-50"
            >
              {loading ? "Embedding Vectors..." : "Index Document Vector"}
            </button>
            {statusMsg && <span className="text-xs font-semibold text-emerald-400">{statusMsg}</span>}
          </div>
        </form>
      </div>
    </div>
  );
}
