const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://storyforge-snc4.onrender.com";

function getAuthHeader(): Record<string, string> {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("storyforge_token");
    if (token) {
      return { Authorization: `Bearer ${token}` };
    }
  }
  return {};
}

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  const headers = {
    "Content-Type": "application/json",
    ...getAuthHeader(),
    ...(options.headers || {}),
  };

  const response = await fetch(url, { ...options, headers });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: "Network request failed" }));
    throw new Error(errorData.detail || `HTTP Error ${response.status}`);
  }

  return response.json();
}

// Projects API
export async function getProjects() {
  return fetchApi<{ projects: any[]; total_count: number }>("/api/v1/projects");
}

export async function createProject(payload: { title: string; topic: string; content_pack_name: string; aspect_ratio?: string }) {
  return fetchApi<any>("/api/v1/projects", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getProjectById(id: string) {
  return fetchApi<any>(`/api/v1/projects/${id}`);
}

// Auth API
export async function loginUser(payload: { email: string; password: string }) {
  return fetchApi<{ access_token: string; user: any }>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function signupUser(payload: { email: string; password: string; full_name: string }) {
  return fetchApi<{ access_token: string; user: any }>("/api/v1/auth/signup", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getMe() {
  return fetchApi<{ user: any }>("/api/v1/auth/me");
}

// Settings API
export async function getApiKeys() {
  return fetchApi<Record<string, string>>("/api/v1/settings/keys");
}

export async function updateApiKey(provider: string, api_key: string) {
  return fetchApi<any>("/api/v1/settings/keys", {
    method: "POST",
    body: JSON.stringify({ provider, api_key }),
  });
}

export async function getWorkspace() {
  return fetchApi<any>("/api/v1/settings/workspace");
}

// Runtime DAG API
export async function generatePlan(goal: string, content_pack: string = "history", aspect_ratio: string = "9:16") {
  return fetchApi<any>("/api/v1/runtime/plan", {
    method: "POST",
    body: JSON.stringify({ goal, content_pack, aspect_ratio }),
  });
}

export async function executeCapability(capability_name: string, kwargs: Record<string, any> = {}, run_in_background: boolean = false) {
  return fetchApi<any>("/api/v1/runtime/execute", {
    method: "POST",
    body: JSON.stringify({ capability_name, kwargs, run_in_background }),
  });
}
