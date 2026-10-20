import { useCallback, useRef, useState } from 'react'
import { api } from '../services/api'
import { GREETING, FIELD_ORDER, hasArabic } from '../services/i18n'

export default function useChat() {
  const [lang, setLangState] = useState('en')
  const [messages, setMessages] = useState([{ role: 'assistant', content: GREETING.en, greeting: true }])
  const [leadId, setLeadId] = useState(null)
  const [profile, setProfile] = useState({})
  const [status, setStatus] = useState('new')
  const [missing, setMissing] = useState(FIELD_ORDER)
  const [matches, setMatches] = useState([])
  const [matchQuality, setMatchQuality] = useState('none')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const idRef = useRef(null); const busy = useRef(false); const langRef = useRef('en')

  const setLang = useCallback((l) => {
    langRef.current = l; setLangState(l)
    // switching language before the first message swaps the greeting
    setMessages((m) => (m.length === 1 && m[0].greeting ? [{ role: 'assistant', content: GREETING[l], greeting: true }] : m))
  }, [])

  const send = useCallback(async (text) => {
    const t = text.trim()
    if (!t || busy.current) return false
    busy.current = true; setLoading(true); setError('')
    if (hasArabic(t)) setLang('ar')
    setMessages((m) => [...m, { role: 'user', content: t }])
    try {
      const r = await api.chat(t, idRef.current, langRef.current)
      idRef.current = r.lead_id; setLeadId(r.lead_id)
      setMessages((m) => [...m, { role: 'assistant', content: r.reply }])
      setProfile(r.profile); setStatus(r.status); setMissing(r.missing_fields); setMatches(r.matches); setMatchQuality(r.match_quality)
      if (r.language) setLang(r.language)
      return true
    } catch (e) {
      if (e.data?.lead_id) { idRef.current = e.data.lead_id; setLeadId(e.data.lead_id) }
      setError(e.message); return false
    } finally { busy.current = false; setLoading(false) }
  }, [setLang])

  const reset = useCallback(() => {
    idRef.current = null; setLeadId(null); setMessages([{ role: 'assistant', content: GREETING[langRef.current], greeting: true }])
    setProfile({}); setStatus('new'); setMissing(FIELD_ORDER); setMatches([]); setError('')
  }, [])
  const addLocal = useCallback((role, content, extra = {}) => setMessages((m) => [...m, { role, content, ...extra }]), [])

  return { lang, setLang, messages, leadId, profile, status, missing, matches, matchQuality, loading, error, send, reset, addLocal }
}
