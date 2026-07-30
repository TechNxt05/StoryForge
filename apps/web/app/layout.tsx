"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import "./globals.css";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const [userName, setUserName] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedUser = localStorage.getItem("storyforge_user");
      if (storedUser) {
        try {
          const parsed = JSON.parse(storedUser);
          setUserName(parsed.full_name || parsed.email || "USER");
        } catch {
          setUserName("USER");
        }
      }
    }
  }, []);

  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-[#090d16] text-slate-100 min-h-screen flex flex-col">
        {/* Navigation Header */}
        <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-[#090d16]/80 backdrop-blur-md px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-6">
            <Link href="/" className="flex items-center space-x-3">
              <div className="h-9 w-9 rounded-xl gradient-button flex items-center justify-center font-bold text-white shadow-lg">
                SF
              </div>
              <span className="font-extrabold text-xl tracking-tight text-white">
                StoryForge <span className="gradient-text">AI</span>
              </span>
            </Link>

            <nav className="hidden md:flex items-center space-x-4 text-xs font-semibold text-slate-300">
              <Link href="/" className="hover:text-indigo-400 transition">Studio</Link>
              <Link href="/analytics" className="hover:text-indigo-400 transition">Analytics</Link>
              <Link href="/assets" className="hover:text-indigo-400 transition">Assets</Link>
              <Link href="/knowledge" className="hover:text-indigo-400 transition">Knowledge RAG</Link>
              <Link href="/settings" className="hover:text-indigo-400 transition">Settings</Link>
            </nav>
          </div>

          <div className="flex items-center space-x-4">
            <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-medium text-slate-400 flex items-center space-x-2">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="hidden sm:inline">Runtime Engine Online</span>
            </div>

            {userName ? (
              <Link href="/settings" className="px-3 py-1.5 rounded-full bg-indigo-600/30 border border-indigo-500/40 text-xs font-bold text-indigo-300 flex items-center space-x-1.5">
                <span>👤</span>
                <span>{userName}</span>
              </Link>
            ) : (
              <Link href="/auth" className="px-4 py-1.5 rounded-xl gradient-button text-xs font-bold text-white shadow-lg">
                Sign In
              </Link>
            )}
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 max-w-7xl w-full mx-auto p-6 md:p-8">{children}</main>

        {/* Footer */}
        <footer className="border-t border-slate-800/60 py-6 text-center text-xs text-slate-500">
          StoryForge AI Platform &copy; 2026 — Autonomous Multi-Agent Media Pipeline
        </footer>
      </body>
    </html>
  );
}
