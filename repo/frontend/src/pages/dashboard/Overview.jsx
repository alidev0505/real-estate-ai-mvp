import { Link } from 'react-router-dom'
import { api, fmtShort } from '../../services/api'
import useFetch from '../../hooks/useFetch'
import StatusBadge from '../../components/StatusBadge'

export default function Overview() {
  const s = useFetch(api.stats); const l = useFetch(api.leads)
  const cards = s.data ? [['Total leads', s.data.total_leads], ['New leads', s.data.new_leads], ['Qualified leads', s.data.qualified_leads], ['Viewings', s.data.viewings]] : []
  return (
    <div>
      <h1 className="font-display text-3xl">Dashboard</h1>
      <p className="mt-1 text-sm text-slate2">Live counts from the database. Includes seeded demo leads.</p>
      {s.error && <p className="mt-4 text-sm text-red-700">{s.error}</p>}
      <div className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        {cards.map(([k, v]) => <div key={k} className="card p-5"><p className="text-sm text-slate2">{k}</p><p className="mt-1 font-display text-4xl">{v}</p></div>)}
      </div>
      <h2 className="mt-10 font-display text-xl">Latest leads</h2>
      <div className="card mt-3 divide-y divide-line">
        {(l.data || []).slice(0, 5).map((x) => (
          <Link key={x.id} to={`/dashboard/leads/${x.id}`} className="flex items-center justify-between gap-3 px-5 py-3.5 hover:bg-mist">
            <div><p className="font-semibold">{x.name || `Lead #${x.id}`}</p><p className="text-sm text-slate2">{x.area || 'Area not provided'} · {fmtShort(x.budget)}</p></div>
            <StatusBadge status={x.status} />
          </Link>
        ))}
        {l.data?.length === 0 && <p className="p-5 text-sm text-slate2">No leads yet. Start a chat to create one.</p>}
      </div>
    </div>
  )
}
