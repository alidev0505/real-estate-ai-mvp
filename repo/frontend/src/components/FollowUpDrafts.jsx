import { useEffect, useState } from 'react'
import { Mail, MessageCircle, Copy, Check, Send } from 'lucide-react'
import { api } from '../services/api'

export default function FollowUpDrafts({ leadId, phone, email }) {
  const [lang, setLang] = useState('en'); const [tab, setTab] = useState('whatsapp')
  const [d, setD] = useState(null); const [err, setErr] = useState(''); const [ok, setOk] = useState('')
  const [copied, setCopied] = useState(false); const [wa, setWa] = useState(null); const [waText, setWaText] = useState(''); const [busy, setBusy] = useState(false)
  useEffect(() => { setD(null); setErr(''); api.drafts(leadId, lang).then((x) => { setD(x); setWaText(x.whatsapp.body) }).catch((e) => setErr(e.message)) }, [leadId, lang])
  useEffect(() => { api.whatsappInfo(leadId).then(setWa).catch(() => setWa(null)) }, [leadId, ok])
  const text = d ? (tab === 'email' ? `Subject: ${d.email.subject}\n\n${d.email.body}` : waText) : ''
  const copy = async () => { try { await navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 1500) } catch { setErr('Copy failed. Select the text and copy it manually.') } }
  const send = async () => {
    if (!window.confirm(`Send this WhatsApp message to ${phone || 'this lead'}?`)) return
    setBusy(true); setErr(''); setOk('')
    try { const r = await api.sendWhatsApp(leadId, waText, lang); setOk(r.via === 'template' ? 'Sent using your approved template.' : 'Message sent.') }
    catch (e) { setErr(e.message) } finally { setBusy(false) }
  }
  const digits = (phone || '').replace(/\D/g, '')
  const seg = (on) => `rounded-md px-3 py-1.5 text-sm font-medium ${on ? 'bg-pine-soft text-pine-dark' : 'text-slate2 hover:bg-mist'}`
  const canSend = wa && wa.configured && wa.has_phone && !wa.demo && !wa.opted_out
  const hint = !wa ? '' : wa.demo ? 'Demo lead: sending is disabled.' : !wa.configured ? 'WhatsApp gateway not configured.' : wa.opted_out ? 'This contact opted out.'
    : wa.within_window ? 'Customer messaged within 24 hours: free-text allowed.' : wa.template_configured ? 'Outside 24 hours: your approved template will be used.' : 'Outside 24 hours: set WHATSAPP_FOLLOWUP_TEMPLATE to send.'
  return (
    <section className="card mt-8 p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div><h2 className="font-display text-xl">Follow-up drafts</h2><p className="text-sm text-slate2">Nothing is sent until you press Send.</p></div>
        <div className="flex gap-1"><button className={seg(lang === 'en')} onClick={() => setLang('en')}>English</button><button className={seg(lang === 'ar')} onClick={() => setLang('ar')}>العربية</button></div>
      </div>
      <div className="mt-4 flex gap-1 border-b border-line pb-2">
        <button className={seg(tab === 'whatsapp')} onClick={() => setTab('whatsapp')}><MessageCircle size={14} className="mr-1.5 inline" />WhatsApp</button>
        <button className={seg(tab === 'email')} onClick={() => setTab('email')}><Mail size={14} className="mr-1.5 inline" />Email</button>
      </div>
      {err && <p className="mt-3 text-sm text-red-700" role="alert">{err}</p>}
      {ok && <p className="mt-3 text-sm font-medium text-pine-dark">{ok}</p>}
      {d && tab === 'email' && <pre dir="auto" className="mt-3 whitespace-pre-wrap rounded-lg bg-mist p-4 font-sans text-sm leading-relaxed">{text}</pre>}
      {d && tab === 'whatsapp' && <textarea dir="auto" rows={6} value={waText} onChange={(e) => setWaText(e.target.value)} maxLength={4000} aria-label="WhatsApp message" className="mt-3 w-full rounded-lg border border-line bg-mist p-4 font-sans text-sm leading-relaxed outline-none focus:border-pine" />}
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <button className="btn btn-ghost" onClick={copy} disabled={!d}>{copied ? <Check size={15} /> : <Copy size={15} />}{copied ? 'Copied' : 'Copy'}</button>
        {tab === 'whatsapp' && <button className="btn btn-primary" onClick={send} disabled={!canSend || busy || !waText.trim()}><Send size={15} />{busy ? 'Sending…' : 'Send via WhatsApp'}</button>}
        {d && tab === 'email' && email && <a className="btn btn-ghost" href={`mailto:${email}?subject=${encodeURIComponent(d.email.subject)}&body=${encodeURIComponent(d.email.body)}`}>Open in email app</a>}
        {d && tab === 'whatsapp' && digits.length >= 8 && !canSend && <a className="btn btn-ghost" target="_blank" rel="noreferrer" href={`https://wa.me/${digits}?text=${encodeURIComponent(waText)}`}>Open in WhatsApp</a>}
      </div>
      {tab === 'whatsapp' && hint && <p className="mt-2 text-xs text-slate2">{hint}{wa?.last_outbound_status && ` Last message: ${wa.last_outbound_status}${wa.last_outbound_error ? ` (${wa.last_outbound_error})` : ''}.`}</p>}
    </section>
  )
}
