// frontend/src/api.js
const API_ORIGIN = import.meta.env.VITE_API_URL || window.location.origin; // prod uses same origin
const API_PREFIX = '/api'; // all backend routes are mounted here

export async function api(path, options = {}) {
  const token = localStorage.getItem('token');
  return fetch(`${API_ORIGIN}${API_PREFIX}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers
    },
    credentials: 'same-origin',
    ...options
  });
}

export function setToken(token) {
  localStorage.setItem('token', token);
}

export function getToken() {
  return localStorage.getItem('token');
}

export function clearToken() {
  localStorage.removeItem('token');
}
