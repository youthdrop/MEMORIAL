// AddressAutocomplete.jsx (safe, no ".json" requests)
import { useState, useEffect } from 'react'
import api from '../api' // axios instance with auth

export default function AddressAutocomplete({ value, onChange }) {
  const [suggestions, setSuggestions] = useState([])
  const [q, setQ] = useState(value || '')

  useEffect(() => {
    const t = setTimeout(async () => {
      const term = q?.trim()
      if (!term) { setSuggestions([]); return }
      // ✅ call your backend, not `${term}.json`
      const { data } = await api.get(`/api/addresses`, { params: { q: term } })
      setSuggestions(data || [])
    }, 250)
    return () => clearTimeout(t)
  }, [q])

  return (
    <div className="relative">
      <input
        value={q}
        onChange={(e) => { setQ(e.target.value); onChange?.(e.target.value) }}
        placeholder="Start typing an address…"
      />
      {suggestions.length > 0 && (
        <ul className="absolute z-10 bg-white shadow rounded">
          {suggestions.map((s, i) => (
            <li key={i} onClick={() => { setQ(s.label); onChange?.(s.label) }}>
              {s.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
