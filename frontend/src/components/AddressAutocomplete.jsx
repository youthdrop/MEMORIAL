import { useEffect, useRef, useState } from 'react'

export default function AddressAutocomplete({ value, onChange, placeholder='Start typing an address…' }){
  const token = import.meta.env.VITE_MAPBOX_TOKEN
  const [q, setQ] = useState(value || '')
  const [items, setItems] = useState([])
  const [open, setOpen] = useState(false)
  const timer = useRef(null)

  useEffect(()=>{ setQ(value || '') }, [value])

  useEffect(()=>{
    if(!token){ setItems([]); setOpen(false); return }
    if(timer.current) clearTimeout(timer.current)
    if(!q){ setItems([]); return }
    timer.current = setTimeout(async ()=>{
      try{
        const url = new URL(`https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(q)}.json`)
        url.searchParams.set('access_token', token)
        url.searchParams.set('autocomplete', 'true')
        url.searchParams.set('limit', '5')
        const r = await fetch(url.toString())
        if(!r.ok) return
        const j = await r.json()
        setItems((j.features || []).map(f => f.place_name))
        setOpen(true)
      } catch {}
    }, 250)
    return () => { if(timer.current) clearTimeout(timer.current) }
  }, [q, token])

  if(!token){
    return (
      <input
        className="w-full border rounded-xl px-3 py-2"
        value={value || ''}
        onChange={e=>onChange?.(e.target.value)}
        placeholder={placeholder}
      />
    )
  }

  return (
    <div className="relative">
      <input
        className="w-full border rounded-xl px-3 py-2"
        value={q}
        onChange={e=>setQ(e.target.value)}
        onFocus={()=> items.length && setOpen(true)}
        placeholder={placeholder}
      />
      {open && items.length > 0 && (
        <div className="absolute z-10 mt-1 w-full bg-white border rounded-xl shadow">
          {items.map((s, i)=>(
            <button key={`${s}-${i}`} type="button" className="block w-full text-left px-3 py-2 hover:bg-gray-50"
              onClick={()=>{ onChange?.(s); setQ(s); setOpen(false) }}>
              {s}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
