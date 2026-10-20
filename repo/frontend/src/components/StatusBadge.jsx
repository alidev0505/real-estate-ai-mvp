import { T } from '../services/i18n'
const CLS = { qualified: 'bg-pine-soft text-pine-dark', info_needed: 'bg-amberbg text-amber2', new: 'bg-skybg text-sky2' }
export default function StatusBadge({ status, large, lang = 'en' }) {
  const s = CLS[status] ? status : 'new'
  return <span className={`inline-flex items-center rounded-full font-semibold ${CLS[s]} ${large ? 'px-3.5 py-1.5 text-sm' : 'px-2.5 py-1 text-xs'}`}>{T[lang].status[s]}</span>
}
