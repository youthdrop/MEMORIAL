// frontend/src/api.js
import axios from 'axios'

// In prod, always same-origin. In dev, allow VITE_API_BASE (e.g. http://localhost:8080)
const isProd = import.meta.env.PROD
const envBase = (import.meta.env.VITE_API_BASE || '').trim()
const baseURL = isProd ? '' : envBase || ''

const api = axios.create({
  baseURL,
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
      // Kick to login on unauthorized
      if (typeof window !== 'undefined') window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default api

export function setToken(t) {
  sessionStorage.setItem('token', t)
}

export function clearToken() {
  sessionStorage.removeItem('token')
  if (typeof window !== 'undefined') window.location.href = '/login'
}

export function getToken() {
  return sessionStorage.getItem('token') || ''
}
