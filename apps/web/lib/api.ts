export const API_BASE = (process.env.NEXT_PUBLIC_API_URL || "https://storyforge-snc4.onrender.com").replace(/\/$/, "");

const TOKEN_KEY = "storyforge_token";
const USER_KEY = "storyforge_user";

export type StepStatus = "pending" | "running" | "completed" | "skipped" | "failed";

export interface JobStep {
  label: string;
  status: StepStatus;
  provider?: string;
  model?: string;
  detail?: string;
  started_at?: string;
  finished_at?: string;
}

export interface Job {
  mode: "full" | "rerender";
  status: "queued" | "running" | "completed" | "failed";
  steps: Record<string, JobStep>;
  error?: string | null;
  queued_at?: string;
  started_at?: string;
  finished_at?: string;
}

export interface Scene {
  heading: string;
  narration: string;
  visual_prompt: string;
  on_screen_text: string;
  image_url?: string;
  image_provider?: string;
  duration?: number;
  voice_provider?: string;
}

export interface Script {
  title: string;
  logline?: string;
  facts?: string[];
  scenes: Scene[];
  provider?: string;
  model?: string;
  warning?: string;
  sources?: { title: string; url: string }[];
}

export interface VideoInfo {
  url: string;
  bytes: number;
  storage: string;
  duration: number;
  width: number;
  height: number;
  created_at?: string;
}

export interface ProjectSummary {
  id: string;
  title: string;
  topic: string;
  content_pack_name: string;
  status: "draft" | "queued" | "generating" | "completed" | "failed";
  created_at: string;
  updated_at: string;
  aspect_ratio: string;
  thumbnail_url: string | null;
  video: VideoInfo | null;
  progress: number;
  scene_count: number;
  providers: { llm?: string; images?: string[]; voice?: string[]; storage?: string } | null;
}

export interface Project extends ProjectSummary {
  settings: { aspect_ratio: string; notes: string; target_seconds: number; voice: string; language: string };
  script: Script | null;
  job: Job | null;
  stale: boolean;
  history: { url: string; duration: number; at: string }[];
  chat: { role: "user" | "assistant"; text: string; at: string }[];
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

export interface Meta {
  content_packs: { id: string; label: string; style: string }[];
  voices: { id: string; label: string }[];
  default_voice: string;
  aspect_ratios: { id: string; label: string }[];
  steps: { id: string; label: string }[];
}

export interface Asset {
  id: string;
  project_id: string;
  project_title: string;
  asset_type: "image" | "video" | "audio";
  provider_name: string;
  storage_url: string;
  file_size_bytes: number;
  mime_type: string;
  metadata_json: Record<string, unknown>;
  created_at: string | null;
}

export interface ProviderStatus {
  id: string;
  category: string;
  name: string;
  env: string[];
  free: string;
  signup?: string;
  configured: boolean;
  active: boolean;
}

export class ApiError extends Error {
  constructor(message: string, public status: number) {
    super(message);
  }
}

/** Generated media may be stored on the API server ("/media/...") or a CDN (absolute URL). */
export function mediaUrl(url?: string | null): string {
  if (!url) return "";
  return url.startsWith("/") ? `${API_BASE}${url}` : url;
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function getStoredUser(): User | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(USER_KEY);
    return raw ? (JSON.parse(raw) as User) : null;
  } catch {
    return null;
  }
}

export function saveSession(token: string, user: User) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  window.dispatchEvent(new Event("storyforge-auth"));
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  window.dispatchEvent(new Event("storyforge-auth"));
}

function errorMessage(data: unknown, status: number): string {
  const detail = (data as { detail?: unknown })?.detail;
  if (typeof detail === "string") return detail;
  // FastAPI validation errors: [{loc, msg}, ...]
  if (Array.isArray(detail) && detail.length) {
    return detail.map((d: { msg?: string }) => (d.msg || "").replace(/^Value error, /, "")).join(" ");
  }
  return `Request failed (HTTP ${status})`;
}

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(options.body && !(options.body instanceof FormData) ? { "Content-Type": "application/json" } : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...((options.headers as Record<string, string>) || {}),
  };

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
  } catch {
    throw new ApiError(
      "Can't reach the StoryForge server. If it was idle it may be waking up (free hosting) - try again in ~30 seconds.",
      0
    );
  }

  if (response.status === 401 && typeof window !== "undefined" && token) {
    clearSession();
  }
  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new ApiError(errorMessage(data, response.status), response.status);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

// Auth
export const loginUser = (payload: { email: string; password: string }) =>
  fetchApi<{ access_token: string; user: User }>("/api/v1/auth/login", { method: "POST", body: JSON.stringify(payload) });

export const signupUser = (payload: { email: string; password: string; full_name: string }) =>
  fetchApi<{ access_token: string; user: User }>("/api/v1/auth/signup", { method: "POST", body: JSON.stringify(payload) });

// Meta
export const getMeta = () => fetchApi<Meta>("/api/v1/meta");
export const getHealth = () => fetchApi<{ status: string; llm_providers: string[]; storage: string }>("/health");

// Projects
export const getProjects = () => fetchApi<{ projects: ProjectSummary[]; total_count: number }>("/api/v1/projects");
export const getProject = (id: string) => fetchApi<Project>(`/api/v1/projects/${id}`);

export const createProject = (payload: {
  title: string;
  topic: string;
  content_pack_name: string;
  aspect_ratio: string;
  notes: string;
  target_seconds: number;
  voice: string;
  language: string;
}) => fetchApi<Project>("/api/v1/projects", { method: "POST", body: JSON.stringify(payload) });

export const updateProject = (id: string, payload: Partial<{ title: string; topic: string; notes: string; voice: string; target_seconds: number }>) =>
  fetchApi<Project>(`/api/v1/projects/${id}`, { method: "PATCH", body: JSON.stringify(payload) });

export const saveScenes = (id: string, scenes: Pick<Scene, "heading" | "narration" | "visual_prompt" | "on_screen_text">[]) =>
  fetchApi<Project>(`/api/v1/projects/${id}/scenes`, { method: "PUT", body: JSON.stringify({ scenes }) });

export const startGeneration = (id: string, mode: "full" | "rerender", regenerate_images: number[] = []) =>
  fetchApi<Project>(`/api/v1/projects/${id}/generate`, { method: "POST", body: JSON.stringify({ mode, regenerate_images }) });

export const chatEdit = (id: string, message: string) =>
  fetchApi<{ reply: string; project: Project }>(`/api/v1/projects/${id}/chat`, { method: "POST", body: JSON.stringify({ message }) });

export const deleteProject = (id: string) => fetchApi<void>(`/api/v1/projects/${id}`, { method: "DELETE" });

// Assets & settings
export const getAssets = (type?: string) => fetchApi<{ assets: Asset[] }>(`/api/v1/assets${type ? `?asset_type=${type}` : ""}`);

export const getProviders = () =>
  fetchApi<{ providers: ProviderStatus[]; llm_order: string[]; storage: string; can_edit: boolean }>("/api/v1/settings/providers");

export const setProviderKey = (env: string, value: string) =>
  fetchApi<{ message: string }>("/api/v1/settings/keys", { method: "POST", body: JSON.stringify({ env, value }) });
