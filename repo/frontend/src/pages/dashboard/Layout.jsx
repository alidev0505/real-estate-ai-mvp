import { NavLink, Outlet, Link, Navigate, useNavigate } from 'react-router-dom'
import { auth } from '../../services/api'
import { LayoutDashboard, Users, MessagesSquare, Building2, CalendarCheck, Settings, MessageCircle, LogOut } from 'lucide-react'

const NAV = [['/dashboard', 'Dashboard', LayoutDashboard, true], ['/dashboard/leads', 'Leads', Users], ['/dashboard/conversations', 'Conversations', MessagesSquare],
  ['/dashboard/properties', 'Properties', Building2], ['/dashboard/viewings', 'Viewings', CalendarCheck], ['/dashboard/settings', 'Settings', Settings]]

export default function Layout() {
  const nav = useNavigate()
  if (!auth.get()) return <Navigate to="/login" replace />
  return (
    <div className="min-h-screen md:grid md:grid-cols-[230px_1fr]">
      <aside className="border-b border-line bg-white p-4 md:min-h-screen md:border-b-0 md:border-r">
        <Link to="/" className="mb-4 block font-display text-lg md:mb-8">AI Real Estate</Link>
        <nav className="flex gap-1 overflow-x-auto md:flex-col" aria-label="Dashboard">
          {NAV.map(([to, label, Icon, end]) => (
            <NavLink key={to} to={to} end={end} className={({ isActive }) => `flex items-center gap-2.5 whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium ${isActive ? 'bg-pine-soft text-pine-dark' : 'text-slate2 hover:bg-mist'}`}>
              <Icon size={16} />{label}
            </NavLink>
          ))}
        </nav>
        <Link to="/chat" className="btn btn-ghost mt-6 hidden w-full md:flex"><MessageCircle size={15} />Open lead chat</Link>
        <button className="btn btn-ghost mt-2 hidden w-full md:flex" onClick={() => { auth.clear(); nav('/login') }}><LogOut size={15} />Sign out</button>
      </aside>
      <main className="p-5 md:p-8"><Outlet /></main>
    </div>
  )
}
