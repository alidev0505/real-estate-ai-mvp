import { Check, Circle } from 'lucide-react'
import StatusBadge from './StatusBadge'
import { fmtAED } from '../services/api'
import { T } from '../services/i18n'

const FIELDS = [['property_type'], ['bedrooms'], ['area'], ['purpose'], ['budget', fmtAED], ['timeline']]

export default function LeadProfile({ profile = {}, status = 'new', lang = 'en' }) {
  const t = T[lang]
  const val = (k, v, fmt) => (k === 'bedrooms' && v === 0 ? t.studio : fmt ? fmt(v) : v)
  const done = FIELDS.filter(([k]) => profile[k] != null && profile[k] !== '').length
  return (
    <aside className="card p-5" aria-label={t.profile} dir={lang === 'ar' ? 'rtl' : 'ltr'}>
      <div className="flex items-center justify-between"><h2 className="font-display text-lg">{t.profile}</h2><span className="text-xs text-slate2">{done} {t.of} {FIELDS.length}</span></div>
      <div className="mt-3"><StatusBadge status={status} large lang={lang} /></div>
      <div className="mt-2 h-1 rounded bg-line" aria-hidden><div className="h-1 rounded bg-pine transition-all duration-500" style={{ width: `${(done / FIELDS.length) * 100}%` }} /></div>
      <dl className="mt-4 divide-y divide-line">
        {FIELDS.map(([k, fmt]) => {
          const v = profile[k]; const has = v != null && v !== ''
          return (
            <div key={k} className="flex items-center justify-between gap-3 py-2.5">
              <div><dt className="text-xs text-slate2">{t.fields[k]}</dt><dd className={`text-sm ${has ? 'font-semibold' : 'text-slate2/70'}`}>{has ? val(k, v, fmt) : t.notProvided}</dd></div>
              {has ? <Check size={16} className="shrink-0 text-pine" /> : <Circle size={14} className="shrink-0 text-line" />}
            </div>
          )
        })}
      </dl>
    </aside>
  )
}
