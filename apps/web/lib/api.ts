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

// Projects API with LocalStorage sync fallback
export async function getProjects() {
  let localProjects: any[] = [];
  if (typeof window !== "undefined") {
    try {
      const stored = localStorage.getItem("storyforge_local_projects");
      if (stored) localProjects = JSON.parse(stored);
    } catch (e) {}
  }

  try {
    const data = await fetchApi<{ projects: any[]; total_count: number }>("/api/v1/projects");
    if (data && data.projects) {
      // Merge backend projects with local projects (avoid duplicates by ID)
      const backendIds = new Set(data.projects.map((p) => p.id));
      const uniqueLocal = localProjects.filter((p) => !backendIds.has(p.id));
      const combined = [...uniqueLocal, ...data.projects];
      return { projects: combined, total_count: combined.length };
    }
  } catch (e) {
    console.warn("Backend API offline/error, returning local projects:", e);
  }

  return { projects: localProjects, total_count: localProjects.length };
}

export async function createProject(payload: { title: string; topic: string; content_pack_name: string; aspect_ratio?: string }) {
  let newProject: any = null;
  try {
    newProject = await fetchApi<any>("/api/v1/projects", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  } catch (e) {
    console.warn("Failed to create project on backend, saving locally:", e);
    newProject = {
      id: `proj-${Math.random().toString(36).substring(2, 9)}`,
      title: payload.title,
      topic: payload.topic,
      content_pack_name: payload.content_pack_name,
      aspect_ratio: payload.aspect_ratio || "9:16",
      status: "draft",
      created_at: new Date().toISOString(),
    };
  }

  // Save to localStorage
  if (typeof window !== "undefined" && newProject) {
    try {
      const stored = localStorage.getItem("storyforge_local_projects");
      const existing = stored ? JSON.parse(stored) : [];
      localStorage.setItem("storyforge_local_projects", JSON.stringify([newProject, ...existing]));
    } catch (err) {}
  }

  return newProject;
}

export async function getProjectById(id: string) {
  try {
    const data = await fetchApi<any>(`/api/v1/projects/${id}`);
    if (data) return data;
  } catch (e) {
    console.warn(`Backend could not find project ${id}, checking localStorage:`, e);
  }

  if (typeof window !== "undefined") {
    try {
      const stored = localStorage.getItem("storyforge_local_projects");
      if (stored) {
        const existing: any[] = JSON.parse(stored);
        const match = existing.find((p) => p.id === id);
        if (match) return match;
      }
    } catch (err) {}
  }

  return null;
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
