const API_BASE = import.meta.env.VITE_API_BASE || '/'

export function getToken(){ return localStorage.getItem('token') }
export function setToken(t){ localStorage.setItem('token', t); window.dispatchEvent(new Event('storage')) }
export function clearToken(){ localStorage.removeItem('token'); window.dispatchEvent(new Event('storage')) }

export async function api(path, opts = {}){
  const token = getToken()
  const headers = { 'Content-Type': 'application/json', ...(opts.headers||{}) }
  if(token) headers.Authorization = `Bearer ${token}`

  const url = `${API_BASE}api/v1${path}`
  const res = await fetch(url, { ...opts, headers })

  // 🔒 if unauthorized, bounce to login so we don't hang on "Loading…"
  if (res.status === 401) {
    clearToken()
    // if you're a SPA route, adjust this path to your login route if different
    window.location.assign('/login')
    throw new Error('Unauthorized')
  }

  // Optional: throw on other non-2xx to see the error upstream
  if (!res.ok) {
    const text = await res.text().catch(()=> '')
    const err = new Error(`HTTP ${res.status} on ${url}: ${text}`)
    err.status = res.status
    err.body = text
    throw err
  }

  return res
}
