const BASE = ''  // empty = same origin (Vite proxy handles /api, /analyze, etc.)

// Always attach the stored auth token automatically
function _authHeader() {
  const t = localStorage.getItem('cc_token')
  return t ? { 'Authorization': `Bearer ${t}` } : {}
}

async function req(method, path, body, token) {
  const headers = { 'Content-Type': 'application/json', ..._authHeader() }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const opts = { method, headers }
  if (body && !(body instanceof FormData)) opts.body = JSON.stringify(body)
  if (body instanceof FormData) { delete headers['Content-Type']; opts.body = body }
  const r = await fetch(BASE + path, opts)
  if (!r.ok) {
    const err = await r.json().catch(() => ({}))
    throw new Error(err.detail || err.message || `HTTP ${r.status}`)
  }
  return r.json()
}

export const api = {
  // Auth
  login:    (email, pw)        => req('POST', '/api/auth/login',  { email, password: pw }),
  signup:   (email, pw, role)  => req('POST', '/api/auth/signup', { email, password: pw, role }),
  me:       (token)            => req('GET',  '/api/auth/me', null, token),

  // Analysis
  analyze:  (fd)               => req('POST', '/analyze', fd),      // FormData
  session:  (id)               => req('GET',  `/session/${id}`),

  // Cover letter
  coverLetter: (sessionId, idx) =>
    req('POST', '/cover-letter', { session_id: sessionId, job_index: idx }),

  // Alerts
  subscribe:   (sessionId, email) =>
    req('POST', '/alerts/subscribe', { session_id: sessionId, email }),
  unsubscribe: (sessionId)        =>
    req('DELETE', `/alerts/unsubscribe/${sessionId}`),

  // Inbox (admin)
  inbox:    (limit = 20)       => req('GET', `/inbox/messages?limit=${limit}`),
  pollInbox: ()                => req('POST', '/inbox/poll', {}),

  // Job emails — filtered by the logged-in user's email
  jobEmails: (email = '', limit = 10) =>
    req('GET', `/inbox/job-emails?email=${encodeURIComponent(email)}&limit=${limit}`),

  // History (DB-backed, persists across restarts)
  history:     (limit = 10) => req('GET', `/history?limit=${limit}`),
  historyFull: (id)          => req('GET', `/history/${id}/full`),

  // DB stats (admin)
  dbStats: () => req('GET', '/db/stats'),

  // Health
  health:   ()                 => req('GET', '/health'),
}
