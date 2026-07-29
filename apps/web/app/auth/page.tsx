"use client";

import React, { useState } from "react";

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [statusMsg, setStatusMsg] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;

    if (isLogin) {
      setStatusMsg(`Authenticated as ${email}`);
    } else {
      setStatusMsg(`Created account for ${fullName} (${email})`);
    }
  };

  return (
    <div className="max-w-md mx-auto my-12 glass-card rounded-3xl p-8 border border-slate-800 shadow-2xl">
      <div className="text-center mb-6">
        <h1 className="text-2xl font-extrabold text-white">
          {isLogin ? "Welcome Back to StoryForge" : "Create StoryForge Account"}
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          {isLogin ? "Sign in to access your video projects" : "Start forging cinema-quality videos with AI"}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {!isLogin && (
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
              Full Name
            </label>
            <input
              type="text"
              required
              placeholder="e.g. Jane Creator"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
            />
          </div>
        )}

        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
            Email Address
          </label>
          <input
            type="email"
            required
            placeholder="admin@storyforge.ai"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
            Password
          </label>
          <input
            type="password"
            required
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <button type="submit" className="w-full gradient-button py-3 rounded-xl font-bold text-white shadow-lg mt-2">
          {isLogin ? "Sign In" : "Create Account"}
        </button>

        {statusMsg && <p className="text-center text-xs font-semibold text-emerald-400 mt-2">{statusMsg}</p>}
      </form>

      <div className="pt-6 mt-6 border-t border-slate-800 text-center">
        <button
          onClick={() => setIsLogin(!isLogin)}
          className="text-xs font-medium text-indigo-400 hover:text-indigo-300 transition"
        >
          {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
        </button>
      </div>
    </div>
  );
}
