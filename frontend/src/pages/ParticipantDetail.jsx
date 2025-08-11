// src/pages/ParticipantDetail.jsx
import { useEffect, useState, useRef } from 'react'
import { api } from '../api'

const SERVICE_TYPES = ['group','one_on_one','counseling','telephone']
const REFERRAL_STATUSES = ['referred','contacted','accepted','declined','completed']

export default function ParticipantDetail({ pid }){
  const [p, setP] = useState(null)
  const [err, setErr] = useState('')
  const [loading, setLoading] = useState(false)

  const [noteText, setNoteText] = useState('')
  const [svc, setSvc] = useState({ service_type:'group', note:'' })
  const [notes, setNotes] = useState([])
  const [services, setServices] = useState([])
  const [employers, setEmployers] = useState([])
  const [providers, setProviders] = useState([])
  const [referrals, setReferrals] = useState([])
  const [refForm, setRefForm] = useState({ kind:'employer', org_id:'', status:'referred', note:'' })

  const [editing, setEditing] = useState(false)
  const [editForm, setEditForm] = useState({ first_name:'', last_name:'', dob:'', race:'', address:'', email:'', phone:'' })

  const mounted = useRef(true)
  useEffect(()=>{ mounted.current = true; return ()=>{ mounted.current = false } }, [])

  async function load(){
    if (pid === undefined || pid === null) return
    setErr('')
    setLoading(true)
    setP(null) // gate UI until the main record loads

    try {
      // 1) MUST succeed: participant record
      const a = await api(`/participants/${pid}`)
      if (!a.ok) throw new Error(`Failed to load participant (${a.status})`)
      const pj = await a.json()
      if (!mounted.current) return
      setP(pj)
      setEditForm(pj)

      // 2) Kick off the rest; failures here won't block the header
      Promise.allSettled([
        api(`/participants/${pid}/casenotes`).then(r=>r.ok ? r.json() : []).then(v=>mounted.current && setNotes(v || [])),
        api(`/participants/${pid}/services`).then(r=>r.ok ? r.json() : []).then(v=>mounted.current && setServices(v || [])),
        api(`/participants/${pid}/referrals`).then(r=>r.ok ? r.json() : []).then(v=>mounted.current && setReferrals(v || [])),
        api(`/employers`).then(r=>r.ok ? r.json() : []).then(v=>mounted.current && setEmployers(v || [])),
        api(`/providers`).then(r=>r.ok ? r.json() : []).then(v=>mounted.current && setProviders(v || [])),
      ]).catch(()=>{})
    } catch (e) {
      if (!mounted.current) return
      console.error('load participant failed:', e)
      setErr(e.message || 'Failed to load participant')
    } finally {
      if (mounted.current) setLoading(false)
    }
  }

  useEffect(()=>{ load() }, [pid])

  async function addCaseNote(){
    if(!noteText.trim()) return
    try {
      const r = await api(`/participants/${pid}/casenotes`, { method:'POST', body: JSON.stringify({ content: noteText }) })
      if (r.status === 201) { setNoteText(''); load() }
      else {
        const t = await r.text().catch(()=> '')
        alert(`Save note failed (${r.status}) ${t}`)
      }
    } catch (e) {
      alert(e.message || 'Save note failed')
    }
  }

  async function addService(){
    try {
      const r = await api(`/participants/${pid}/services`, { method:'POST', body: JSON.stringify(svc) })
      if (r.status === 201) { setSvc({ service_type:'group', note:'' }); load() }
      else {
        const t = await r.text().catch(()=> '')
        alert(`Save service failed (${r.status}) ${t}`)
      }
    } catch (e) {
      alert(e.message || 'Save service failed')
    }
  }

  async function addReferral(){
    if(!refForm.org_id) return
    try {
      const r = await api(`/participants/${pid}/referrals`, { method:'POST', body: JSON.stringify(refForm) })
      if (r.status === 201) { setRefForm({ kind:'employer', org_id:'', status:'referred', note:'' }); load() }
      else {
        const t = await r.text().catch(()=> '')
        alert(`Save referral failed (${r.status}) ${t}`)
      }
    } catch (e) {
      alert(e.message || 'Save referral failed')
    }
  }

  async function saveEdit(){
    if(!editForm.first_name?.trim() || !editForm.last_name?.trim()){
      alert('First and last name are required'); return
    }
    if(editForm.email && !/^\S+@\S+\.\S+$/.test(editForm.email)){
      alert('Invalid email'); return
    }
    try {
      // Try PATCH first (common for Flask APIs), then fallback to PUT once if 405
      let r = await api(`/participants/${pid}`, { method:'PATCH', body: JSON.stringify(editForm) })
      if (r.status === 405) {
        r = await api(`/participants/${pid}`, { method:'PUT', body: JSON.stringify(editForm) })
      }
      if (!r.ok) {
        const t = await r.text().catch(()=> '')
        throw new Error(`Update failed (${r.status}) ${t}`)
      }
      setEditing(false)
      load()
    } catch (e) {
      console.error('saveEdit failed:', e)
      alert(e.message || 'Update failed')
    }
  }

  if (err) {
    return (
      <div className="space-y-3">
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
          Failed to load participant: {err}
        </div>
        <button
          className="rounded-2xl border px-3 py-1.5"
          onClick={load}
        >
          Retry
        </button>
      </div>
    )
  }

  if (!p || loading) return <div>Loading…</div>

  return (
    <div className="space-y-6">
      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <div className="text-lg font-semibold">
            {p.first_name} {p.last_name}
          </div>
          {!editing ? (
            <button className="px-3 py-1.5 rounded-xl border" onClick={()=>setEditing(true)}>Edit</button>
          ) : (
            <div className="flex gap-2">
              <button className="px-3 py-1.5 rounded-xl border" onClick={()=>setEditing(false)}>Cancel</button>
              <button className="px-3 py-1.5 rounded-xl bg-black text-white" onClick={saveEdit}>Save</button>
            </div>
          )}
        </div>

        {!editing ? (
          <div className="text-sm text-gray-600 space-y-1">
            <div><b>DOB:</b> {p.dob || '—'}</div>
            <div><b>Race:</b> {p.race || '—'}</div>
            <div><b>Address:</b> {p.address || '—'}</div>
            <div><b>Email:</b> {p.email || '—'}</div>
            <div><b>Phone:</b> {p.phone || '—'}</div>
          </div>
        ) : (
          <div className="grid gap-2">
            <input className="border rounded-xl px-3 py-2" placeholder="First name" value={editForm.first_name||''} onChange={e=>setEditForm(f=>({...f, first_name:e.target.value}))}/>
            <input className="border rounded-xl px-3 py-2" placeholder="Last name" value={editForm.last_name||''} onChange={e=>setEditForm(f=>({...f, last_name:e.target.value}))}/>
            <input className="border rounded-xl px-3 py-2" type="date" value={editForm.dob||''} onChange={e=>setEditForm(f=>({...f, dob:e.target.value}))}/>
            <input className="border rounded-xl px-3 py-2" placeholder="Race" value={editForm.race||''} onChange={e=>setEditForm(f=>({...f, race:e.target.value}))}/>
            <input className="border rounded-xl px-3 py-2" placeholder="Address" value={editForm.address||''} onChange={e=>setEditForm(f=>({...f, address:e.target.value}))}/>
            <input className="border rounded-xl px-3 py-2" placeholder="Email" value={editForm.email||''} onChange={e=>setEditForm(f=>({...f, email:e.target.value}))}/>
            <input className="border rounded-xl px-3 py-2" placeholder="Phone" value={editForm.phone||''} onChange={e=>setEditForm(f=>({...f, phone:e.target.value}))}/>
          </div>
        )}
      </section>

      <section className="grid gap-6">
        <div>
          <h4 className="font-semibold mb-2">Case Notes</h4>
          <div className="space-y-2 mb-3 max-h-44 overflow-auto pr-1">
            {notes.length===0 && <div className="text-sm text-gray-500">No notes yet.</div>}
            {notes.map(n=>(
              <div key={n.id} className="border rounded-xl p-2">
                <div className="text-sm">{n.content}</div>
                {n.created_at && <div className="text-xs text-gray-500 mt-1">{new Date(n.created_at).toLocaleString()}</div>}
              </div>
            ))}
          </div>
          <textarea className="w-full border rounded-xl px-3 py-2 min-h-[90px]" placeholder="Add a case note…" value={noteText} onChange={e=>setNoteText(e.target.value)} />
          <div className="flex gap-2 mt-2">
            <button className="px-4 py-2 rounded-2xl bg-black text-white disabled:opacity-60" onClick={addCaseNote} disabled={!noteText.trim()}>Save Note</button>
            <button className="px-4 py-2 rounded-2xl border" onClick={()=>setNoteText('')}>Clear</button>
          </div>
        </div>

        <div>
          <h4 className="font-semibold mb-2">Services</h4>
          <div className="space-y-2 mb-3 max-h-44 overflow-auto pr-1">
            {services.length===0 && <div className="text-sm text-gray-500">No services yet.</div>}
            {services.map(s=>(
              <div key={s.id} className="border rounded-xl p-2 flex items-center justify-between">
                <div className="text-sm capitalize">{(s.service_type||'').replace('_',' ')}</div>
                {s.provided_at && <div className="text-xs text-gray-500">{new Date(s.provided_at).toLocaleString()}</div>}
              </div>
            ))}
          </div>
          <div className="grid gap-2">
            <select className="border rounded-xl px-3 py-2" value={svc.service_type} onChange={e=>setSvc(x=>({...x, service_type:e.target.value}))}>
              {SERVICE_TYPES.map(t => <option key={t} value={t}>{t.replace('_',' ')}</option>)}
            </select>
            <textarea className="border rounded-xl px-3 py-2 min-h-[60px]" placeholder="Note (optional)" value={svc.note} onChange={e=>setSvc(x=>({...x, note:e.target.value}))} />
            <div className="flex gap-2">
              <button className="px-4 py-2 rounded-2xl bg-black text-white" onClick={addService}>Save Service</button>
              <button className="px-4 py-2 rounded-2xl border" onClick={()=>setSvc({ service_type:'group', note:'' })}>Clear</button>
            </div>
          </div>
        </div>

        <div>
          <h4 className="font-semibold mb-2">Referrals</h4>
          <div className="space-y-2 mb-3 max-h-44 overflow-auto pr-1">
            {referrals.length===0 && <div className="text-sm text-gray-500">No referrals yet.</div>}
            {referrals.map(r=>(
              <div key={r.id} className="border rounded-xl p-2 flex items-center justify-between">
                <div className="text-sm">{r.kind}: {r.org_name} • {r.status}</div>
                <div className="text-xs text-gray-500">{r.referred_at && new Date(r.referred_at).toLocaleString()}</div>
              </div>
            ))}
          </div>
          <div className="grid gap-2">
            <select className="border rounded-xl px-3 py-2" value={refForm.kind} onChange={e=>setRefForm(x=>({...x, kind:e.target.value, org_id:''}))}>
              <option value="employer">employer</option>
              <option value="provider">provider</option>
            </select>
            {refForm.kind==='employer' ? (
              <select className="border rounded-xl px-3 py-2" value={refForm.org_id} onChange={e=>setRefForm(x=>({...x, org_id:Number(e.target.value)||''}))}>
                <option value="">Select employer…</option>
                {employers.map(o => <option key={o.id} value={o.id}>{o.name}</option>)}
              </select>
            ) : (
              <select className="border rounded-xl px-3 py-2" value={refForm.org_id} onChange={e=>setRefForm(x=>({...x, org_id:Number(e.target.value)||''}))}>
                <option value="">Select provider…</option>
                {providers.map(o => <option key={o.id} value={o.id}>{o.name}</option>)}
              </select>
            )}
            <select className="border rounded-xl px-3 py-2" value={refForm.status} onChange={e=>setRefForm(x=>({...x, status:e.target.value}))}>
              {REFERRAL_STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <textarea className="border rounded-xl px-3 py-2 min-h-[60px]" placeholder="Note (optional)" value={refForm.note} onChange={e=>setRefForm(x=>({...x, note:e.target.value}))}/>
            <button className="px-4 py-2 rounded-2xl bg-black text-white disabled:opacity-60" onClick={addReferral} disabled={!refForm.org_id}>Save Referral</button>
          </div>
        </div>
      </section>
    </div>
  )
}
