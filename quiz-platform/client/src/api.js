const API = "/api";

function headers() {
  const token = localStorage.getItem("token");
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function api(path, options = {}) {
  const res = await fetch(`${API}${path}`, { ...options, headers: { ...headers(), ...options.headers } });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Ошибка запроса");
  return data;
}

export const auth = {
  register: (body) => api("/auth/register", { method: "POST", body: JSON.stringify(body) }),
  login: (body) => api("/auth/login", { method: "POST", body: JSON.stringify(body) }),
};

export const quizzes = {
  list: () => api("/quizzes"),
  create: (body) => api("/quizzes", { method: "POST", body: JSON.stringify(body) }),
  get: (id) => api(`/quizzes/${id}`),
  addQuestion: (id, body) => api(`/quizzes/${id}/questions`, { method: "POST", body: JSON.stringify(body) }),
};

export const sessions = {
  create: (quizId) => api("/sessions", { method: "POST", body: JSON.stringify({ quizId }) }),
  get: (id) => api(`/sessions/${id}`),
  join: (roomCode) => api("/sessions/join", { method: "POST", body: JSON.stringify({ roomCode }) }),
  leaderboard: (id) => api(`/sessions/${id}/leaderboard`),
  history: () => api("/sessions/history/me"),
};
