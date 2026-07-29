"use client";

import React from "react";

export interface DAGNode {
  id: string;
  name: string;
  capability: string;
  modelUsed: string;
  apiKeyType: "Zero-Key (Free)" | "Free API Key" | "Local Execution" | "Paid Tier API";
  status: "completed" | "running" | "pending" | "failed";
  duration: string;
}

interface DAGNodeCanvasProps {
  nodes: DAGNode[];
  selectedNodeId: string;
  onSelectNode: (nodeId: string) => void;
}

export default function DAGNodeCanvas({ nodes, selectedNodeId, onSelectNode }: DAGNodeCanvasProps) {
  const completedCount = nodes.filter((n) => n.status === "completed").length;
  const progressPercent = Math.round((completedCount / nodes.length) * 100);

  return (
    <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-5">
      {/* Header & Overall Generation Progress Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h3 className="font-bold text-sm text-slate-200 uppercase tracking-wider">
              Reel Generation DAG Roadmap
            </h3>
            <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-[11px] font-bold">
              {completedCount} of {nodes.length} Steps Completed
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time multi-agent execution pipeline with model & API key transparency.
          </p>
        </div>

        {/* Progress Bar Display */}
        <div className="w-full md:w-64 space-y-1.5">
          <div className="flex justify-between text-xs font-semibold">
            <span className="text-slate-300">Total Progress</span>
            <span className="text-indigo-400">{progressPercent}%</span>
          </div>
          <div className="w-full h-2.5 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
            <div
              className="h-full gradient-button transition-all duration-500 rounded-full"
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Horizontal Step Roadmap Node Cards */}
      <div className="flex items-center space-x-3 overflow-x-auto pb-2 scrollbar-none">
        {nodes.map((node, idx) => {
          const isSelected = node.id === selectedNodeId;
          let statusBadge = "bg-slate-800 text-slate-400 border-slate-700";
          let icon = "⏳";

          if (node.status === "completed") {
            statusBadge = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
            icon = "✓";
          } else if (node.status === "running") {
            statusBadge = "bg-indigo-500/10 text-indigo-400 border-indigo-500/30 animate-pulse";
            icon = "⚡";
          }

          return (
            <React.Fragment key={node.id}>
              {idx > 0 && <div className="h-0.5 w-6 bg-slate-800 flex-shrink-0"></div>}

              <button
                onClick={() => onSelectNode(node.id)}
                className={`flex-shrink-0 glass-card rounded-xl p-3.5 text-left border transition w-52 ${
                  isSelected
                    ? "border-indigo-500 ring-2 ring-indigo-500/30 bg-indigo-950/20"
                    : "border-slate-800 hover:border-slate-700"
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-extrabold uppercase tracking-wider text-slate-400">
                    Step {idx + 1}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold border flex items-center space-x-1 ${statusBadge}`}>
                    <span>{icon}</span>
                    <span className="capitalize">{node.status}</span>
                  </span>
                </div>

                <div className="font-bold text-xs text-white line-clamp-1 mb-1">{node.name}</div>

                {/* Model & API Transparency Indicator */}
                <div className="mt-2 pt-2 border-t border-slate-800/80 space-y-1">
                  <div className="text-[10px] font-mono text-indigo-300 line-clamp-1">
                    🤖 {node.modelUsed}
                  </div>
                  <div className="text-[9px] font-semibold text-slate-400 flex items-center justify-between">
                    <span>🔑 {node.apiKeyType}</span>
                    <span className="text-slate-500 font-mono">{node.duration}</span>
                  </div>
                </div>
              </button>
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
