import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { LogIn } from 'lucide-react'
import { api, auth } from '../services/api'

export default function Login() {
  const nav = useNavigate()
  const [u, setU] = useState(''); const [p, setP] = useState(''); const [err, setErr] = useState(''); const [busy, setBusy] = useState(false)
  const submit = async (e) => {
    e.preventDefault(); setBusy(true); setErr('')
    try { const r = await api.login(u.trim(), p); auth.set(r.token); nav('/dashboard', { replace: true }) }
    catch (x) { setErr(x.message); setBusy(false) }
  }
  const field = 'mt-1 w-full rounded-lg border border-line bg-white px-3 py-2.5 text-sm outline-none focus:border-pine'
  return (
    <div className="grid min-h-screen place-items-center p-4">
      <form onSubmit={submit} className="card w-full max-w-sm p-7">
        <Link to="/" className="font-display text-lg">AI Real Estate</Link>
        <h1 className="mt-5 font-display text-2xl">Agent sign-in</h1>
        <p className="mt-1 text-sm text-slate2">Sign in to view leads, conversations and viewings.</p>
        <label className="mt-5 block text-sm font-medium">Username<input className={field} value={u} onChange={(e) => setU(e.target.value)} autoComplete="username" required autoFocus /></label>
        <label className="mt-4 block text-sm font-medium">Password<input className={field} type="password" value={p} onChange={(e) => setP(e.target.value)} autoComplete="current-password" required /></label>
        {err && <p className="mt-4 text-sm text-red-700" role="alert">{err}</p>}
        <button className="btn btn-primary mt-6 w-full" disabled={busy}><LogIn size={16} />{busy ? 'Signing in…' : 'Sign in'}</button>
      </form>
    </div>
  )
}
