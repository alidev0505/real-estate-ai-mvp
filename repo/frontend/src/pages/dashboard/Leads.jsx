import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Download } from 'lucide-react'
import { api, fmtShort } from '../../services/api'
import useFetch from '../../hooks/useFetch'
import StatusBadge from '../../components/StatusBadge'

export default function Leads() {
  const { data, error, loading } = useFetch(api.leads); const nav = useNavigate()
  const [exErr, setExErr] = useState('')
  const exp = () => api.exportLeads().then(() => setExErr('')).catch((e) => setExErr(e.message))
  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3"><h1 className="font-display text-3xl">Leads</h1>
        <button className="btn btn-ghost" onClick={exp}><Download size={15} />Export CSV</button></div>
      {exErr && <p className="mt-3 text-sm text-red-700">{exErr}</p>}
      {error && <p className="mt-4 text-sm text-red-700">{error}</p>}
      <div className="card mt-6 overflow-x-auto">
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead className="border-b border-line text-slate2"><tr>{['Name', 'Property', 'Area', 'Budget', 'Status', 'Follow-up'].map((h) => <th key={h} className="px-5 py-3 font-medium">{h}</th>)}</tr></thead>
          <tbody className="divide-y divide-line">
            {(data || []).map((l) => (
              <tr key={l.id} tabIndex={0} onKeyDown={(e) => e.key === 'Enter' && nav(`/dashboard/leads/${l.id}`)} onClick={() => nav(`/dashboard/leads/${l.id}`)} className="cursor-pointer hover:bg-mist">
                <td className="px-5 py-3.5 font-semibold">{l.name || `Lead #${l.id}`}{l.is_demo && <span className="ml-2 text-[11px] font-medium text-slate2">demo</span>}</td>
                <td className="px-5 py-3.5">{l.property_type ? `${l.bedrooms != null ? (l.bedrooms === 0 ? 'Studio ' : l.bedrooms + 'BR ') : ''}${l.property_type}` : '—'}</td>
                <td className="px-5 py-3.5">{l.area || '—'}</td><td className="px-5 py-3.5">{fmtShort(l.budget)}</td>
                <td className="px-5 py-3.5"><StatusBadge status={l.status} /></td><td className="px-5 py-3.5 text-slate2">{l.follow_up_status}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {loading && <p className="p-5 text-sm text-slate2">Loading leads…</p>}
        {data?.length === 0 && <p className="p-5 text-sm text-slate2">No leads yet.</p>}
      </div>
    </div>
  )
}
