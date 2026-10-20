const BASE = (import.meta.env.VITE_API_URL || '') + '/api'
const TOKEN_KEY = 'agent_token'
export const auth = {
  get: () => localStorage.getItem(TOKEN_KEY),
  set: (t) => localStorage.setItem(TOKEN_KEY, t),
  clear: () => localStorage.removeItem(TOKEN_KEY),
}

async function raw(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json', ...(auth.get() ? { Authorization: `Bearer ${auth.get()}` } : {}) }
  let res
  try { res = await fetch(BASE + path, { ...opts, headers }) }
  catch { throw new Error('Cannot reach the server. Check that the backend is running.') }
  if (res.status === 401 && !path.startsWith('/auth/login') && path !== '/chat') {
    auth.clear(); window.location.assign('/login')
  }
  return res
}
async function req(path, opts) {
  const res = await raw(path, opts)
  const data = await res.json().catch(() => ({}))
  if (!res.ok) { const e = new Error(data.error || 'Request failed'); e.data = data; throw e }
  return data
}
const send = (method) => (p, body) => req(p, { method, body: JSON.stringify(body) })
const post = send('POST')

export const api = {
  health: () => req('/health'),
  login: (username, password) => post('/auth/login', { username, password }),
  chat: (message, lead_id, lang) => post('/chat', { message, lead_id, lang }),
  stats: () => req('/dashboard/stats'),
  leads: () => req('/leads'),
  lead: (id) => req(`/leads/${id}`),
  conversation: (id) => req(`/leads/${id}/conversation`),
  properties: () => req('/properties'),
  matches: (id) => req(`/properties/matches/${id}`),
  addProperty: (b) => post('/properties', b),
  editProperty: (id, b) => send('PUT')(`/properties/${id}`, b),
  deleteProperty: (id) => req(`/properties/${id}`, { method: 'DELETE' }),
  whatsappInfo: (id) => req(`/leads/${id}/whatsapp`),
  sendWhatsApp: (id, body, lang) => post(`/leads/${id}/whatsapp/send`, { body, lang }),
  drafts: (id, lang) => req(`/leads/${id}/followup-drafts?lang=${lang}`),
  viewings: () => req('/viewings'),
  createViewing: (b) => post('/viewings', b),
  async exportLeads() {
    const res = await raw('/leads/export.csv')
    if (!res.ok) throw new Error('Export failed. Please try again.')
    const url = URL.createObjectURL(await res.blob())
    const a = Object.assign(document.createElement('a'), { href: url, download: 'leads.csv' })
    document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url)
  },
}
export const fmtAED = (n) => (n == null ? '—' : 'AED ' + Number(n).toLocaleString('en-US'))
export const fmtShort = (n) => (n == null ? '—' : n >= 1e6 ? `AED ${+(n / 1e6).toFixed(2)}M` : `AED ${Math.round(n / 1e3)}K`)
export const typeLabel = (p) => `${p.bedrooms === 0 ? 'Studio' : p.bedrooms + ' Bedroom'} ${p.bedrooms === 0 ? '' : p.property_type}`.trim()
