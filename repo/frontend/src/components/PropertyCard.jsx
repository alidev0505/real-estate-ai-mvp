import { useState } from 'react'
import { Bed, Bath, MapPin, CalendarCheck, Info } from 'lucide-react'
import PropertyArt from './PropertyArt'
import { fmtAED, typeLabel } from '../services/api'
import { T } from '../services/i18n'

export default function PropertyCard({ property: p, onDetails, onSchedule, lang = 'en' }) {
  const t = T[lang]
  const [open, setOpen] = useState(false)
  return (
    <article dir={lang === 'ar' ? 'rtl' : 'ltr'} className="card overflow-hidden flex flex-col">
      <div className="relative h-36 bg-mist">
        {p.image_url ? <img src={p.image_url} alt={p.title} className="h-full w-full object-cover" /> : <PropertyArt property={p} className="h-full w-full" />}
        <span className="absolute left-2 top-2 rounded-full bg-white/90 px-2 py-0.5 text-[11px] font-semibold text-slate2">{t.demoListing}</span>
      </div>
      <div className="p-4 flex-1 flex flex-col">
        <h4 className="font-display text-lg leading-tight">{p.title}</h4>
        <p className="mt-1 text-sm text-slate2">{typeLabel(p)}</p>
        <p className="text-sm text-slate2 flex items-center gap-1"><MapPin size={13} />{p.area}</p>
        <p className="mt-3 text-lg font-bold">{fmtAED(p.price)}</p>
        <p className="mt-1 text-sm text-slate2 flex items-center gap-3">
          <span className="flex items-center gap-1"><Bed size={14} />{p.bedrooms === 0 ? t.studio : `${p.bedrooms} ${t.beds}`}</span>
          <span className="flex items-center gap-1"><Bath size={14} />{p.bathrooms} {t.baths}</span>
        </p>
        {open && <p className="mt-3 text-sm text-slate2 border-t border-line pt-3">{p.description} <span className="block mt-1 text-xs">{t.demoNotVerified}</span></p>}
        {(onDetails || onSchedule) && (
          <div className="mt-4 flex gap-2">
            <button className="btn btn-ghost flex-1 !px-2" onClick={() => { setOpen(!open); if (!open) onDetails?.(p) }}><Info size={15} />{t.details}</button>
            <button className="btn btn-primary flex-1 !px-2" onClick={() => onSchedule?.(p)}><CalendarCheck size={15} />{t.schedule}</button>
          </div>
        )}
      </div>
    </article>
  )
}
