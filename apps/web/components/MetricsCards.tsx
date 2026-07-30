"use client";

import React from "react";

interface MetricsCardsProps {
  timeframe?: string;
}

export default function MetricsCards({ timeframe = "7d" }: MetricsCardsProps) {
  const getMetrics = () => {
    switch (timeframe) {
      case "24h":
        return [
          { title: "Est. Cost (24h)", value: "$1.85", change: "-2.1%", color: "text-emerald-400" },
          { title: "Avg Render Time", value: "11.8s", change: "-0.8s", color: "text-indigo-400" },
          { title: "Pipeline Success", value: "100.0%", change: "+0.6%", color: "text-emerald-400" },
          { title: "Tokens & Assets", value: "180K Tokens", change: "+5.2%", color: "text-purple-400" },
        ];
      case "30d":
        return [
          { title: "Est. Cost (30d)", value: "$48.90", change: "-12.4%", color: "text-emerald-400" },
          { title: "Avg Render Time", value: "16.4s", change: "-3.2s", color: "text-indigo-400" },
          { title: "Pipeline Success", value: "98.8%", change: "+1.2%", color: "text-emerald-400" },
          { title: "Tokens & Assets", value: "5.4M Tokens", change: "+24.0%", color: "text-purple-400" },
        ];
      case "7d":
      default:
        return [
          { title: "Est. Cost (7d)", value: "$12.45", change: "-8.2%", color: "text-emerald-400" },
          { title: "Avg Render Time", value: "14.2s", change: "-1.5s", color: "text-indigo-400" },
          { title: "Pipeline Success", value: "99.4%", change: "+0.6%", color: "text-emerald-400" },
          { title: "Tokens & Assets", value: "1.2M Tokens", change: "+14.0%", color: "text-purple-400" },
        ];
    }
  };

  const cards = getMetrics();

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
