import { Zap, Target, Clock } from 'lucide-react'

const IMPACT_STYLE = {
  critical: 'bg-red-100 text-red-700',
  high:     'bg-orange-100 text-orange-700',
  medium:   'bg-amber-100 text-amber-700',
  low:      'bg-slate-100 text-slate-500',
}

export default function ActionPlan({ plan }) {
  const actions    = plan.priority_actions || []
  const quickWins  = plan.quick_wins       || []
  const timeline   = plan.timeline_weeks
  const motivation = plan.motivational_close

  if (!actions.length && !quickWins.length) return (
    <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-400">
      Action plan unavailable.
    </div>
  )

  return (
    <div className="space-y-5">
      {/* Timeline */}
      {timeline && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 flex items-center gap-3">
          <Clock size={18} className="text-blue-600 shrink-0" />
          <p className="text-blue-800 text-sm font-medium">
            Estimated <strong>{timeline} weeks</strong> to become competitive for this role if all actions are completed.
          </p>
        </div>
      )}

      {/* Quick wins */}
      {quickWins.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center gap-2 mb-4">
            <Zap size={16} className="text-amber-500" />
            <h3 className="font-semibold text-slate-900 text-sm">Quick Wins — do today</h3>
          </div>
          <div className="space-y-2">
            {quickWins.map((w, i) => (
              <div key={i} className="flex items-start gap-3 text-sm text-slate-700 py-2 border-b border-slate-50 last:border-0">
                <span className="bg-amber-100 text-amber-600 text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center shrink-0 mt-0.5">
                  {i + 1}
                </span>
                {w}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Priority actions */}
      <div className="space-y-3">
        <h3 className="font-semibold text-slate-700 text-sm flex items-center gap-2">
          <Target size={15} /> Priority Actions
        </h3>
        {actions.map((a, i) => (
          <div key={i} className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-slate-400 text-xs font-bold w-6">#{a.rank}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full font-semibold uppercase tracking-wide ${IMPACT_STYLE[a.impact?.toLowerCase()] || IMPACT_STYLE.low}`}>
                {a.impact}
              </span>
              <span className="text-xs text-slate-400 ml-auto">{a.effort}</span>
            </div>
            <p className="text-sm text-slate-800 leading-relaxed">{a.action}</p>
            {(a.resources || []).length > 0 && (
              <div className="flex flex-wrap gap-1 mt-3">
                {a.resources.map(r => (
                  <span key={r} className="text-xs bg-slate-100 text-slate-500 px-2 py-1 rounded">{r}</span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Resume rewrites */}
      {(plan.resume_rewrites || []).length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold text-slate-900 text-sm mb-4">Resume Rewrites</h3>
          <div className="space-y-4">
            {plan.resume_rewrites.map((r, i) => (
              <div key={i}>
                <p className="text-xs font-semibold text-slate-400 uppercase mb-2">{r.section}</p>
                {r.issue && <p className="text-xs text-red-600 bg-red-50 rounded p-2 mb-2">Issue: {r.issue}</p>}
                {r.improved && (
                  <div className="bg-green-50 border border-green-200 rounded p-3">
                    <p className="text-xs text-green-600 font-semibold mb-1">Improved version:</p>
                    <p className="text-sm text-green-800">{r.improved}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Motivational close */}
      {motivation && (
        <div className="bg-slate-50 border border-slate-200 rounded-xl p-4">
          <p className="text-sm text-slate-600 italic">"{motivation}"</p>
        </div>
      )}
    </div>
  )
}
