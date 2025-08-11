const API_BASE = import.meta.env.VITE_API_BASE || '/'

export function getToken(){ 
  return localStorage.getItem('token') 
}

export function setToken(t){ 
  localStorage.setItem('token', t)
  window.dispatchEvent(new Event('storage'))
}

export function clearToken(){ 
  localStorage.removeItem('token')
  window.dispatchEvent(new Event('storage'))
}

export async function api(path, opts = {}){
  const token = getToken()
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) }
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(`${API_BASE}api/v1${path}`, { ...opts, headers })
  // auto sign-out on unauthorized OR invalid token (e.g., 422 from JWT "sub" type issues)
  if (res.status === 401 || res.status === 422) clearToken()
  return res
}
