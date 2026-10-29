"use client";

import React, { useCallback, useEffect, useState } from "react";
import { getProviders, getStoredUser, ProviderStatus, setProviderKey, User } from "../../lib/api";
import { useRequireAuth } from "../../lib/useRequireAuth";

export default function SettingsPage() {
  const ready = useRequireAuth();
  const [providers, setProviders] = useState<ProviderStatus[]>([]);
  const [llmOrder, setLlmOrder] = useState<string[]>([]);
  const [storage, setStorage] = useState("");
  const [canEdit, setCanEdit] = useState(false);
  const [error, setError] = useState("");
  const [user, setUser] = useState<User | null>(null);

  const load = useCallback(() => {
    getProviders()
      .then((res) => {
        setProviders(res.providers);
        setLlmOrder(res.llm_order);
        setStorage(res.storage);
        setCanEdit(res.can_edit);
      })
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!ready) return;
    setUser(getStoredUser());
    load();
  }, [ready, load]);

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="pb-4 border-b border-slate-800">
        <h1 className="text-2xl font-extrabold text-white">Settings</h1>
        {user && <p className="text-xs text-slate-400 mt-1">Signed in as {user.full_name} ({user.email})</p>}
      </div>

      {error && <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">{error}</div>}

      <div className="glass-card rounded-2xl p-5 border border-slate-800 space-y-2 text-xs text-slate-300">
        <h2 className="font-bold text-sm text-white">How generation is powered</h2>
        <p>
          Script writers are tried in order: <span className="font-mono text-indigo-300">{llmOrder.join(" → ") || "—"}</span>. Videos are stored on{" "}
          <span className="font-mono text-indigo-300">{storage === "cloudinary" ? "Cloudinary (permanent)" : "the API server (lost when a free server restarts)"}</span>.
        </p>
        <p className="text-slate-400">
          Everything works with zero keys, but free keys make it faster and better. Keys are configured as environment variables on the API server
          (e.g. in the Render dashboard) and are never shown here.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {providers.map((p) => (
          <ProviderCard key={p.id} provider={p} canEdit={canEdit} onSaved={load} />
        ))}
      </div>
    </div>
  );
}

function ProviderCard({ provider, canEdit, onSaved }: { provider: ProviderStatus; canEdit: boolean; onSaved: () => void }) {
  const [values, setValues] = useState<Record<string, string>>({});
  const [msg, setMsg] = useState("");
  const [saving, setSaving] = useState(false);

  const status = provider.configured
    ? { text: "Configured", cls: "bg-emerald-500/10 text-emerald-300 border-emerald-500/30" }
    : provider.active
      ? { text: "Active (no key)", cls: "bg-sky-500/10 text-sky-300 border-sky-500/30" }
      : { text: "Not configured", cls: "bg-slate-800 text-slate-400 border-slate-700" };

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMsg("");
    try {
      for (const [env, value] of Object.entries(values)) {
        if (value.trim()) await setProviderKey(env, value.trim());
      }
      setValues({});
      setMsg("Applied until the next server restart. Add it to the host's environment to keep it.");
      onSaved();
    } catch (err) {
      setMsg((err as Error).message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col">
      <div className="flex items-start justify-between gap-3 mb-2">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-wider text-slate-500">{provider.category}</p>
          <h3 className="font-bold text-sm text-white">{provider.name}</h3>
        </div>
        <span className={`px-2 py-0.5 rounded-full border text-[10px] font-semibold whitespace-nowrap ${status.cls}`}>{status.text}</span>
      </div>
      <p className="text-xs text-slate-400 flex-1">{provider.free}</p>
      {provider.env.length > 0 && (
        <p className="text-[11px] text-slate-500 font-mono mt-2 break-all">{provider.env.join(", ")}</p>
      )}
      {provider.signup && (
        <a href={provider.signup} target="_blank" rel="noreferrer" className="text-xs text-indigo-300 hover:underline mt-2 font-semibold">
          Get a free key ↗
        </a>
      )}
      {canEdit && provider.env.length > 0 && (
        <form onSubmit={save} className="mt-3 pt-3 border-t border-slate-800 space-y-2">
          {provider.env.map((env) => (
            <input
              key={env}
              type="password"
              autoComplete="off"
              placeholder={env}
              aria-label={env}
              value={values[env] || ""}
              onChange={(e) => setValues({ ...values, [env]: e.target.value })}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          ))}
          <button type="submit" disabled={saving} className="px-3 py-1.5 rounded-lg bg-indigo-600 text-xs font-semibold text-white disabled:opacity-50">
            {saving ? "Saving…" : "Apply (admin)"}
          </button>
          {msg && <p className="text-[11px] text-slate-400">{msg}</p>}
        </form>
      )}
    </div>
  );
}
