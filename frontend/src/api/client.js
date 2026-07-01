const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? (import.meta.env.DEV ? "http://localhost:8000" : "");

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export async function createAnalysisTask(payload) {
  return request("/api/analysis-tasks", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function createWorkflowAnalysisTask(payload) {
  return request("/api/analysis-tasks/workflow", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getTask(taskId) {
  return request(`/api/analysis-tasks/${taskId}`);
}

export async function getTasks(params = {}) {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      searchParams.set(key, value);
    }
  });
  const query = searchParams.toString();
  return request(`/api/analysis-tasks${query ? `?${query}` : ""}`);
}

export async function getSteps(taskId) {
  return request(`/api/analysis-tasks/${taskId}/steps`);
}

export async function getToolCalls(taskId) {
  return request(`/api/analysis-tasks/${taskId}/tool-calls`);
}

export async function getReport(taskId) {
  return request(`/api/analysis-tasks/${taskId}/report`);
}

export async function getSystemCapabilities() {
  return request("/api/system/capabilities");
}

export async function runProviderDiagnostics(payload) {
  return request("/api/system/provider-diagnostics", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
