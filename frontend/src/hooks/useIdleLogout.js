// frontend/src/hooks/useIdleLogout.js
import { useEffect, useRef } from 'react'
import { clearToken } from '../api'

export default function useIdleLogout(timeoutMs = 5 * 60 * 1000) {
  const timerRef = useRef(null)

  useEffect(() => {
    const reset = () => {
      if (timerRef.current) clearTimeout(timerRef.current)
      timerRef.current = setTimeout(() => {
        // clear token and refresh to bounce to Login
        clearToken()
        if (typeof window !== 'undefined') window.location.reload()
      }, timeoutMs)
    }

    // user activity that resets the timer
    const events = ['mousemove', 'keydown', 'wheel', 'touchstart', 'visibilitychange']
    events.forEach((e) => window.addEventListener(e, reset, { passive: true }))
    reset()

    // when tab/window closes
    const beforeUnload = () => { try { sessionStorage.removeItem('token') } catch {} }
    window.addEventListener('beforeunload', beforeUnload)

    return () => {
      events.forEach((e) => window.removeEventListener(e, reset))
      window.removeEventListener('beforeunload', beforeUnload)
      if (timerRef.current) clearTimeout(timerRef.current)
    }
  }, [timeoutMs])
}
