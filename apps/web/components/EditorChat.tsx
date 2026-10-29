"use client";

import React, { useEffect, useRef, useState } from "react";

interface EditorChatProps {
  history: { role: "user" | "assistant"; text: string }[];
  onSendMessage: (message: string) => Promise<void>;
  isProcessing: boolean;
  disabled: boolean;
  error: string;
}

const SUGGESTIONS = ["Make the hook more dramatic", "Shorten every scene", "Add a call to action at the end", "Use simpler words for kids"];

export default function EditorChat({ history, onSendMessage, isProcessing, disabled, error }: EditorChatProps) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [history.length, isProcessing]);

  const send = async (text: string) => {
    if (!text.trim() || isProcessing || disabled) return;
    setInput("");
    await onSendMessage(text.trim());
  };

  return (
    <div className="flex flex-col h-[420px] bg-slate-900 rounded-2xl border border-slate-800">
      <div className="p-4 border-b border-slate-800">
        <h3 className="font-bold text-slate-200 text-sm">AI script editor</h3>
        <p className="text-[11px] text-slate-500">Describe a change; the script updates, then re-render.</p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {history.length === 0 && (
          <div className="space-y-2">
            <p className="text-xs text-slate-400">Try:</p>
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => send(s)}
                disabled={disabled || isProcessing}
                className="block w-full text-left px-3 py-2 rounded-xl bg-slate-800/70 border border-slate-700 text-xs text-slate-300 hover:border-indigo-500/50 disabled:opacity-50"
              >
                {s}
              </button>
            ))}
          </div>
        )}
        {history.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[85%] rounded-2xl px-3.5 py-2 text-xs leading-relaxed ${
                msg.role === "user" ? "bg-indigo-600 text-white rounded-br-none" : "bg-slate-800 text-slate-200 rounded-bl-none border border-slate-700"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        {isProcessing && (
          <div className="flex justify-start">
            <div className="rounded-2xl px-4 py-2.5 text-xs bg-slate-800 text-slate-400 rounded-bl-none border border-slate-700">Rewriting the script…</div>
          </div>
        )}
        {error && <div className="text-xs text-rose-300 bg-rose-500/10 border border-rose-500/30 rounded-xl p-2.5">{error}</div>}
        <div ref={bottomRef} />
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="p-3 border-t border-slate-800 flex gap-2"
      >
        <input
          type="text"
          value={input}
          maxLength={1000}
          onChange={(e) => setInput(e.target.value)}
          disabled={isProcessing || disabled}
          placeholder={disabled ? "Available once the script exists" : "e.g. Make scene 2 about the Bible"}
          aria-label="Instruction for the AI editor"
          className="flex-1 min-w-0 bg-slate-950 border border-slate-700 rounded-full py-2.5 px-4 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={!input.trim() || isProcessing || disabled}
          className="px-4 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold disabled:opacity-50 disabled:bg-slate-700"
        >
          Send
        </button>
      </form>
    </div>
  );
}
