// frontend/src/components/AddressAutocomplete.jsx
import { useState, useEffect } from 'react'
import api from '../api' // ✅ default import

export default function AddressAutocomplete({ value, onChange }) {
  const [suggestions, setSuggestions] = useState([])
  const [q, setQ] = useState(value || '')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const t = setTimeout(async () => {
      const term = (q || '').trim()
      if (!term) { setSuggestions([]); return }

      try {
        setLoading(true)
        // Absolute path so it works in prod regardless of baseURL
        const { data } = await api.get('/api/addresses', { params: { q: term } })
        setSuggestions(Array.isArray(data) ? data : [])
      } catch (e) {
        // swallow errors; autocomplete should be best-effort
        setSuggestions([])
        console.warn('address lookup failed', e?.response?.data || e.message)
      } finally {
        setLoading(false)
      }
    }, 250)

    return () => clearTimeout(t)
  }, [q])

  return (
    <div className="relative">
      <input
        value={q}
        onChange={(e) => { const v = e.target.value; setQ(v); onChange?.(v) }}
        placeholder="Start typing an address…"
        className="w-full border rounded-xl px-3 py-2"
        autoComplete="off"
      />
      {loading && <div className="absolute right-3 top-2 text-xs text-gray-500">…</div>}
      {suggestions.length > 0 && (
        <ul className="absolute z-10 bg-white shadow rounded w-full mt-1 max-h-52 overflow-auto">
          {suggestions.map((s, i) => (
            <li
              key={i}
              className="px-3 py-2 hover:bg-gray-100 cursor-pointer"
              onClick={() => { setQ(s.label); onChange?.(s.label); setSuggestions([]) }}
            >
              {s.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
