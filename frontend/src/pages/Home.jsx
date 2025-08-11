import { useEffect, useState } from 'react'
import { api, clearToken } from '../api'
import AddressAutocomplete from '../components/AddressAutocomplete.jsx'
import Drawer from '../components/Drawer.jsx'
import ParticipantDetail from './ParticipantDetail.jsx'
import Reports from './Reports.jsx' // 👈 add this

const RACE_OPTIONS = [
  'American Indian or Alaska Native','Asian','Black or African American',
  'Native Hawaiian or Other Pacific Islander','White','Multiracial','Other','Prefer not to say'
]

const emptyP  = { first_name:'', last_name:'', dob:'', race:'', address:'', email:'', phone:'' }
const emptyE  = { name:'', contact_name:'', phone:'', email:'', address:'' }
const emptyPr = { name:'', contact_name:'', phone:'', email:'', address:'' }

export default function Home(){
  const [items, setItems] = useState([])
  const [showAddP, setShowAddP] = useState(false)
  const [pForm, setPForm] = useState(emptyP)

  const [showAddEmp, setShowAddEmp] = useState(false)
  const [eForm, setEForm] = useState(emptyE)

  const [showAddProv, setShowAddProv] = useState(false)
  const [prForm, setPrForm] = useState(emptyPr)

  const [selectedId, setSelectedId] = useState(null)
  const [selectedName, setSelectedName] = useState('')

  const [showReports, setShowReports] = useState(false) // 👈 add this

  async function load(){
    const r = await api('/participants')
    if(r.ok){ setItems(await r.json()) }
  }
  useEffect(()=>{ load() },[])

  async function createParticipant(){
    const r = await api('/participants', { method:'POST', body: JSON.stringify(pForm) })
    if(r.status === 201){ setShowAddP(false); setPForm(emptyP); load() }
    else alert(`${r.status} ${r.statusText}\n` + await r.text())
  }
  async function createEmployer(){
    const r = await api('/employers', { method:'POST', body: JSON.stringify(eForm) })
    if(r.status === 201){ setShowAddEmp(false); setEForm(emptyE); alert('Employer saved') }
    else alert(`${r.status} ${r.statusText}\n` + await r.text())
  }
  async function createProvider(){
    const r = await api('/providers', { method:'POST', body: JSON.stringify(prForm) })
    if(r.status === 201){ setShowAddProv(false); setPrForm(emptyPr); alert('Provider saved') }
    else alert(`${r.status} ${r.statusText}\n` + await r.text())
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="sticky top-0 z-10 bg-white border-b">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold">SMDROPIN MIS</h1>
          <div className="flex gap-2">
            <button className="px-4 py-2 rounded-2xl border" onClick={()=>setShowReports(true)}>Reports</button> {/* 👈 added */}
            <button className="px-4 py-2 rounded-2xl bg-black text-white" onClick={()=>setShowAddP(true)}>Add Participant</button>
            <button className="px-4 py-2 rounded-2xl border" onClick={()=>setShowAddEmp(true)}>Add Employer</button>
            <button className="px-4 py-2 rounded-2xl border" onClick={()=>setShowAddProv(true)}>Add Provider</button>
            <button className="px-4 py-2 rounded-2xl border" onClick={clearToken}>Sign out</button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6">
        <section className="bg-white rounded-2xl p-4 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">Participants</h2>
          </div>
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
                {items.map(p=>(
                  <tr key={p.id} className="border-b hover:bg-gray-50">
                    <td className="py-2">{p.name}</td>
                    <td className="py-2">{p.dob || '—'}</td>
                    <td className="py-2">{p.race || '—'}</td>
                    <td className="py-2 text-right">
                      <button className="px-3 py-1.5 rounded-xl border"
                        onClick={()=>{ setSelectedId(p.id); setSelectedName(p.name) }}>
                        View / Add Details
                      </button>
                    </td>
                  </tr>
                ))}
                {items.length===0 && (
                  <tr><td className="py-3 text-gray-500" colSpan={4}>No participants yet.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>
      </main>

      {/* Drawers */}
      <Drawer open={showAddP} title="Add Participant (Admin only)" onClose={()=>setShowAddP(false)}>
        <FormLabel label="First name"><input className="w-full border rounded-xl px-3 py-2" value={pForm.first_name} onChange={e=>setPForm(f=>({...f, first_name:e.target.value}))} /></FormLabel>
        <FormLabel label="Last name"><input className="w-full border rounded-xl px-3 py-2" value={pForm.last_name} onChange={e=>setPForm(f=>({...f, last_name:e.target.value}))} /></FormLabel>
        <FormLabel label="DOB"><input type="date" className="w-full border rounded-xl px-3 py-2" value={pForm.dob || ''} onChange={e=>setPForm(f=>({...f, dob:e.target.value}))} /></FormLabel>
        <FormLabel label="Race">
          <select className="w-full border rounded-xl px-3 py-2" value={pForm.race || ''} onChange={e=>setPForm(f=>({...f, race:e.target.value}))}>
            <option value="">Select race…</option>
            {RACE_OPTIONS.map(opt => <option key={opt} value={opt}>{opt}</option>)}
          </select>
        </FormLabel>
        <FormLabel label="Address"><AddressAutocomplete value={pForm.address || ''} onChange={v=>setPForm(f=>({...f, address:v}))} /></FormLabel>
        <FormLabel label="Email"><input className="w-full border rounded-xl px-3 py-2" value={pForm.email} onChange={e=>setPForm(f=>({...f, email:e.target.value}))} /></FormLabel>
        <FormLabel label="Telephone"><input className="w-full border rounded-xl px-3 py-2" value={pForm.phone} onChange={e=>setPForm(f=>({...f, phone:e.target.value}))} /></FormLabel>
        <div className="flex gap-2 pt-2">
          <button className="px-4 py-2 rounded-2xl bg-black text-white" onClick={createParticipant}>Save</button>
          <button className="px-4 py-2 rounded-2xl border" onClick={()=>setShowAddP(false)}>Cancel</button>
        </div>
      </Drawer>

      <Drawer open={showAddEmp} title="Add Employer (Admin only)" onClose={()=>setShowAddEmp(false)}>
        {['name','contact_name','phone','email','address'].map(k=>(
          <FormLabel key={k} label={k.replace('_',' ').replace(/\b\w/g,m=>m.toUpperCase())}>
            <input className="w-full border rounded-xl px-3 py-2" value={eForm[k]||''} onChange={e=>setEForm(f=>({...f,[k]:e.target.value}))} />
          </FormLabel>
        ))}
        <div className="flex gap-2 pt-2">
          <button className="px-4 py-2 rounded-2xl bg-black text-white" onClick={createEmployer}>Save</button>
          <button className="px-4 py-2 rounded-2xl border" onClick={()=>setShowAddEmp(false)}>Cancel</button>
        </div>
      </Drawer>

      <Drawer open={showAddProv} title="Add Provider (Admin only)" onClose={()=>setShowAddProv(false)}>
        {['name','contact_name','phone','email','address'].map(k=>(
          <FormLabel key={k} label={k.replace('_',' ').replace(/\b\w/g,m=>m.toUpperCase())}>
            <input className="w-full border rounded-xl px-3 py-2" value={prForm[k]||''} onChange={e=>setPrForm(f=>({...f,[k]:e.target.value}))} />
          </FormLabel>
        ))}
        <div className="flex gap-2 pt-2">
          <button className="px-4 py-2 rounded-2xl bg-black text-white" onClick={createProvider}>Save</button>
          <button className="px-4 py-2 rounded-2xl border" onClick={()=>setShowAddProv(false)}>Cancel</button>
        </div>
      </Drawer>

      <Drawer open={!!selectedId} title={selectedName ? `Participant: ${selectedName}` : 'Participant'} onClose={()=>setSelectedId(null)}>
        {selectedId && <ParticipantDetail pid={selectedId} />}
      </Drawer>

      {/* 👇 Reports Drawer */}
      <Drawer open={showReports} title="Reports" onClose={()=>setShowReports(false)}>
        <Reports />
      </Drawer>
    </div>
  )
}

function FormLabel({label, children}){
  return (
    <label className="text-sm text-gray-700">
      <div className="mb-1 text-gray-600">{label}</div>
      {children}
    </label>
  )
}
