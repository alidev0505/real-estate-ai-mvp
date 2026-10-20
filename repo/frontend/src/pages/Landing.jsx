import { Link } from 'react-router-dom'
import { Zap, ListChecks, Building2, CalendarClock, LayoutDashboard } from 'lucide-react'

const FEATURES = [
  [Zap, 'Instant lead response', 'Every enquiry gets a reply in seconds, at any hour.'],
  [ListChecks, 'AI qualification', 'Type, area, purpose, budget and timeline, collected in conversation.'],
  [Building2, 'Property matching', 'Requirements are matched against your inventory automatically.'],
  [CalendarClock, 'Viewing scheduling', 'Qualified buyers book a slot without waiting for an agent.'],
  [LayoutDashboard, 'Agent dashboard', 'Every lead arrives with a structured profile and the full chat.'],
]
export default function Landing() {
  return (
    <div className="min-h-screen bg-white">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <span className="font-display text-lg">AI Real Estate</span>
        <span className="rounded-full bg-amberbg px-3 py-1 text-xs font-semibold text-amber2">Demo mode · fictional data</span>
      </header>
      <main className="mx-auto max-w-6xl px-6 pb-20 pt-12 md:pt-20">
        <h1 className="font-display text-5xl leading-[1.05] md:text-7xl max-w-3xl">Respond. Qualify. Match. Convert.</h1>
        <p className="mt-6 max-w-xl text-lg text-slate2">AI-powered lead response and qualification for Dubai real estate teams.</p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link to="/chat" className="btn btn-primary !px-6 !py-3">Try AI Assistant</Link>
          <Link to="/dashboard" className="btn btn-ghost !px-6 !py-3">View Dashboard</Link>
        </div>
        <div className="mt-20 grid gap-px overflow-hidden rounded-2xl border border-line bg-line sm:grid-cols-2 lg:grid-cols-5">
          {FEATURES.map(([Icon, t, d]) => (
            <div key={t} className="bg-white p-6">
              <Icon size={20} className="text-pine" />
              <h3 className="mt-4 font-semibold">{t}</h3>
              <p className="mt-1.5 text-sm text-slate2">{d}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
