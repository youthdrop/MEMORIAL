// frontend/src/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401) {
      sessionStorage.removeItem('token')
      // optional: window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api
export function setToken(t) { sessionStorage.setItem('token', t) }
export function clearToken() { sessionStorage.removeItem('token') }
export function getToken() { return sessionStorage.getItem('token') || '' }
