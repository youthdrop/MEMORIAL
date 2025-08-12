// frontend/src/App.jsx
import { useEffect, useState } from 'react'
import Login from './pages/Login.jsx'
import Home from './pages/Home.jsx'
import { getToken } from './api.js'
import useIdleLogout from './hooks/useIdleLogout'

export default function App() {
  useIdleLogout(5 * 60 * 1000) // 5 minutes of inactivity
  const [token, setToken] = useState(getToken())

  useEffect(() => {
    const onStorage = () => setToken(getToken())
    window.addEventListener('storage', onStorage)
    return () => window.removeEventListener('storage', onStorage)
  }, [])

  if (!token) return <Login onLoggedIn={setToken} />
  return <Home />
}
