import { useEffect, useState } from 'react'

const CIRC = 2 * Math.PI * 54  // r=54

function Bar({ label, value, color }) {
  const [w, setW] = useState(0)
  useEffect(() => { setTimeout(() => setW(value), 100) }, [value])
  return (
    <div className="grid grid-cols-[100px_1fr_32px] items-center gap-3">
      <span className="text-sm text-slate-500">{label}</span>
      <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
        <div className={`h-full rounded-full bar-animate ${color}`} style={{ width: `${w}%` }} />
      </div>
      <span className="text-sm font-medium text-slate-700 text-right">{value}</span>
    </div>
  )
}

export default function ScoreGauge({ score }) {
  const overall = score.overall_score || 0
  const [offset, setOffset] = useState(CIRC)
  useEffect(() => {
    setTimeout(() => setOffset(CIRC * (1 - overall / 100)), 200)
  }, [overall])

  const ringColor = overall >= 70 ? '#22c55e' : overall >= 50 ? '#f97316' : '#ef4444'

  const matched = score.matched_skills || []
  const missing = score.missing_skills || []
  const keywords = score.missing_keywords || []

  return (
    <div className="space-y-6">
      {/* Score + bars */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 flex flex-col sm:flex-row gap-8 items-center">
        {/* Circle */}
        <div className="relative w-36 h-36 shrink-0">
          <svg className="w-36 h-36 -rotate-90" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="54" fill="none" stroke="#f1f5f9" strokeWidth="10" />
            <circle cx="60" cy="60" r="54" fill="none" stroke={ringColor} strokeWidth="10"
              strokeLinecap="round" strokeDasharray={CIRC}
              strokeDashoffset={offset} className="ring-fill" />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-4xl font-extrabold text-slate-900">{overall}</span>
            <span className="text-xs text-slate-400">/100</span>
          </div>
        </div>

        {/* Bars */}
        <div className="flex-1 w-full space-y-3">
          <Bar label="Skills"     value={score.skills_score     || 0} color="bg-blue-500" />
          <Bar label="Experience" value={score.experience_score || 0} color="bg-purple-500" />
          <Bar label="Education"  value={score.education_score  || 0} color="bg-green-500" />
          <Bar label="Keywords"   value={score.keyword_score    || 0} color="bg-amber-400" />
        </div>
      </div>

      {/* Skills gap */}
      <div className="grid sm:grid-cols-2 gap-4">
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Matched Skills</p>
          <div className="flex flex-wrap gap-2">
            {matched.length ? matched.map(s => (
              <span key={s} className="text-xs bg-green-50 text-green-700 border border-green-200 px-2 py-1 rounded-full">{s}</span>
            )) : <span className="text-slate-400 text-sm">None matched</span>}
          </div>
        </div>
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Missing Skills</p>
          <div className="flex flex-wrap gap-2">
            {missing.length ? missing.map(s => (
              <span key={s} className="text-xs bg-red-50 text-red-700 border border-red-200 px-2 py-1 rounded-full">{s}</span>
            )) : <span className="text-green-600 text-sm">No gaps!</span>}
          </div>
        </div>
      </div>

      {/* ATS keywords missing */}
      {keywords.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-5">
          <p className="text-xs font-semibold text-amber-700 uppercase tracking-wider mb-3">Missing ATS Keywords</p>
          <div className="flex flex-wrap gap-2">
            {keywords.map(k => (
              <span key={k} className="text-xs bg-white text-amber-700 border border-amber-300 px-2 py-1 rounded-full">{k}</span>
            ))}
          </div>
        </div>
      )}

      {/* Experience gap */}
      {score.experience_gap && (
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Experience Gap</p>
          <p className="text-sm text-slate-700">{score.experience_gap}</p>
        </div>
      )}
    </div>
  )
}
