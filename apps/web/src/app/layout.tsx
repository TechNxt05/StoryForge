import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'StoryForge AI Studio',
  description: 'AI Agentic Storytelling Platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div id="app-root">{children}</div>
      </body>
    </html>
  );
}
