import { useEffect, useState } from 'react'
import api from '../api'
import Drawer from '../components/Drawer.jsx'
import ParticipantDetail from './ParticipantDetail.jsx'
import AddressAutocomplete from '../components/AddressAutocomplete.jsx'

const RACE_OPTIONS = [
  'American Indian or Alaska Native',
  'Asian',
  'Black or African American',
  'Native Hawaiian or Other Pacific Islander',
  'White',
  'Multiracial',
  'Other',
  'Prefer not to say',
]

const EMPTY_FORM = {
  first_name: '',
  last_name: '',
  dob: '',
  race: '',
  address: '',
  email: '',
  phone: '',
}

export default function ParticipantList({ showAdd, setShowAdd }){
  const [items, setItems] = useState([])
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  const [selectedId, setSelectedId] = useState(null)
  const [selectedName, setSelectedName] = useState('')

  async function load(){
    setError('')
    const res = await api('/participants')
    if(res.ok){
      setItems(await res.json())
    } else {
      setError(`Failed to load participants: ${res.status} ${res.statusText}`)
    }
  }
  useEffect(()=>{ load() },[])

  async function create(e){
    e?.preventDefault?.()
    setSaving(true)
    setError('')
    try{
      const res = await api('/participants', {
        method:'POST',
        body: JSON.stringify(form),
      })
      if(res.status === 201){
        setShowAdd(false)
        setForm(EMPTY_FORM)
        load()
      } else {
        const txt = await res.text()
        setError(txt || 'Save failed (admin only?)')
      }
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b">
              <th className="py-2">Name</th>
              <th className="py-2">DOB</th>
              <th className="py-2">Race</th>
              <th className="py-2 text-right">Actions</th>
            </tr>
          </thead>

          <tbody>
            {items.map(p => (
              <tr key={p.id} className="border-b hover:bg-gray-50">
                <td className="py-2">{p.name}</td>
                <td className="py-2">{p.dob || '—'}</td>
                <td className="py-2">{p.race || '—'}</td>
                <td className="py-2 text-right">
                  <button
                    className="px-3 py-1.5 rounded-xl border"
                    onClick={()=>{ setSelectedId(p.id); setSelectedName(p.name) }}
                  >
                    View / Add Details
                  </button>
                </td>
              </tr>
            ))}
            {items.length===0 && (
              <tr>
                <td className="py-3 text-gray-500" colSpan={4}>No participants yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Add Participant Drawer */}
      <Drawer
        open={!!showAdd}
        onClose={()=> setShowAdd(false)}
        title="Add Participant (Admin only)"
      >
        <form onSubmit={create} className="grid gap-3">
          <label className="text-sm">
            <div className="mb-1 text-gray-600">First name</div>
            <input
              className="w-full border rounded-xl px-3 py-2"
              value={form.first_name}
              onChange={e=>setForm(f=>({...f, first_name: e.target.value}))}
              required
            />
          </label>

          <label className="text-sm">
            <div className="mb-1 text-gray-600">Last name</div>
            <input
              className="w-full border rounded-xl px-3 py-2"
              value={form.last_name}
              onChange={e=>setForm(f=>({...f, last_name: e.target.value}))}
              required
            />
          </label>

          <label className="text-sm">
            <div className="mb-1 text-gray-600">DOB</div>
            <input
              type="date"
              className="w-full border rounded-xl px-3 py-2"
              value={form.dob || ''}
              onChange={e=>setForm(f=>({...f, dob: e.target.value}))}
            />
          </label>

          <label className="text-sm">
            <div className="mb-1 text-gray-600">Race</div>
            <select
              className="w-full border rounded-xl px-3 py-2"
              value={form.race || ''}
              onChange={e=>setForm(f=>({...f, race: e.target.value}))}
            >
              <option value="">Select race…</option>
              {RACE_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
            </select>
          </label>

          <label className="text-sm">
            <div className="mb-1 text-gray-600">Address</div>
            <AddressAutocomplete
              value={form.address || ''}
              onChange={v=>setForm(f=>({...f, address: v}))}
            />
          </label>

          <label className="text-sm">
            <div className="mb-1 text-gray-600">Email</div>
            <input
              type="email"
              className="w-full border rounded-xl px-3 py-2"
              value={form.email}
              onChange={e=>setForm(f=>({...f, email: e.target.value}))}
            />
          </label>

          <label className="text-sm">
            <div className="mb-1 text-gray-600">Telephone</div>
            <input
              className="w-full border rounded-xl px-3 py-2"
              value={form.phone}
              onChange={e=>setForm(f=>({...f, phone: e.target.value}))}
            />
          </label>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl px-3 py-2">
              {error}
            </div>
          )}

          <div className="flex gap-2 pt-1">
            <button
              type="submit"
              className="px-4 py-2 rounded-2xl bg-black text-white disabled:opacity-60"
              disabled={saving}
            >
              {saving ? 'Saving…' : 'Save'}
            </button>
            <button
              type="button"
              className="px-4 py-2 rounded-2xl border"
              onClick={()=> setShowAdd(false)}
            >
              Cancel
            </button>
          </div>
        </form>
      </Drawer>

      {/* Participant Details Drawer */}
      <Drawer
        open={!!selectedId}
        onClose={()=> setSelectedId(null)}
        title={selectedName ? `Participant: ${selectedName}` : 'Participant'}
      >
        {selectedId && <ParticipantDetail pid={selectedId} />}
      </Drawer>
    </div>
  )
}
