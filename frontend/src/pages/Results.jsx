import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../lib/api'
import ScoreGauge from '../components/ScoreGauge'
import RoastCard from '../components/RoastCard'
import ActionPlan from '../components/ActionPlan'
import JobCard from '../components/JobCard'
import CoverLetterModal from '../components/CoverLetterModal'
import { ArrowLeft, Bell, AlertCircle } from 'lucide-react'

export default function Results() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const [session, setSession] = useState(null)
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState('score')
  const [coverJob, setCoverJob] = useState(null)
  const [alertEmail, setAlertEmail] = useState('')
  const [alertStatus, setAlertStatus] = useState(null)

  useEffect(() => {
    api.session(sessionId)
      .then(s  => setSession(s))
      .catch(() => navigate('/'))
      .finally(() => setLoading(false))
  }, [sessionId])

  const subscribeAlerts = async () => {
    if (!alertEmail.trim()) return
    try {
      const r = await api.subscribe(sessionId, alertEmail)
      setAlertStatus(r.welcome_email_sent
        ? `✓ Subscribed! Job alert sent to ${alertEmail}`
        : '✓ Subscribed! (Email send requires configuration)')
    } catch (e) {
      setAlertStatus('✗ ' + e.message)
    }
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64 text-slate-400">Loading results…</div>
  )
  if (!session) return null

  const score    = session.score       || {}
  const roast    = session.roast       || {}
  const plan     = session.action_plan || {}
  const jobs     = session.jobs        || {}
  const profile  = session.profile     || {}
  const allJobs  = [...(jobs.local_jobs || []), ...(jobs.remote_jobs || [])]

  const tabs = [
    { key: 'score',  label: 'Score'       },
    { key: 'roast',  label: 'Roast'       },
    { key: 'plan',   label: 'Action Plan' },
    { key: 'jobs',   label: `Jobs (${allJobs.length})` },
  ]

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 page-enter">
      {/* Back + title */}
      <div className="flex items-center gap-4 mb-6">
        <button onClick={() => navigate('/')} className="text-slate-400 hover:text-slate-700 transition-colors">
          <ArrowLeft size={20} />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            {profile.full_name ? `${profile.full_name}'s Analysis` : 'Analysis Results'}
          </h1>
          <p className="text-slate-500 text-sm">
            {profile.current_role || ''}{profile.years_experience ? ` · ${profile.years_experience} yrs exp` : ''}
          </p>
        </div>
        {session.errors?.length > 0 && (
          <div className="ml-auto flex items-center gap-1 text-amber-600 text-xs bg-amber-50 px-2 py-1 rounded-lg">
            <AlertCircle size={12} /> {session.errors.length} warning(s)
          </div>
        )}
      </div>

      {/* Score summary bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-4 mb-6 flex flex-wrap gap-6 items-center">
        <div className="text-center">
          <div className={`text-3xl font-extrabold ${score.overall_score >= 70 ? 'text-green-600' : score.overall_score >= 50 ? 'text-orange-500' : 'text-red-500'}`}>
            {score.overall_score ?? '—'}/100
          </div>
          <div className="text-xs text-slate-400">Overall fit</div>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-semibold
          ${{ 'Strong Fit':'bg-green-100 text-green-700', 'Good Fit':'bg-blue-100 text-blue-700',
               'Partial Fit':'bg-amber-100 text-amber-700', 'Weak Fit':'bg-orange-100 text-orange-700',
               'Not a Fit':'bg-red-100 text-red-700' }[score.verdict] || 'bg-slate-100 text-slate-600'}`}>
          {score.verdict || 'Unknown'}
        </div>
        <p className="text-slate-600 text-sm flex-1 min-w-0">{score.one_line_summary}</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-100 rounded-xl p-1 mb-6">
        {tabs.map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium transition-colors
              ${tab === t.key ? 'bg-white shadow-sm text-slate-900' : 'text-slate-500 hover:text-slate-700'}`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {tab === 'score' && <ScoreGauge score={score} />}
      {tab === 'roast' && <RoastCard roast={roast} />}
      {tab === 'plan'  && <ActionPlan plan={plan} />}

      {tab === 'jobs' && (
        <div className="space-y-6">
          {/* Malaysian jobs */}
          <div>
            <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
              🇲🇾 Malaysian Jobs
            </h3>
            {(jobs.local_jobs || []).length === 0
              ? <p className="text-slate-400 text-sm">No Malaysian jobs found. Try adding more skills to your resume.</p>
              : (jobs.local_jobs || []).map((j, i) => (
                  <JobCard key={i} job={j} index={i} onCoverLetter={() => setCoverJob({ job: j, index: i })} />
                ))
            }
          </div>
          {/* Remote/tech jobs */}
          {(jobs.remote_jobs || []).length > 0 && (
            <div>
              <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
                🌐 Remote / AI Tech Jobs
              </h3>
              {(jobs.remote_jobs || []).map((j, i) => (
                <JobCard key={i} job={j} index={(jobs.local_jobs||[]).length + i} />
              ))}
            </div>
          )}

          {/* Alert subscribe */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-5">
            <div className="flex items-center gap-2 mb-2">
              <Bell size={16} className="text-blue-600" />
              <span className="font-semibold text-blue-900 text-sm">Get daily job alerts</span>
            </div>
            <p className="text-blue-700 text-xs mb-3">
              Fresh matching jobs emailed every morning. Reply to the email to refine your search.
            </p>
            <div className="flex gap-2">
              <input type="email" value={alertEmail} onChange={e => setAlertEmail(e.target.value)}
                placeholder="your@email.com"
                className="flex-1 border border-blue-200 bg-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400" />
              <button onClick={subscribeAlerts}
                className="bg-blue-600 hover:bg-blue-700 text-white text-sm px-4 py-2 rounded-lg transition-colors whitespace-nowrap">
                Subscribe
              </button>
            </div>
            {alertStatus && <p className="text-xs mt-2 text-blue-700">{alertStatus}</p>}
          </div>
        </div>
      )}

      {/* Cover letter modal */}
      {coverJob && (
        <CoverLetterModal
          sessionId={sessionId}
          jobIndex={coverJob.index}
          jobTitle={coverJob.job.title}
          company={coverJob.job.company}
          onClose={() => setCoverJob(null)}
        />
      )}
    </div>
  )
}
