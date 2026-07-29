"use client";

import React, { useState } from "react";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<"keys" | "workspace" | "preferences">("keys");
  const [provider, setProvider] = useState("gemini");
  const [apiKey, setApiKey] = useState("");
  const [savedStatus, setSavedStatus] = useState("");

  const handleSaveKey = (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiKey) return;

    setSavedStatus(`Saved key for ${provider.toUpperCase()}`);
    setApiKey("");

    setTimeout(() => setSavedStatus(""), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="pb-4 border-b border-slate-800">
        <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">Control Panel</span>
        <h1 className="text-2xl font-extrabold text-white mt-0.5">Platform Settings & Workspace</h1>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab("keys")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition ${
            activeTab === "keys" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-slate-200"
          }`}
        >
          API Keys & Providers
        </button>
        <button
          onClick={() => setActiveTab("workspace")}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition ${
            activeTab === "workspace" ? "bg-indigo-600 text-white" : "text-slate-400 hover:text-slate-200"
          }`}
        >
          Workspace & Team
        </button>
      </div>

      {/* Tab 1: API Keys */}
      {activeTab === "keys" && (
        <div className="glass-card rounded-2xl p-6 border border-slate-800 max-w-2xl space-y-6">
          <div>
            <h3 className="font-bold text-base text-white">Provider API Keys</h3>
            <p className="text-xs text-slate-400 mt-1">Configure your generative AI provider keys for failover execution.</p>
          </div>

          <form onSubmit={handleSaveKey} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                AI Provider
              </label>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none"
              >
                <option value="gemini">Google Gemini / Veo</option>
                <option value="flux">Black Forest Labs (FLUX.1)</option>
                <option value="kokoro">Kokoro TTS Engine</option>
                <option value="voiceai">VoiceAI / Edge-TTS</option>
                <option value="cloudinary">Cloudinary CDN</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                API Secret Key
              </label>
              <input
                type="password"
                required
                placeholder="sk-..."
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="flex items-center justify-between pt-2">
              <button type="submit" className="gradient-button px-5 py-2 rounded-xl text-xs font-bold text-white shadow-lg">
                Save API Key
              </button>

              {savedStatus && (
                <span className="text-xs font-semibold text-emerald-400">{savedStatus}</span>
              )}
            </div>
          </form>
        </div>
      )}

      {/* Tab 2: Workspace */}
      {activeTab === "workspace" && (
        <div className="glass-card rounded-2xl p-6 border border-slate-800 max-w-2xl space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-base text-white">Default Studio Workspace</h3>
              <p className="text-xs text-slate-400">Pro Agency Plan &bull; 42/250 Renders Used This Month</p>
            </div>
            <span className="px-3 py-1 rounded-full bg-indigo-500/20 border border-indigo-500/40 text-indigo-300 text-xs font-bold">
              PRO TIER
            </span>
          </div>

          <div className="w-full bg-slate-900 rounded-full h-2 overflow-hidden border border-slate-800">
            <div className="bg-indigo-500 h-full w-[17%]"></div>
          </div>

          <div>
            <h4 className="font-bold text-xs text-slate-300 uppercase tracking-wider mb-3">Team Members</h4>
            <div className="space-y-2">
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between text-xs">
                <div>
                  <span className="font-bold text-white">Admin Creator</span>
                  <span className="text-slate-400 block">admin@storyforge.ai</span>
                </div>
                <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-semibold uppercase text-[10px]">Owner</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
