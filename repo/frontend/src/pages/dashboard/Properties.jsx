import { useEffect, useState } from 'react'
import { Plus, Pencil, Trash2, X, EyeOff, Eye } from 'lucide-react'
import { api } from '../../services/api'
import PropertyCard from '../../components/PropertyCard'

const TYPES = ['Apartment', 'Villa', 'Townhouse', 'Penthouse']
const AREAS = ['Dubai Marina', 'Downtown Dubai', 'Business Bay', 'Jumeirah', 'Palm Jumeirah', 'Arabian Ranches', 'Dubai Hills', 'JVC']
const EMPTY = { title: '', property_type: 'Apartment', bedrooms: 1, bathrooms: 1, area: 'Dubai Marina', price: '', description: '', image_url: '', available: true }

function Form({ initial, onClose, onSaved }) {
  const [f, setF] = useState({ ...EMPTY, ...initial, image_url: initial?.image_url || '', description: initial?.description || '' })
  const [err, setErr] = useState(''); const [busy, setBusy] = useState(false)
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value })
  const save = async (e) => {
    e.preventDefault(); setBusy(true); setErr('')
    const body = { ...f, bedrooms: Number(f.bedrooms), bathrooms: Number(f.bathrooms), price: Number(f.price) }
    try { initial?.id ? await api.editProperty(initial.id, body) : await api.addProperty(body); onSaved() }
    catch (x) { setErr(x.message); setBusy(false) }
  }
  const inp = 'mt-1 w-full rounded-lg border border-line bg-white px-3 py-2 text-sm outline-none focus:border-pine'
  return (
    <div className="fixed inset-0 z-50 grid place-items-center overflow-y-auto bg-ink/40 p-4" role="dialog" aria-modal="true">
      <form onSubmit={save} className="card w-full max-w-lg p-6">
        <div className="flex items-center justify-between"><h2 className="font-display text-xl">{initial?.id ? 'Edit property' : 'Add property'}</h2><button type="button" onClick={onClose} aria-label="Close"><X size={18} /></button></div>
        <div className="mt-4 grid grid-cols-2 gap-3 text-sm font-medium">
          <label className="col-span-2">Title<input className={inp} value={f.title} onChange={set('title')} required maxLength={120} /></label>
          <label>Type<select className={inp} value={f.property_type} onChange={set('property_type')}>{TYPES.map((t) => <option key={t}>{t}</option>)}</select></label>
          <label>Area<input className={inp} list="areas" value={f.area} onChange={set('area')} required /><datalist id="areas">{AREAS.map((a) => <option key={a} value={a} />)}</datalist></label>
          <label>Bedrooms (0 = studio)<input className={inp} type="number" min="0" max="12" value={f.bedrooms} onChange={set('bedrooms')} required /></label>
          <label>Bathrooms<input className={inp} type="number" min="0" max="12" value={f.bathrooms} onChange={set('bathrooms')} required /></label>
          <label className="col-span-2">Price (AED)<input className={inp} type="number" min="50000" step="1000" value={f.price} onChange={set('price')} required /></label>
          <label className="col-span-2">Image URL (optional)<input className={inp} type="url" value={f.image_url} onChange={set('image_url')} placeholder="https://…" /></label>
          <label className="col-span-2">Description<textarea className={inp} rows={3} maxLength={1000} value={f.description} onChange={set('description')} /></label>
        </div>
        {err && <p className="mt-3 text-sm text-red-700" role="alert">{err}</p>}
        <div className="mt-5 flex justify-end gap-2"><button type="button" className="btn btn-ghost" onClick={onClose}>Cancel</button><button className="btn btn-primary" disabled={busy}>{busy ? 'Saving…' : 'Save property'}</button></div>
      </form>
    </div>
  )
}

export default function Properties() {
  const [items, setItems] = useState(null); const [err, setErr] = useState(''); const [form, setForm] = useState(null)
  const load = () => api.properties().then(setItems).catch((e) => setErr(e.message))
  useEffect(() => { load() }, [])
  const toggle = (p) => api.editProperty(p.id, { available: !p.available }).then(load).catch((e) => setErr(e.message))
  const remove = (p) => { if (confirm(`Delete "${p.title}"? Properties with viewings are archived instead.`)) api.deleteProperty(p.id).then(load).catch((e) => setErr(e.message)) }
  return (
    <div>
      <div className="mb-6 flex flex-wrap items-start justify-between gap-3">
        <div><h1 className="font-display text-3xl">Properties</h1><p className="mt-1 text-sm text-slate2">Fictional demo data. Hidden properties are excluded from lead matching.</p></div>
        <button className="btn btn-primary" onClick={() => setForm({})}><Plus size={16} />Add property</button>
      </div>
      {err && <p className="mb-4 text-sm text-red-700">{err}</p>}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {(items || []).map((p) => (
          <div key={p.id} className={p.available ? '' : 'opacity-60'}>
            <PropertyCard property={p} />
            <div className="mt-2 flex gap-2">
              <button className="btn btn-ghost flex-1 !py-1.5" onClick={() => setForm(p)}><Pencil size={14} />Edit</button>
              <button className="btn btn-ghost flex-1 !py-1.5" onClick={() => toggle(p)}>{p.available ? <><EyeOff size={14} />Hide</> : <><Eye size={14} />Show</>}</button>
              <button className="btn btn-ghost !py-1.5 text-red-700" onClick={() => remove(p)} aria-label={`Delete ${p.title}`}><Trash2 size={14} /></button>
            </div>
          </div>
        ))}
      </div>
      {form && <Form initial={form} onClose={() => setForm(null)} onSaved={() => { setForm(null); load() }} />}
    </div>
  )
}
