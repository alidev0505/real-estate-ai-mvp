import { useState } from 'react'
import { X, CheckCircle2 } from 'lucide-react'
import { api } from '../services/api'
import { T } from '../services/i18n'

const SLOTS = ['11:00 AM', '2:00 PM', '5:00 PM']
const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

export default function ViewingModal({ property, leadId, onClose, onDone, lang = 'en' }) {
  const t = T[lang]; const loc = lang === 'ar' ? 'ar-AE' : 'en-GB'
  const days = Array.from({ length: 7 }, (_, i) => { const d = new Date(); d.setDate(d.getDate() + i + 1); return d })
  const [date, setDate] = useState(iso(days[2]))
  const [time, setTime] = useState(SLOTS[0])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const submit = async () => {
    setBusy(true); setError('')
    try { const v = await api.createViewing({ lead_id: leadId, property_id: property.id, date, time }); onDone(v) }
    catch (e) { setError(e.message); setBusy(false) }
  }
  const chip = (on) => `rounded-lg border px-3 py-2 text-sm font-medium ${on ? 'border-pine bg-pine-soft text-pine-dark' : 'border-line bg-white hover:bg-mist'}`
  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-ink/40 p-4" role="dialog" aria-modal="true" aria-label="Schedule viewing">
      <div className="card w-full max-w-md p-6" dir={lang === 'ar' ? 'rtl' : 'ltr'}>
        <div className="flex items-start justify-between">
          <div><h3 className="font-display text-xl">{t.scheduleTitle}</h3><p className="text-sm text-slate2">{property.title}, {property.area}</p></div>
          <button onClick={onClose} aria-label="Close" className="p-1 text-slate2"><X size={18} /></button>
        </div>
        <p className="mt-5 text-sm font-semibold">{t.date}</p>
        <div className="mt-2 grid grid-cols-4 gap-2">
          {days.map((d) => <button key={iso(d)} className={chip(date === iso(d))} onClick={() => setDate(iso(d))}>{d.toLocaleDateString(loc, { day: 'numeric', month: 'short' })}</button>)}
        </div>
        <p className="mt-5 text-sm font-semibold">{t.time}</p>
        <div className="mt-2 grid grid-cols-3 gap-2">{SLOTS.map((s) => <button key={s} className={chip(time === s)} onClick={() => setTime(s)}>{s}</button>)}</div>
        {error && <p className="mt-4 text-sm text-red-700">{error}</p>}
        <button className="btn btn-primary w-full mt-6" disabled={busy} onClick={submit}><CheckCircle2 size={16} />{busy ? t.submitting : t.request}</button>
      </div>
    </div>
  )
}
