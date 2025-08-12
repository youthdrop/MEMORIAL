import { useEffect, useState } from 'react'
import api from '../api'

export default function Reports(){
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')
  const [enroll, setEnroll] = useState([])
  const [svcs, setSvcs] = useState([])
  const [outs, setOuts] = useState([])
  const [refs, setRefs] = useState([])

  async function load(){
    const qs = (from||to) ? `?start=${from||''}&end=${to||''}` : ''
    const [a,b,c,d] = await Promise.all([
      api(`/reports/enrollments${qs}`),
      api(`/reports/services${qs}`),
      api(`/reports/outcomes`),
      api(`/reports/referrals`)
    ])
    if(a.ok) setEnroll(await a.json())
    if(b.ok) setSvcs(await b.json())
    if(c.ok) setOuts(await c.json())
    if(d.ok) setRefs(await d.json())
  }
  useEffect(()=>{ load() },[])

  return (
    <div className="space-y-6">
      <div className="flex gap-2">
        <input type="date" className="border rounded-xl px-3 py-2" value={from} onChange={e=>setFrom(e.target.value)} />
        <input type="date" className="border rounded-xl px-3 py-2" value={to} onChange={e=>setTo(e.target.value)} />
        <button className="px-4 py-2 rounded-2xl bg-black text-white" onClick={load}>Run</button>
      </div>

      <section>
        <h3 className="font-semibold mb-2">Participant Enrollments</h3>
        <div className="text-sm border rounded-xl overflow-hidden">
          <table className="w-full">
            <thead><tr className="bg-gray-50 text-left text-gray-600"><th className="p-2">Date</th><th className="p-2">Count</th></tr></thead>
            <tbody>{enroll.map((r,i)=>(<tr key={i} className="border-t"><td className="p-2">{r.date}</td><td className="p-2">{r.count}</td></tr>))}</tbody>
          </table>
        </div>
      </section>

      <section>
        <h3 className="font-semibold mb-2">Services by Type</h3>
        <div className="text-sm border rounded-xl overflow-hidden">
          <table className="w-full">
            <thead><tr className="bg-gray-50 text-left text-gray-600"><th className="p-2">Service</th><th className="p-2">Date</th><th className="p-2">Count</th></tr></thead>
            <tbody>{svcs.map((r,i)=>(<tr key={i} className="border-t"><td className="p-2">{r.service_type}</td><td className="p-2">{r.date}</td><td className="p-2">{r.count}</td></tr>))}</tbody>
          </table>
        </div>
      </section>

      <section>
        <h3 className="font-semibold mb-2">Outcomes (Employment/Education)</h3>
        <div className="text-sm border rounded-xl overflow-hidden">
          <table className="w-full">
            <thead><tr className="bg-gray-50 text-left text-gray-600"><th className="p-2">Kind</th><th className="p-2">Status</th><th className="p-2">Count</th></tr></thead>
            <tbody>{outs.map((r,i)=>(<tr key={i} className="border-t"><td className="p-2">{r.kind}</td><td className="p-2">{r.status}</td><td className="p-2">{r.count}</td></tr>))}</tbody>
          </table>
        </div>
      </section>

      <section>
        <h3 className="font-semibold mb-2">Referrals</h3>
        <div className="text-sm border rounded-xl overflow-hidden">
          <table className="w-full">
            <thead><tr className="bg-gray-50 text-left text-gray-600"><th className="p-2">Org</th><th className="p-2">Kind</th><th className="p-2">Status</th><th className="p-2">Count</th></tr></thead>
            <tbody>{refs.map((r,i)=>(<tr key={i} className="border-t"><td className="p-2">{r.org_name}</td><td className="p-2">{r.kind}</td><td className="p-2">{r.status}</td><td className="p-2">{r.count}</td></tr>))}</tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
