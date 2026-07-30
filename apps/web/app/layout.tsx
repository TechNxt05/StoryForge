"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import "./globals.css";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const router = useRouter();
  const pathname = usePathname();
  const [userName, setUserName] = useState<string | null>(null);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined") {
      const storedUser = localStorage.getItem("storyforge_user");
      if (storedUser) {
        try {
          const parsed = JSON.parse(storedUser);
          setUserName(parsed.full_name || parsed.email || "USER");
        } catch {
          setUserName(null);
        }
      } else {
        setUserName(null);
      }
    }
  }, [pathname]);

  const handleLogout = () => {
    localStorage.removeItem("storyforge_token");
    localStorage.removeItem("storyforge_user");
    setUserName(null);
    setShowDropdown(false);
    router.push("/auth");
  };

  const navLinks = [
    { href: "/", label: "Studio" },
    { href: "/analytics", label: "Analytics" },
    { href: "/assets", label: "Assets" },
    { href: "/knowledge", label: "Knowledge RAG" },
    { href: "/settings", label: "Settings" },
  ];

  return (
    <html lang="en" className="dark">
      <head>
        <title>StoryForge AI — Autonomous Video Creation Platform</title>
        <meta name="description" content="StoryForge AI coordinates research, scriptwriting, voice cloning, keyframe synthesis, and FFmpeg video rendering to produce cinema-quality short videos autonomously." />
      </head>
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

            <nav className="hidden md:flex items-center space-x-1 text-xs font-semibold text-slate-300">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`px-3 py-1.5 rounded-lg transition ${
                    pathname === link.href
                      ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/30"
                      : "hover:text-indigo-400 hover:bg-slate-800/50"
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </nav>
          </div>

          <div className="flex items-center space-x-4">
            <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-medium text-slate-400 flex items-center space-x-2">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="hidden sm:inline">Runtime Engine Online</span>
            </div>

            {userName ? (
              <div className="relative">
                <button
                  onClick={() => setShowDropdown(!showDropdown)}
                  className="px-3 py-1.5 rounded-full bg-indigo-600/30 border border-indigo-500/40 text-xs font-bold text-indigo-300 flex items-center space-x-1.5 hover:bg-indigo-600/50 transition"
                >
                  <span>👤</span>
                  <span>{userName}</span>
                  <span className="text-[10px] ml-1">▾</span>
                </button>

                {showDropdown && (
                  <div className="absolute right-0 mt-2 w-44 glass-card rounded-xl border border-slate-700 shadow-2xl overflow-hidden z-50">
                    <Link
                      href="/settings"
                      onClick={() => setShowDropdown(false)}
                      className="block px-4 py-2.5 text-xs font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition"
                    >
                      ⚙️ Settings
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2.5 text-xs font-medium text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 transition border-t border-slate-800"
                    >
                      🚪 Sign Out
                    </button>
                  </div>
                )}
              </div>
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
