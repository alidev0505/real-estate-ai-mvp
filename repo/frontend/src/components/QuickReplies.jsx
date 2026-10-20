import { useEffect, useState } from 'react'
import { Check } from 'lucide-react'
import { OPTIONS, T } from '../services/i18n'

// Tick-box answers for the next missing field. Ticking sends the answer immediately.
export default function QuickReplies({ field, lang, disabled, onPick }) {
  const [picked, setPicked] = useState(null)
  useEffect(() => { setPicked(null) }, [field])
  const opts = OPTIONS[field]
  if (!opts) return null
  const ar = lang === 'ar'
  return (
    <fieldset className="border-t border-line bg-white px-4 pb-3 pt-2.5" dir={ar ? 'rtl' : 'ltr'} disabled={disabled}>
      <legend className="sr-only">{T[lang].fields[field]}</legend>
      <p className="mb-2 text-xs text-slate2">{T[lang].pick}</p>
      <div className="flex flex-wrap gap-2">
        {opts.map((o, i) => {
          const on = picked === i
          return (
            <button key={o[0]} type="button" role="checkbox" aria-checked={on} disabled={disabled}
              onClick={() => { setPicked(i); onPick(ar ? (o[3] || o[1]) : (o[2] || o[0])) }}
              className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-sm font-medium transition-colors disabled:opacity-60 ${on ? 'border-pine bg-pine-soft text-pine-dark' : 'border-line bg-white hover:border-pine/50 hover:bg-mist'}`}>
              <span className={`grid h-4 w-4 place-items-center rounded border ${on ? 'border-pine bg-pine text-white' : 'border-slate2/50'}`}>{on && <Check size={12} strokeWidth={3} />}</span>
              {ar ? o[1] : o[0]}
            </button>
          )
        })}
      </div>
    </fieldset>
  )
}
