"use client";

import React from "react";

export default function ModelUsageChart() {
  const providers = [
    { name: "FLUX.1 (Image Gen)", usage: "450 Keyframes", share: "38%", cost: "$4.50", status: "Primary" },
    { name: "Google Veo (Video Gen)", usage: "120 Clips", share: "32%", cost: "$5.20", status: "Primary" },
    { name: "Gemini 1.5 (LLM)", usage: "1.2M Tokens", share: "18%", cost: "$1.80", status: "Primary" },
    { name: "Kokoro / VoiceAI (TTS)", usage: "85 Audios", share: "12%", cost: "$0.95", status: "Backup Failover Ready" },
  ];

  return (
    <div className="glass-card rounded-2xl p-6 border border-slate-800">
      <h3 className="font-bold text-sm text-slate-300 uppercase tracking-wider mb-4">
        AI Provider Usage & Cost Breakdown
      </h3>

      <div className="space-y-4">
        {providers.map((p, idx) => (
          <div key={idx} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="h-8 w-8 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 flex items-center justify-center font-bold text-xs">
                {idx + 1}
              </div>
              <div>
                <h4 className="font-bold text-xs text-white">{p.name}</h4>
                <p className="text-[11px] text-slate-400">{p.usage}</p>
              </div>
            </div>

            <div className="flex items-center space-x-6">
              <div className="text-right">
                <span className="block text-xs font-bold text-slate-200">{p.cost}</span>
                <span className="text-[10px] text-slate-400">{p.share} Share</span>
              </div>
              <span className="px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[10px] font-semibold">
                {p.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
