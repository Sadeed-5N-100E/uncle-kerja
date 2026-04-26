import { useState, useEffect } from 'react'
import { Bell, RefreshCw, Loader2, Mail, ExternalLink } from 'lucide-react'
import { api } from '../lib/api'
import { useAuth } from '../context/AuthContext'

export default function Alerts() {
  const { user } = useAuth()
  const [email,   setEmail]   = useState(user?.email || '')
  const [status,  setStatus]  = useState('')
  const [polling, setPolling] = useState(false)
  const [inbox,   setInbox]   = useState([])
  const [loadingInbox, setLoadingInbox] = useState(true)

  useEffect(() => {
    if (!user?.email) { setLoadingInbox(false); return }
    api.jobEmails(user.email, 10)
      .then(d => setInbox(d.emails || []))
      .catch(() => {})
      .finally(() => setLoadingInbox(false))
  }, [user?.email])

  const subscribeNow = async () => {
    setStatus('Subscribing…')
    try {
      const sessions = JSON.parse(localStorage.getItem('cc_sessions') || '[]')
      const sessionId = sessions[sessions.length - 1]
      if (!sessionId) { setStatus('Run an analysis first.'); return }
      const r = await api.subscribe(sessionId, email)
      setStatus(r.welcome_email_sent
        ? `✓ Subscribed! Welcome email sent to ${email} from usm.z.ai@agentmail.to`
        : '✓ Subscribed! Emails will send once a resume is analysed.')
    } catch (e) {
      setStatus('✗ ' + e.message)
    }
  }

  const pollNow = async () => {
    setPolling(true)
    try {
      const r = await api.pollInbox()
      const count = r.count || 0
      setStatus(count > 0 ? `Processed ${count} reply(ies).` : 'No new replies.')
      if (user?.email) {
        const d = await api.jobEmails(user.email, 10)
        setInbox(d.emails || [])
      }
    } catch(e) {
      setStatus('Poll error: ' + e.message)
    } finally {
      setPolling(false)
    }
  }

  return (
    <div className="max-w-3xl mx-auto px-4 py-8 page-enter">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">Job Alerts</h1>
        <p className="text-slate-500 text-sm mt-1">
          Manage your email job alerts. Powered by{' '}
          <span className="font-medium text-slate-700">Career Copilot MY</span> via{' '}
          <code className="text-xs bg-slate-100 px-1.5 py-0.5 rounded">usm.z.ai@agentmail.to</code>
        </p>
      </div>

      {/* Subscribe card */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Bell size={18} className="text-blue-600" />
          <h2 className="font-semibold text-slate-900">Subscribe to daily alerts</h2>
        </div>
        <p className="text-slate-500 text-sm mb-4">
          We'll email matching jobs every morning. You can reply directly to the email to:
        </p>
        <ul className="text-sm text-slate-600 space-y-1 mb-4 ml-4 list-disc">
          <li>Ask for jobs in a different location (<em>"find me jobs in Penang"</em>)</li>
          <li>Change role (<em>"show me frontend roles instead"</em>)</li>
          <li>Stop alerts (<em>"unsubscribe"</em>)</li>
        </ul>
        <div className="flex gap-2">
          <input type="email" value={email} onChange={e => setEmail(e.target.value)}
            placeholder="your@email.com"
            className="flex-1 border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
          <button onClick={subscribeNow}
            className="bg-blue-600 hover:bg-blue-700 text-white text-sm px-5 py-2 rounded-lg transition-colors">
            Subscribe
          </button>
        </div>
        {status && <p className={`text-xs mt-2 ${status.startsWith('✓') ? 'text-green-600' : 'text-red-600'}`}>{status}</p>}
      </div>

      {/* Inbox */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Mail size={18} className="text-slate-600" />
            <h2 className="font-semibold text-slate-900">Job Alerts Sent to You</h2>
            <span className="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full">{inbox.length}</span>
          </div>
          <button onClick={pollNow} disabled={polling}
            className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 border border-slate-200 rounded-lg px-3 py-1.5 transition-colors">
            <RefreshCw size={13} className={polling ? 'animate-spin' : ''} />
            {polling ? 'Checking…' : 'Check replies'}
          </button>
        </div>

        {loadingInbox ? (
          <div className="flex items-center gap-2 text-slate-400 text-sm py-4">
            <Loader2 size={16} className="animate-spin" /> Loading…
          </div>
        ) : inbox.length === 0 ? (
          <p className="text-slate-400 text-sm py-4 text-center">No job alerts sent yet. Subscribe above — alerts arrive from <strong>usm.z.ai@agentmail.to</strong>.</p>
        ) : (
          <div className="space-y-2">
            {inbox.map((m, i) => (
              <div key={i} className="flex items-start justify-between gap-4 py-3 border-b border-slate-100 last:border-0">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-800 truncate">{m.subject || '(no subject)'}</p>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {m.from} · {m.created_at ? new Date(m.created_at).toLocaleString() : ''}
                  </p>
                  {(m.labels || []).map(l => (
                    <span key={l} className="inline-block text-xs bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded mr-1 mt-1">{l}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
