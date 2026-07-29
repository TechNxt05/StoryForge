"use client";

import React, { useState } from "react";
import DAGNodeCanvas, { DAGNode } from "../../../components/DAGNodeCanvas";
import VideoPreviewPlayer from "../../../components/VideoPreviewPlayer";

export default function CanvasStudioPage() {
  const [selectedNodeId, setSelectedNodeId] = useState("node-1");

  const nodes: DAGNode[] = [
    {
      id: "node-1",
      name: "Deep Research",
      capability: "deep_research",
      modelUsed: "Gemini 1.5 Pro",
      apiKeyType: "Free API Key",
      status: "completed",
      duration: "1.2s",
    },
    {
      id: "node-2",
      name: "Fact Verification",
      capability: "fact_verification",
      modelUsed: "Groq Llama-3.3-70b",
      apiKeyType: "Free API Key",
      status: "completed",
      duration: "0.8s",
    },
    {
      id: "node-3",
      name: "Story Structure",
      capability: "story_structure_planner",
      modelUsed: "Claude 3.5 Sonnet",
      apiKeyType: "Free API Key",
      status: "completed",
      duration: "0.5s",
    },
    {
      id: "node-4",
      name: "Scriptwriter & Dialogue",
      capability: "scriptwriter",
      modelUsed: "Gemini 1.5 Flash",
      apiKeyType: "Free API Key",
      status: "completed",
      duration: "1.4s",
    },
    {
      id: "node-5",
      name: "Visual Storyboard",
      capability: "storyboard_generator",
      modelUsed: "FLUX.1-schnell",
      apiKeyType: "Zero-Key (Free)",
      status: "completed",
      duration: "2.1s",
    },
    {
      id: "node-6",
      name: "Voiceover Synthesis",
      capability: "voice_synthesizer",
      modelUsed: "Kokoro-82M ONNX",
      apiKeyType: "Local Execution",
      status: "completed",
      duration: "1.1s",
    },
    {
      id: "node-7",
      name: "FFmpeg Composition",
      capability: "ffmpeg_renderer",
      modelUsed: "FFmpeg H.264/AAC CLI",
      apiKeyType: "Local Execution",
      status: "running",
      duration: "3.5s",
    },
  ];

  const selectedNode = nodes.find((n) => n.id === selectedNodeId) || nodes[0];

  return (
    <div className="space-y-6">
      {/* Studio Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div>
          <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">
            Interactive Studio Canvas & DAG Roadmap
          </span>
          <h1 className="text-2xl font-extrabold text-white mt-0.5">The Invention of Printing Press</h1>
        </div>

        <div className="flex items-center space-x-3">
          <button className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition">
            Export Multi-Platform &rarr;
          </button>
          <button className="gradient-button px-5 py-2 rounded-xl text-xs font-bold text-white shadow-lg">
            Re-Run DAG Pipeline
          </button>
        </div>
      </div>

      {/* DAG Workflow Node Canvas & Progress Roadmap */}
      <DAGNodeCanvas
        nodes={nodes}
        selectedNodeId={selectedNodeId}
        onSelectNode={(id) => setSelectedNodeId(id)}
      />

      {/* Main Workspace Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Live Video Player Preview */}
        <div className="lg:col-span-1">
          <VideoPreviewPlayer
            aspectRatio="9:16"
            title="The Invention of Printing Press"
          />
        </div>

        {/* Right Column: Active Node Details & Live Logs */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-sm text-slate-200 uppercase tracking-wider">
                Selected Step: {selectedNode.name}
              </h3>
              <span className="px-2.5 py-1 rounded bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-mono">
                🤖 {selectedNode.modelUsed} ({selectedNode.apiKeyType})
              </span>
            </div>

            <div className="bg-slate-950/80 rounded-xl p-4 font-mono text-xs text-emerald-400 border border-slate-800 max-h-56 overflow-y-auto">
              <pre>
                {JSON.stringify(
                  {
                    step_id: selectedNode.id,
                    capability_name: selectedNode.capability,
                    model_executed: selectedNode.modelUsed,
                    api_key_tier: selectedNode.apiKeyType,
                    status: selectedNode.status,
                    execution_time: selectedNode.duration,
                    output_artifact: `${selectedNode.capability}_artifact_v1`,
                  },
                  null,
                  2
                )}
              </pre>
            </div>
          </div>

          <div className="glass-card rounded-2xl p-6 border border-slate-800">
            <h3 className="font-bold text-sm text-slate-300 uppercase tracking-wider mb-3">
              Live Agent Execution Logs & Provider Routing
            </h3>
            <div className="bg-slate-950/80 rounded-xl p-4 font-mono text-[11px] text-slate-300 space-y-1.5 border border-slate-800 max-h-48 overflow-y-auto">
              <div className="text-slate-500">[10:41:02.102] RuntimeEngine initialized workflow plan-101</div>
              <div className="text-emerald-400">[10:41:03.250] Step 1 Deep Research completed using Gemini 1.5 Pro (Free API Key)</div>
              <div className="text-emerald-400">[10:41:04.100] Step 2 Fact Verification completed using Groq Llama-3.3-70b (Free API Key)</div>
              <div className="text-emerald-400">[10:41:05.500] Step 5 Storyboard completed using FLUX.1-schnell (Zero-Key Free Mode)</div>
              <div className="text-emerald-400">[10:41:06.200] Step 6 Voice Synthesis completed using Kokoro-82M (Local Execution)</div>
              <div className="text-indigo-400">[10:41:06.800] Step 7 FFmpeg composition rendering MP4 via Local FFmpeg CLI...</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
