import { useState, useEffect } from 'react'
import { api } from '../lib/api'
import { RefreshCw, Mail, Activity, Loader2 } from 'lucide-react'

export default function Admin() {
  const [health,  setHealth]  = useState(null)
  const [inbox,   setInbox]   = useState([])
  const [loading, setLoading] = useState(true)
  const [polling, setPolling] = useState(false)
  const [pollResult, setPollResult] = useState(null)

  const loadData = async () => {
    setLoading(true)
    try {
      const [h, m] = await Promise.all([api.health(), api.inbox(20)])
      setHealth(h)
      setInbox(m.messages || [])
    } catch(e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadData() }, [])

  const runPoll = async () => {
    setPolling(true); setPollResult(null)
    try {
      const r = await api.pollInbox()
      setPollResult(`Processed ${r.count} message(s): ${JSON.stringify(r.processed?.map(m => m.intent || m.error))}`)
      await loadData()
    } catch(e) {
      setPollResult('Error: ' + e.message)
    } finally {
      setPolling(false)
    }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64 text-slate-400">
      <Loader2 size={24} className="animate-spin mr-2" /> Loading admin panel…
    </div>
  )

  const stat = (label, value, sub = '') => (
    <div className="bg-white rounded-xl border border-slate-200 p-4">
      <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">{label}</p>
      <p className="text-2xl font-bold text-slate-900">{value}</p>
      {sub && <p className="text-xs text-slate-400 mt-0.5">{sub}</p>}
    </div>
  )

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 page-enter">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Admin Panel</h1>
          <p className="text-slate-500 text-sm">System health and inbox management</p>
        </div>
        <button onClick={loadData}
          className="flex items-center gap-1.5 text-sm border border-slate-200 rounded-lg px-3 py-2 hover:bg-slate-50 transition-colors">
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        {stat('Status', health?.status === 'ok' ? '🟢 OK' : '🔴 Down')}
        {stat('AgentMail', health?.email_ready ? '✓ Ready' : '✗ Not configured', health?.agentmail_inbox || '')}
        {stat('Inbox', inbox.length, 'recent messages')}
        {stat('Sent', inbox.filter(m => (m.labels||[]).includes('sent')).length, 'sent messages')}
      </div>

      {/* Reply agent */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 mb-6">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Activity size={16} className="text-blue-600" />
            <h2 className="font-semibold text-slate-900">Reply Agent</h2>
          </div>
          <button onClick={runPoll} disabled={polling}
            className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white text-sm px-4 py-2 rounded-lg transition-colors">
            <RefreshCw size={13} className={polling ? 'animate-spin' : ''} />
            {polling ? 'Running…' : 'Process inbox now'}
          </button>
        </div>
        <p className="text-slate-500 text-sm mb-2">Reads unprocessed inbound emails, classifies intent, and auto-replies. Runs automatically every 5 minutes.</p>
        {pollResult && (
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 text-xs text-slate-600 font-mono">
            {pollResult}
          </div>
        )}
      </div>

      {/* Inbox table */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        <div className="flex items-center gap-2 p-4 border-b border-slate-100">
          <Mail size={16} className="text-slate-600" />
          <h2 className="font-semibold text-slate-900">Inbox — last 20</h2>
        </div>
        {inbox.length === 0 ? (
          <p className="text-slate-400 text-sm p-6 text-center">No messages.</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 border-b border-slate-100">
              <tr>
                <th className="text-left text-xs font-medium text-slate-400 px-4 py-2">From</th>
                <th className="text-left text-xs font-medium text-slate-400 px-4 py-2">Subject</th>
                <th className="text-left text-xs font-medium text-slate-400 px-4 py-2 hidden sm:table-cell">Date</th>
                <th className="text-left text-xs font-medium text-slate-400 px-4 py-2">Labels</th>
              </tr>
            </thead>
            <tbody>
              {inbox.map((m, i) => (
                <tr key={i} className="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-3 text-slate-600 max-w-[160px] truncate">{m.from || '—'}</td>
                  <td className="px-4 py-3 text-slate-800 max-w-xs truncate">{m.subject || '(no subject)'}</td>
                  <td className="px-4 py-3 text-slate-400 text-xs hidden sm:table-cell">
                    {m.created_at ? new Date(m.created_at).toLocaleString() : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1 flex-wrap">
                      {(m.labels || []).map(l => (
                        <span key={l} className="text-xs bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded">{l}</span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
