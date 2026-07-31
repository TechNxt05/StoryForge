"use client";

import React, { useState } from "react";

interface EditorChatProps {
  onSendMessage: (message: string) => Promise<void>;
  isProcessing: boolean;
}

export default function EditorChat({ onSendMessage, isProcessing }: EditorChatProps) {
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; text: string }[]>([
    { role: "assistant", text: "I've generated your video timeline! What would you like to tweak? You can ask me to adjust brightness, change voiceovers, or add new media." },
  ]);
  const [input, setInput] = useState("");

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isProcessing) return;

    const userMsg = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: userMsg }]);

    await onSendMessage(userMsg);

    // After processing, add a generic assistant response (in real app, this comes from backend)
    setMessages((prev) => [
      ...prev,
      { role: "assistant", text: "I've updated the timeline based on your request. Check the timeline editor above!" },
    ]);
  };

  return (
    <div className="flex flex-col h-[400px] bg-slate-900 rounded-xl border border-slate-800">
      <div className="p-4 border-b border-slate-800 bg-slate-900/80 rounded-t-xl">
        <h3 className="font-bold text-slate-200 text-sm flex items-center space-x-2">
          <span>✨</span>
          <span>StoryForge Assistant</span>
        </h3>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${
                msg.role === "user"
                  ? "bg-indigo-600 text-white rounded-br-none"
                  : "bg-slate-800 text-slate-200 rounded-bl-none border border-slate-700"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        {isProcessing && (
          <div className="flex justify-start">
            <div className="max-w-[85%] rounded-2xl px-4 py-2.5 text-sm bg-slate-800 text-slate-400 rounded-bl-none border border-slate-700 flex space-x-2 items-center">
              <span className="animate-bounce">●</span>
              <span className="animate-bounce" style={{ animationDelay: "150ms" }}>●</span>
              <span className="animate-bounce" style={{ animationDelay: "300ms" }}>●</span>
            </div>
          </div>
        )}
      </div>

      <div className="p-3 border-t border-slate-800 bg-slate-900/50 rounded-b-xl">
        <form onSubmit={handleSend} className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isProcessing}
            placeholder="Type 'Make the first video brighter'..."
            className="w-full bg-slate-950 border border-slate-700 rounded-full py-3 pl-4 pr-12 text-sm text-slate-200 focus:outline-none focus:border-indigo-500 transition disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || isProcessing}
            className="absolute right-2 top-2 p-1.5 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white disabled:opacity-50 disabled:bg-slate-700 transition"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4">
              <path d="M3.105 2.289a.75.75 0 00-.826.95l1.414 4.925A1.5 1.5 0 005.135 9.25h6.115a.75.75 0 010 1.5H5.135a1.5 1.5 0 00-1.442 1.086l-1.414 4.926a.75.75 0 00.826.95 28.896 28.896 0 0015.293-7.154.75.75 0 000-1.115A28.897 28.897 0 003.105 2.289z" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}
