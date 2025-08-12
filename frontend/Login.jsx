// frontend/src/pages/Login.jsx
import { useState } from 'react'
import { api, setToken } from '../api'

export default function Login({ onLoggedIn }){
  const [email, setEmail] = useState('admin@stocktonmemorial.org')
  const [password, setPassword] = useState('ChangeMe123!')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function submit(e){
    e.preventDefault()
    setError('')
    setLoading(true)
    try{
      // backend route is /api/login, and api() adds the /api prefix for us
      const res = await api('/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      })

      if (!res.ok) {
        // try to surface backend message if present
        let msg = 'Invalid email or password'
        try {
          const j = await res.json()
          if (j?.error) msg = j.error
          if (j?.message) msg = j.message
        } catch (_) {}
        setError(msg)
        return
      }

      const data = await res.json()
      if (!data?.access_token) {
        setError('Login succeeded but no token returned')
        return
      }
      setToken(data.access_token)
      onLoggedIn(data.access_token)
    } catch (err) {
      setError('Network error. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-gray-100 to-gray-200 grid place-items-center">
      <div className="w-full max-w-md">
        <div className="mb-6 text-center">
          <div className="inline-flex items-center gap-2">
            <div className="h-9 w-9 rounded-2xl bg-black/90 grid place-items-center text-white text-sm font-bold">SM</div>
            <div className="text-xl font-semibold tracking-tight">Stockton/Memorial MIS</div>
          </div>
          <div className="mt-1 text-gray-500 text-sm">Secure staff sign-in</div>
        </div>

        <form onSubmit={submit} className="bg-white/70 backdrop-blur-md shadow-lg ring-1 ring-black/5 rounded-2xl p-6 space-y-4">
          <div>
            <label className="block text-sm text-gray-700 mb-1">Email</label>
            <input
              className="w-full rounded-xl border border-gray-300 px-3 py-2 focus:outline-none focus:ring-4 focus:ring-black/10"
              value={email}
              onChange={e=>setEmail(e.target.value)}
              autoComplete="username"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-700 mb-1">Password</label>
            <input
              type="password"
              className="w-full rounded-xl border border-gray-300 px-3 py-2 focus:outline-none focus:ring-4 focus:ring-black/10"
              value={password}
              onChange={e=>setPassword(e.target.value)}
              autoComplete="current-password"
            />
          </div>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl px-3 py-2">
              {error}
            </div>
          )}

          <button
            type="submit"
            className="w-full rounded-2xl px-4 py-2 font-medium bg-black text-white shadow hover:shadow-md transition disabled:opacity-60 disabled:cursor-not-allowed"
            disabled={loading}
          >
            {loading ? 'Signing in…' : 'Sign in'}
          </button>

          <div className="flex items-center justify-between text-xs text-gray-500 pt-1">
            <span>Admin & User accounts only</span>
            <span className="inline-flex items-center gap-1">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-500"></span>
              Online
            </span>
          </div>
        </form>

        <div className="mt-6 text-center text-xs text-gray-500">
          © {new Date().getFullYear()} Stockton/Memorial Drop-In Center
        </div>
      </div>
    </div>
  )
}
