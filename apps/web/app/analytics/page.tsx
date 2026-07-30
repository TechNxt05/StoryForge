"use client";

import React, { useState } from "react";
import MetricsCards from "../../components/MetricsCards";
import ModelUsageChart from "../../components/ModelUsageChart";

export default function AnalyticsPage() {
  const [timeframe, setTimeframe] = useState("7d");

  return (
    <div className="space-y-6">
      {/* Header & Filter */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div>
          <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">Performance Intelligence</span>
          <h1 className="text-2xl font-extrabold text-white mt-0.5">Analytics & Model Metrics</h1>
        </div>

        <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-xl p-1">
          {["24h", "7d", "30d"].map((t) => (
            <button
              key={t}
              onClick={() => setTimeframe(t)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold uppercase transition ${
                timeframe === t ? "bg-indigo-600 text-white shadow-md" : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Metric Cards with active timeframe prop */}
      <MetricsCards timeframe={timeframe} />

      {/* Usage & Cost Distribution with active timeframe prop */}
      <ModelUsageChart timeframe={timeframe} />
    </div>
  );
}
