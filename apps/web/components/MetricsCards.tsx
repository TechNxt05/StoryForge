"use client";

import React from "react";

export default function MetricsCards() {
  const cards = [
    { title: "Total Est. Cost", value: "$12.45", change: "-8.2%", color: "text-emerald-400" },
    { title: "Avg Render Time", value: "14.2s", change: "-1.5s", color: "text-indigo-400" },
    { title: "Pipeline Success Rate", value: "99.4%", change: "+0.6%", color: "text-emerald-400" },
    { title: "Tokens & Assets", value: "1.2M Tokens", change: "+14.0%", color: "text-purple-400" },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, idx) => (
        <div key={idx} className="glass-card rounded-2xl p-5 border border-slate-800">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-400 text-xs font-medium uppercase tracking-wider">{card.title}</span>
            <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
              {card.change}
            </span>
          </div>
          <p className={`text-2xl font-extrabold mt-1 ${card.color}`}>{card.value}</p>
        </div>
      ))}
    </div>
  );
}
