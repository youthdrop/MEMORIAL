// frontend/src/api.js
import axios from 'axios'

const isProd = import.meta.env.PROD
const envBase = (import.meta.env.VITE_API_BASE || '').trim()
// In prod (Railway) use same-origin; in dev default to localhost if not set
const baseURL = isProd ? '' : envBase || 'http://localhost:8080/api'

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

export default api
export const setToken = (t) => sessionStorage.setItem('token', t)
export const getToken = () => sessionStorage.getItem('token') || ''
export const clearToken = () => sessionStorage.removeItem('token')
