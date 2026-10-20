import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { Send, Play, RotateCcw, ArrowLeft, CheckCircle2, AlertCircle, Languages } from 'lucide-react'
import useChat from '../hooks/useChat'
import LeadProfile from '../components/LeadProfile'
import PropertyCard from '../components/PropertyCard'
import ViewingModal from '../components/ViewingModal'
import QuickReplies from '../components/QuickReplies'
import { T, DEMO_SCRIPT } from '../services/i18n'

export default function Chat() {
  const c = useChat(); const { lang } = c; const t = T[lang]; const ar = lang === 'ar'
  const [input, setInput] = useState('')
  const [target, setTarget] = useState(null)
  const [demoRunning, setDemoRunning] = useState(false)
  const end = useRef(null)
  useEffect(() => { end.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }) }, [c.messages, c.loading, c.matches])
  useEffect(() => { document.documentElement.lang = lang }, [lang])

  const submit = async (e) => { e.preventDefault(); const x = input; setInput(''); if (!(await c.send(x))) setInput(x) }
  const runDemo = async () => {
    c.reset(); setDemoRunning(true)
    await new Promise((r) => setTimeout(r, 300))
    for (const line of DEMO_SCRIPT[lang]) { if (!(await c.send(line))) break; await new Promise((r) => setTimeout(r, 600)) }  // each line goes through the real AI
    setDemoRunning(false)
  }
  const busy = c.loading || demoRunning
  const qualified = c.status === 'qualified'
  const nextField = !qualified ? c.missing[0] : null
  const dateLoc = ar ? 'ar-AE' : 'en-GB'

  return (
    <div className="min-h-screen">
      <div className="mx-auto grid max-w-6xl gap-5 p-4 lg:grid-cols-[1fr_320px] lg:p-6">
        <section className="card flex h-[calc(100vh-2rem)] flex-col overflow-hidden lg:h-[calc(100vh-3rem)]">
          <header className="flex items-center gap-3 border-b border-line px-5 py-4" dir={ar ? 'rtl' : 'ltr'}>
            <Link to="/" aria-label="Home" className="text-slate2"><ArrowLeft size={18} className={ar ? 'rotate-180' : ''} /></Link>
            <div className="flex-1">
              <h1 className="font-display text-lg leading-tight">{t.title}</h1>
              <p className="text-xs text-slate2">{t.sub} · <span className="text-pine">● {t.online}</span></p>
            </div>
            <button className="btn btn-ghost !py-1.5 !text-xs" onClick={() => c.setLang(ar ? 'en' : 'ar')} disabled={busy} aria-label="Switch language"><Languages size={13} />{ar ? 'English' : 'العربية'}</button>
            <button className="btn btn-ghost !py-1.5 !text-xs" onClick={c.reset} disabled={busy}><RotateCcw size={13} />{t.newChat}</button>
          </header>
          <div className="flex flex-wrap items-center justify-between gap-2 bg-amberbg px-5 py-2 text-xs text-amber2" dir={ar ? 'rtl' : 'ltr'}>
            <span><b>{t.demoBanner}</b> {t.demoNote}</span>
            <button className="btn btn-ghost !py-1 !text-xs" onClick={runDemo} disabled={busy}><Play size={12} />{t.loadDemo}</button>
          </div>
          <div className="flex-1 space-y-3 overflow-y-auto px-5 py-5" aria-live="polite">
            {c.messages.map((m, i) => (
              <div key={i} className={`msg flex ${m.role === 'user' ? 'justify-end' : ''}`}>
                {m.viewing ? (
                  <div dir={ar ? 'rtl' : 'ltr'} className="flex items-center gap-2 rounded-xl border border-pine/30 bg-pine-soft px-4 py-3 text-sm font-semibold text-pine-dark"><CheckCircle2 size={16} />{t.viewingDone} {m.content}</div>
                ) : (
                  <div dir="auto" className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-4 py-2.5 text-start text-[15px] leading-relaxed ${m.role === 'user' ? 'rounded-br-sm bg-pine text-white' : 'rounded-bl-sm bg-mist text-ink'}`}>{m.content}</div>
                )}
              </div>
            ))}
            {c.loading && <div className="flex"><div className="rounded-2xl bg-mist px-4 py-3 text-slate2" aria-label="Assistant is typing">● ● ●</div></div>}
            {c.error && <div className="flex items-start gap-2 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-800"><AlertCircle size={16} className="mt-0.5 shrink-0" />{c.error}</div>}
            {qualified && c.matches.length > 0 && (
              <div className="pt-2" dir={ar ? 'rtl' : 'ltr'}>
                <p className="mb-3 text-sm font-semibold">{c.matchQuality === 'nearest' ? t.nearest(c.matches.length) : t.matchN(c.matches.length)}</p>
                <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                  {c.matches.map((p) => <PropertyCard key={p.id} property={p} lang={lang} onDetails={() => c.addLocal('assistant', t.great)} onSchedule={setTarget} />)}
                </div>
              </div>
            )}
            <div ref={end} />
          </div>
          {nextField && !demoRunning && <QuickReplies field={nextField} lang={lang} disabled={busy} onPick={c.send} />}
          <form onSubmit={submit} className="flex gap-2 border-t border-line p-3">
            <input dir="auto" value={input} onChange={(e) => setInput(e.target.value)} maxLength={2000} disabled={busy} aria-label="Message"
              placeholder={t.placeholder} className="flex-1 rounded-lg border border-line bg-white px-4 py-2.5 text-[15px] outline-none focus:border-pine" />
            <button className="btn btn-primary" disabled={busy || !input.trim()} aria-label={t.send}><Send size={16} className={ar ? 'rotate-180' : ''} /></button>
          </form>
        </section>
        <div className="lg:sticky lg:top-6 lg:self-start"><LeadProfile profile={c.profile} status={c.status} lang={lang} /></div>
      </div>
      {target && <ViewingModal property={target} leadId={c.leadId} lang={lang} onClose={() => setTarget(null)}
        onDone={(v) => { setTarget(null); c.addLocal('assistant', `${target.title}, ${new Date(v.date + 'T00:00').toLocaleDateString(dateLoc, { day: 'numeric', month: 'long', year: 'numeric' })} · ${v.time}. ${t.confirm}`, { viewing: true }) }} />}
    </div>
  )
}
