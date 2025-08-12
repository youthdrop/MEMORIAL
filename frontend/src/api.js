// frontend/src/api.js
import axios from 'axios'

// Detect environment & set base URL
const isProd = import.meta.env.PROD
let baseURL = ''

if (isProd) {
  // Production: always hit same origin /api
  baseURL = '/api'
} else {
  // Development: use .env VITE_API_BASE (example: http://localhost:8080/api)
  baseURL = import.meta.env.VITE_API_BASE?.trim() || 'http://localhost:8080/api'
}

const api = axios.create({
  baseURL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// Attach token on every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Handle unauthorized responses
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401) {
      localStorage.removeItem('token')
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(err)
  }
)

export default api
export const setToken = (t) => localStorage.setItem('token', t)
export const clearToken = () => localStorage.removeItem('token')
export const getToken = () => localStorage.getItem('token') || ''
