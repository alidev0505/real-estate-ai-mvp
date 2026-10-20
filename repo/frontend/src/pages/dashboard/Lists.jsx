import { Link } from 'react-router-dom'
import { api } from '../../services/api'
import useFetch from '../../hooks/useFetch'
import StatusBadge from '../../components/StatusBadge'

const Title = ({ children, sub }) => <div className="mb-6"><h1 className="font-display text-3xl">{children}</h1>{sub && <p className="mt-1 text-sm text-slate2">{sub}</p>}</div>

export function Conversations() {
  const { data, error } = useFetch(api.leads)
  return (<div><Title>Conversations</Title>{error && <p className="text-red-700">{error}</p>}
    <div className="card divide-y divide-line">{(data || []).filter((l) => l.message_count > 0).map((l) => (
      <Link key={l.id} to={`/dashboard/leads/${l.id}`} className="flex items-center justify-between px-5 py-3.5 hover:bg-mist">
        <div><p className="font-semibold">{l.name || `Lead #${l.id}`}</p><p className="text-sm text-slate2">{l.message_count} messages · {l.follow_up_status}</p></div><StatusBadge status={l.status} /></Link>))}</div></div>)
}
export function Viewings() {
  const { data, error } = useFetch(api.viewings)
  return (<div><Title>Viewings</Title>{error && <p className="text-red-700">{error}</p>}
    <div className="card overflow-x-auto"><table className="w-full min-w-[560px] text-left text-sm"><thead className="border-b border-line text-slate2"><tr>{['Lead', 'Property', 'Date', 'Time', 'Status'].map((h) => <th key={h} className="px-5 py-3 font-medium">{h}</th>)}</tr></thead>
      <tbody className="divide-y divide-line">{(data || []).map((v) => <tr key={v.id}><td className="px-5 py-3.5 font-semibold"><Link to={`/dashboard/leads/${v.lead_id}`}>{v.lead_name}</Link></td><td className="px-5 py-3.5">{v.property_title}</td><td className="px-5 py-3.5">{v.date}</td><td className="px-5 py-3.5">{v.time}</td><td className="px-5 py-3.5 capitalize">{v.status}</td></tr>)}</tbody></table>
      {data?.length === 0 && <p className="p-5 text-sm text-slate2">No viewing requests yet.</p>}</div></div>)
}
export function Settings() {
  const { data, error } = useFetch(api.health)
  const rows = data && [['AI provider', data.provider], ['AI model', data.model || 'Not set'], ['AI key', data.ai_configured ? 'Configured' : 'Missing. Set AI_API_KEY and AI_MODEL in backend/.env'], ['Database', data.database]]
  return (<div><Title sub="Read-only. Configuration lives in backend/.env.">Settings</Title>{error && <p className="text-red-700">{error}</p>}
    <dl className="card divide-y divide-line">{(rows || []).map(([k, v]) => <div key={k} className="flex justify-between px-5 py-3.5 text-sm"><dt className="text-slate2">{k}</dt><dd className="font-semibold">{v}</dd></div>)}</dl></div>)
}
