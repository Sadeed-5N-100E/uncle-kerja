import { ExternalLink, FileText, MapPin, Building2, Calendar } from 'lucide-react'

const SOURCE_BADGE = {
  serpapi:     { label: 'Google Jobs',  cls: 'bg-blue-100 text-blue-700' },
  theirstack:  { label: 'TheirStack',   cls: 'bg-indigo-100 text-indigo-700' },
  aidevboard:  { label: 'AI Dev Board', cls: 'bg-green-100 text-green-700' },
}

export default function JobCard({ job, index, onCoverLetter }) {
  const score = job.match_score || 0
  const scoreColor = score >= 70 ? 'text-green-600' : score >= 50 ? 'text-orange-500' : 'text-slate-400'
  const badge = SOURCE_BADGE[job.source] || { label: job.source || 'Live', cls: 'bg-slate-100 text-slate-500' }

  return (
    <div className="bg-white rounded-xl border border-slate-200 hover:border-slate-300 transition-colors p-5 mb-3">
      <div className="flex items-start gap-4">
        {/* Score */}
        <div className="shrink-0 text-center w-14">
          <span className={`text-2xl font-extrabold ${scoreColor}`}>{score}%</span>
          <p className="text-xs text-slate-400">match</p>
        </div>

        {/* Details */}
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${badge.cls}`}>{badge.label}</span>
            {job.posted && (
              <span className="flex items-center gap-1 text-xs text-slate-400">
                <Calendar size={11} /> {job.posted}
              </span>
            )}
          </div>

          <h3 className="font-semibold text-slate-900 text-sm leading-snug">{job.title}</h3>
          <div className="flex flex-wrap items-center gap-3 mt-1 text-xs text-slate-500">
            <span className="flex items-center gap-1"><Building2 size={11} /> {job.company}</span>
            <span className="flex items-center gap-1"><MapPin size={11} /> {job.location}</span>
            {job.salary_range && job.salary_range !== 'Not specified' && (
              <span className="text-slate-600 font-medium">{job.salary_range}</span>
            )}
          </div>

          {job.why_matched && (
            <p className="text-xs text-slate-500 italic mt-2">{job.why_matched}</p>
          )}

          {/* Matched skills */}
          {(job.matched_skills || []).length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {job.matched_skills.map(s => (
                <span key={s} className="text-xs bg-green-50 text-green-700 px-1.5 py-0.5 rounded">{s}</span>
              ))}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex flex-col gap-2 shrink-0">
          {job.apply_url ? (
            <a href={job.apply_url} target="_blank" rel="noopener noreferrer"
              className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs px-3 py-1.5 rounded-lg transition-colors whitespace-nowrap">
              Apply <ExternalLink size={11} />
            </a>
          ) : null}
          {onCoverLetter && (
            <button onClick={onCoverLetter}
              className="flex items-center gap-1.5 border border-slate-200 text-slate-600 hover:bg-slate-50 text-xs px-3 py-1.5 rounded-lg transition-colors whitespace-nowrap">
              <FileText size={11} /> Cover letter
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
