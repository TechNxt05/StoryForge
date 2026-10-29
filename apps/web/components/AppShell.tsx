"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearSession, getHealth, getStoredUser, User } from "../lib/api";

const NAV_LINKS = [
  { href: "/", label: "Studio" },
  { href: "/assets", label: "Assets" },
  { href: "/analytics", label: "Analytics" },
  { href: "/settings", label: "Settings" },
];

type ServerState = "checking" | "online" | "waking" | "offline";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const [showDropdown, setShowDropdown] = useState(false);
  const [server, setServer] = useState<ServerState>("checking");

  useEffect(() => {
    const sync = () => setUser(getStoredUser());
    sync();
    window.addEventListener("storyforge-auth", sync);
    window.addEventListener("storage", sync);
    return () => {
      window.removeEventListener("storyforge-auth", sync);
      window.removeEventListener("storage", sync);
    };
  }, []);

  // Free hosts sleep when idle; the first request can take ~30-60s to wake the API.
  useEffect(() => {
    let cancelled = false;
    let attempts = 0;
    const ping = async () => {
      try {
        await getHealth();
        if (!cancelled) setServer("online");
      } catch {
        attempts += 1;
        if (cancelled) return;
        setServer(attempts > 8 ? "offline" : "waking");
        if (attempts <= 8) setTimeout(ping, 8000);
      }
    };
    ping();
    return () => {
      cancelled = true;
    };
  }, []);

  const handleLogout = () => {
    clearSession();
    setShowDropdown(false);
    router.push("/auth");
  };

  const isActive = (href: string) => (href === "/" ? pathname === "/" || pathname.startsWith("/studio") : pathname.startsWith(href));

  const serverBadge = {
    checking: { dot: "bg-slate-500", text: "Connecting…" },
    online: { dot: "bg-emerald-500", text: "API online" },
    waking: { dot: "bg-amber-400 animate-pulse", text: "Waking server…" },
    offline: { dot: "bg-rose-500", text: "API offline" },
  }[server];

  return (
    <>
      <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-[#090d16]/85 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 md:px-6 py-3 flex items-center justify-between gap-4">
          <div className="flex items-center gap-6 min-w-0">
            <Link href="/" className="flex items-center gap-2.5 shrink-0">
              <div className="h-9 w-9 rounded-xl gradient-button flex items-center justify-center font-bold text-white shadow-lg">SF</div>
              <span className="font-extrabold text-lg tracking-tight text-white hidden sm:inline">
                StoryForge <span className="gradient-text">AI</span>
              </span>
            </Link>

            <nav className="hidden md:flex items-center gap-1 text-xs font-semibold text-slate-300">
              {NAV_LINKS.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`px-3 py-1.5 rounded-lg transition ${
                    isActive(link.href)
                      ? "bg-indigo-600/20 text-indigo-300 border border-indigo-500/30"
                      : "border border-transparent hover:text-indigo-300 hover:bg-slate-800/50"
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </nav>
          </div>

          <div className="flex items-center gap-3">
            <div
              className="px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-medium text-slate-400 flex items-center gap-2"
              title={server === "waking" ? "Free hosting sleeps when idle. The first request can take up to a minute." : undefined}
            >
              <span className={`h-2 w-2 rounded-full ${serverBadge.dot}`} />
              <span className="hidden sm:inline">{serverBadge.text}</span>
            </div>

            {user ? (
              <div className="relative">
                <button
                  onClick={() => setShowDropdown(!showDropdown)}
                  className="px-3 py-1.5 rounded-full bg-indigo-600/30 border border-indigo-500/40 text-xs font-bold text-indigo-200 flex items-center gap-1.5 hover:bg-indigo-600/50 transition max-w-[10rem]"
                >
                  <span className="truncate">{user.full_name || user.email}</span>
                  <span className="text-[10px]">▾</span>
                </button>

                {showDropdown && (
                  <div className="absolute right-0 mt-2 w-48 glass-card rounded-xl border border-slate-700 shadow-2xl overflow-hidden z-50">
                    <div className="px-4 py-2.5 text-[11px] text-slate-400 border-b border-slate-800 truncate">{user.email}</div>
                    <Link
                      href="/settings"
                      onClick={() => setShowDropdown(false)}
                      className="block px-4 py-2.5 text-xs font-medium text-slate-300 hover:bg-slate-800 hover:text-white transition"
                    >
                      Settings
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2.5 text-xs font-medium text-rose-400 hover:bg-rose-500/10 transition border-t border-slate-800"
                    >
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              pathname !== "/auth" && (
                <Link href="/auth" className="px-4 py-1.5 rounded-xl gradient-button text-xs font-bold text-white shadow-lg">
                  Sign in
                </Link>
              )
            )}
          </div>
        </div>

        {/* Mobile navigation */}
        <nav className="md:hidden flex items-center gap-1 px-4 pb-2 overflow-x-auto text-xs font-semibold text-slate-300">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`px-3 py-1.5 rounded-lg whitespace-nowrap ${isActive(link.href) ? "bg-indigo-600/20 text-indigo-300" : "hover:bg-slate-800/50"}`}
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6 md:p-8">{children}</main>

      <footer className="border-t border-slate-800/60 py-6 text-center text-xs text-slate-500">
        StoryForge AI — topic to narrated short video with free AI providers
      </footer>
    </>
  );
}
