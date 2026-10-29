import type { Metadata } from "next";
import AppShell from "../components/AppShell";
import "./globals.css";

export const metadata: Metadata = {
  title: "StoryForge AI — Topic to narrated short video",
  description:
    "Type a topic and StoryForge researches it, writes the script, generates scene images, narrates it and renders a captioned MP4 — using free AI providers.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-[#090d16] text-slate-100 min-h-screen flex flex-col">
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
