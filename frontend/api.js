// frontend/src/api.js
export function getToken() {
  return localStorage.getItem('token');
}
export function setToken(t) {
  localStorage.setItem('token', t);
}

// Always call the same origin as the page (works on Railway & locally)
export async function api(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers.Authorization = `Bearer ${token}`;

  // Ensure every call is under /api (backend serves SPA + API on same domain)
  const url = path.startsWith('/api') ? path : `/api${path}`;

  return fetch(url, { ...options, headers });
}
