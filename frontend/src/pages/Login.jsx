// src/pages/Login.jsx
import { useState } from 'react'
import { api, setToken as persistToken } from '../api'

export default function Login({ onLoggedIn }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  async function onSubmit(e){
    e.preventDefault()
    setError('')
    setBusy(true)
    try {
      // Frontend calls /api/v1/auth/login; backend aliases it to /api/login
      // frontend/src/pages/Login.jsx
        // frontend/src/pages/Login.jsx
        const res = await api('/login', {
          method: 'POST',
          body: JSON.stringify({ email, password })
        });


      if (!res.ok) {
        const t = await res.text().catch(()=> '')
        throw new Error(`Login failed (${res.status}) ${t}`)
      }
      const data = await res.json()
      const token = data.access_token || data.token
      if (!token) throw new Error('No token returned by server')

      // persist + notify App
      persistToken(token)
      onLoggedIn?.(token)
    } catch (err) {
      console.error('login error:', err)
      setError(err.message || 'Network error')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="min-h-[60vh] flex items-center justify-center px-4">
      <form onSubmit={onSubmit} className="w-full max-w-sm space-y-4 border rounded-2xl p-6 shadow-sm">
        <h1 className="text-xl font-semibold">Sign in</h1>

        {error && (
          <div className="text-sm text-red-700 bg-red-50 border border-red-200 rounded-lg p-2">
            {error}
          </div>
        )}

        <label className="block">
          <div className="mb-1 text-sm text-gray-600">Email</div>
          <input
            type="email"
            className="w-full border rounded-xl px-3 py-2"
            placeholder="you@example.org"
            value={email}
            onChange={e=>setEmail(e.target.value)}
            required
          />
        </label>

        <label className="block">
          <div className="mb-1 text-sm text-gray-600">Password</div>
          <input
            type="password"
            className="w-full border rounded-xl px-3 py-2"
            placeholder="••••••••"
            value={password}
            onChange={e=>setPassword(e.target.value)}
            required
          />
        </label>

        <button
          type="submit"
          disabled={busy}
          className="w-full rounded-2xl bg-black text-white py-2 disabled:opacity-60"
        >
          {busy ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </div>
  )
}
