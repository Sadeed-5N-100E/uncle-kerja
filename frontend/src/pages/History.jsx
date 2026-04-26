import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { Clock, ChevronRight, Flame, BarChart3, Briefcase, AlertCircle } from 'lucide-react'

const VERDICT_STYLE = {
  'Strong Fit':  'bg-green-100 text-green-700 border-green-200',
  'Good Fit':    'bg-blue-100 text-blue-700 border-blue-200',
  'Partial Fit': 'bg-amber-100 text-amber-700 border-amber-200',
  'Weak Fit':    'bg-orange-100 text-orange-700 border-orange-200',
  'Not a Fit':   'bg-red-100 text-red-700 border-red-200',
}

const SCORE_COLOR = (s) =>
  s >= 70 ? 'text-green-600' : s >= 50 ? 'text-amber-600' : 'text-red-600'

function AnalysisCard({ a }) {
  const date = a.created_at
    ? new Date(a.created_at).toLocaleString('en-MY', {
        day: 'numeric', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit',
      })
    : '—'

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 hover:border-slate-300 transition-all group">
      <div className="flex items-start gap-4">
        {/* Score circle */}
        <div className="shrink-0 text-center w-14">
          <span className={`text-2xl font-extrabold ${SCORE_COLOR(a.overall_score || 0)}`}>
            {a.overall_score ?? '—'}
          </span>
          <p className="text-xs text-slate-600">/100</p>
        </div>

        {/* Details */}
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            {a.verdict && (
              <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${VERDICT_STYLE[a.verdict] || 'bg-slate-800 text-slate-400 border-slate-700'}`}>
                {a.verdict}
              </span>
            )}
            {a.jobs_count > 0 && (
              <span className="text-xs text-slate-500 flex items-center gap-1">
                <Briefcase size={10} /> {a.jobs_count} jobs found
              </span>
            )}
            {a.user_email && (
              <span className="text-xs text-slate-600 ml-auto">{a.user_email}</span>
            )}
          </div>

          <p className="text-sm font-medium text-slate-800 truncate">
            {a.job_title || 'Resume Analysis'}
          </p>

          {a.summary && (
            <p className="text-xs text-slate-500 mt-1 line-clamp-2">{a.summary}</p>
          )}

          {a.roast_opening && (
            <p className="text-xs text-orange-600 mt-1 italic line-clamp-1">
              🔥 "{a.roast_opening}"
            </p>
          )}

          <p className="text-xs text-slate-400 flex items-center gap-1 mt-2">
            <Clock size={10} /> {date}
          </p>
        </div>

        {/* View button */}
        <Link to={`/results/${a.id}`}
          className="shrink-0 flex items-center gap-1 text-xs text-purple-600 hover:text-purple-700
                     border border-purple-200 hover:border-purple-400 px-3 py-1.5 rounded-lg
                     transition-all group-hover:gap-2">
          View <ChevronRight size={12} />
        </Link>
      </div>
    </div>
  )
}

export default function History() {
  const [data,    setData]    = useState([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

  useEffect(() => {
    api.history(20)
      .then(d  => setData(d.analyses || []))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="max-w-3xl mx-auto px-4 py-10 page-enter">
        <div className="flex items-center gap-3 mb-8">
          <BarChart3 size={22} className="text-purple-600" />
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Analysis History</h1>
            <p className="text-slate-500 text-sm">Your past resume analyses — stored in the database</p>
          </div>
          <Link to="/analyse"
            className="ml-auto bg-purple-600 hover:bg-purple-500 text-white text-sm
                       font-semibold px-4 py-2 rounded-xl transition-colors">
            New Analysis
          </Link>
        </div>

        {loading && (
          <div className="flex justify-center py-16">
            <div className="animate-spin w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full" />
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 bg-red-50 border border-red-200
                          text-red-700 text-sm px-4 py-3 rounded-xl">
            <AlertCircle size={15} /> {error}
          </div>
        )}

        {!loading && !error && data.length === 0 && (
          <div className="text-center py-16">
            <img src="/assets/score-agent-mascot.png" alt=""
                 className="w-24 h-24 object-contain mx-auto mb-4 opacity-40" />
            <p className="text-slate-500 text-sm mb-4">No analyses yet.</p>
            <Link to="/analyse"
              className="inline-flex items-center gap-2 bg-purple-600 hover:bg-purple-500
                         text-white text-sm font-semibold px-5 py-2.5 rounded-xl transition-colors">
              Analyse your first resume <ChevronRight size={15} />
            </Link>
          </div>
        )}

        {!loading && data.length > 0 && (
          <div className="space-y-3">
            {data.map(a => <AnalysisCard key={a.id} a={a} />)}
          </div>
        )}
    </div>
  )
}
