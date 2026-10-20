import { useParams, Link } from 'react-router-dom'
import { ArrowLeft, Check, Clock, UserRound } from 'lucide-react'
import { api, fmtAED } from '../../services/api'
import useFetch from '../../hooks/useFetch'
import StatusBadge from '../../components/StatusBadge'
import PropertyCard from '../../components/PropertyCard'
import FollowUpDrafts from '../../components/FollowUpDrafts'

export default function LeadDetail() {
  const { id } = useParams()
  const lead = useFetch(() => api.lead(id), [id]); const convo = useFetch(() => api.conversation(id), [id])
  const matches = useFetch(() => api.matches(id), [id])
  const l = lead.data
  if (lead.error) return <p className="text-red-700">{lead.error}</p>
  if (!l) return <p className="text-slate2">Loading…</p>
  const req = [['Property', l.property_type], ['Bedrooms', l.bedrooms === 0 ? 'Studio' : l.bedrooms], ['Area', l.area], ['Purpose', l.purpose], ['Budget', l.budget && fmtAED(l.budget)], ['Timeline', l.timeline]]
  return (
    <div>
      <Link to="/dashboard/leads" className="mb-4 inline-flex items-center gap-1 text-sm text-slate2"><ArrowLeft size={14} />All leads</Link>
      <div className="flex flex-wrap items-center gap-3"><h1 className="font-display text-3xl">{l.name || `Lead #${l.id}`}</h1><StatusBadge status={l.status} large /></div>
      <div className="mt-6 grid gap-5 lg:grid-cols-3">
        <section className="card p-5"><h2 className="font-display text-lg">Contact</h2>
          <p className="mt-3 text-sm">Phone: {l.phone || 'Not provided'}</p><p className="text-sm">Email: {l.email || 'Not provided'}</p>
          {l.human_requested && <p className="mt-3 flex items-center gap-1.5 rounded-lg bg-amberbg px-3 py-2 text-sm font-medium text-amber2"><UserRound size={14} />Asked for a human agent</p>}</section>
        <section className="card p-5"><h2 className="font-display text-lg">Requirements</h2>
          <dl className="mt-3 space-y-1.5 text-sm">{req.map(([k, v]) => <div key={k} className="flex justify-between"><dt className="text-slate2">{k}</dt><dd className="font-semibold">{v ?? 'Not provided'}</dd></div>)}</dl></section>
        <section className="card p-5"><h2 className="font-display text-lg">Follow-up</h2>
          <p className="mt-3 text-sm">Status: <b>{l.follow_up.status}</b></p>
          <ul className="mt-3 space-y-2 text-sm">{l.follow_up.steps.map((s) => <li key={s.label} className="flex items-center gap-2">{s.done ? <Check size={15} className="text-pine" /> : <Clock size={15} className="text-slate2" />}{s.label}{!s.done && <span className="text-slate2">pending</span>}</li>)}</ul>
          <p className="mt-3 text-xs text-slate2">{l.follow_up.note}</p>
          {l.viewings.map((v) => <p key={v.id} className="mt-3 rounded-lg bg-pine-soft px-3 py-2 text-sm text-pine-dark">Viewing: {v.property_title}, {v.date} at {v.time}</p>)}</section>
      </div>
      <FollowUpDrafts leadId={l.id} phone={l.phone} email={l.email} />
      <h2 className="mt-8 font-display text-xl">Conversation</h2>
      <div className="card mt-3 space-y-3 p-5">
        {(convo.data || []).map((m) => (
          <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : ''}`}>
            <div className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm ${m.role === 'user' ? 'bg-pine text-white' : 'bg-mist'}`}>
              <p className={`mb-0.5 text-[11px] font-semibold ${m.role === 'user' ? 'text-white/70' : 'text-slate2'}`}>{m.role === 'user' ? 'Lead' : 'AI'} · {new Date(m.created_at + 'Z').toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })}</p>{m.message}</div>
          </div>))}
      </div>
      {matches.data?.matches?.length > 0 && l.status === 'qualified' && (<><h2 className="mt-8 font-display text-xl">Matching properties</h2>
        <div className="mt-3 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{matches.data.matches.map((p) => <PropertyCard key={p.id} property={p} />)}</div></>)}
    </div>
  )
}
