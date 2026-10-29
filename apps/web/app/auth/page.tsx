"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { loginUser, saveSession, signupUser } from "../../lib/api";

const inputClass =
  "w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-indigo-500";

export default function AuthPage() {
  const router = useRouter();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg("");

    try {
      const res = isLogin
        ? await loginUser({ email, password })
        : await signupUser({ email, password, full_name: fullName });
      saveSession(res.access_token, res.user);
      const next = new URLSearchParams(window.location.search).get("next");
      router.push(next && next.startsWith("/") && !next.startsWith("//") ? next : "/");
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Authentication failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto my-8 md:my-12 glass-card rounded-3xl p-6 md:p-8 border border-slate-800 shadow-2xl">
      <div className="text-center mb-6">
        <h1 className="text-2xl font-extrabold text-white">{isLogin ? "Welcome back" : "Create your account"}</h1>
        <p className="text-xs text-slate-400 mt-1">
          {isLogin ? "Sign in to your video projects" : "Turn any topic into a narrated short video — free"}
        </p>
      </div>

      {errorMsg && (
        <div role="alert" className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs font-semibold text-center">
          {errorMsg}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {!isLogin && (
          <div>
            <label htmlFor="full-name" className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
              Full name
            </label>
            <input id="full-name" type="text" required autoComplete="name" value={fullName} onChange={(e) => setFullName(e.target.value)} className={inputClass} />
          </div>
        )}

        <div>
          <label htmlFor="email" className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
            Email
          </label>
          <input id="email" type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} className={inputClass} />
        </div>

        <div>
          <label htmlFor="password" className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
            Password
          </label>
          <input
            id="password"
            type="password"
            required
            minLength={isLogin ? undefined : 8}
            autoComplete={isLogin ? "current-password" : "new-password"}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={inputClass}
          />
          {!isLogin && <p className="text-[11px] text-slate-500 mt-1">At least 8 characters.</p>}
        </div>

        <button type="submit" disabled={loading} className="w-full gradient-button py-3 rounded-xl font-bold text-white shadow-lg mt-2 disabled:opacity-50">
          {loading ? "Please wait…" : isLogin ? "Sign in" : "Create account"}
        </button>
      </form>

      <div className="pt-6 mt-6 border-t border-slate-800 text-center">
        <button
          onClick={() => {
            setIsLogin(!isLogin);
            setErrorMsg("");
          }}
          className="text-xs font-medium text-indigo-400 hover:text-indigo-300 transition"
        >
          {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
        </button>
      </div>
    </div>
  );
}
