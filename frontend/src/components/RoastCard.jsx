import { Flame } from 'lucide-react'

export default function RoastCard({ roast }) {
  if (!roast.opening_roast) return (
    <div className="bg-white rounded-xl border border-slate-200 p-8 text-center text-slate-400">
      Roast data unavailable.
    </div>
  )

  const emojis = roast.emoji_rating || '🔥'

  return (
    <div className="space-y-4">
      {/* Rating */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 flex items-center gap-3">
        <Flame size={20} className="text-orange-500" />
        <div>
          <span className="text-lg font-bold text-slate-900">Resume Rating</span>
          <span className="text-2xl ml-3">{emojis}</span>
        </div>
      </div>

      {/* Opening */}
      <div className="bg-orange-50 border border-orange-200 rounded-xl p-5">
        <p className="text-orange-900 font-semibold text-base leading-relaxed">
          "{roast.opening_roast}"
        </p>
      </div>

      {/* Detailed sections */}
      {[
        { label: 'Skills Assessment', text: roast.skills_roast,     bg: 'bg-red-50 border-red-200',   text_: 'text-red-800' },
        { label: 'Experience Review', text: roast.experience_roast, bg: 'bg-amber-50 border-amber-200', text_: 'text-amber-800' },
        { label: 'Presentation',      text: roast.formatting_roast, bg: 'bg-slate-50 border-slate-200', text_: 'text-slate-700' },
      ].map(({ label, text, bg, text_ }) => text && (
        <div key={label} className={`rounded-xl border p-5 ${bg}`}>
          <p className={`text-xs font-semibold uppercase tracking-wider mb-2 opacity-60 ${text_}`}>{label}</p>
          <p className={`text-sm leading-relaxed ${text_}`}>{text}</p>
        </div>
      ))}

      {/* Silver lining */}
      {roast.silver_lining && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-5">
          <p className="text-xs font-semibold text-green-600 uppercase tracking-wider mb-2">Silver Lining</p>
          <p className="text-green-800 text-sm leading-relaxed italic">"{roast.silver_lining}"</p>
        </div>
      )}

      {/* Closing */}
      {roast.closing_line && (
        <div className="bg-slate-900 rounded-xl p-5">
          <p className="text-white font-medium text-sm leading-relaxed">"{roast.closing_line}"</p>
        </div>
      )}
    </div>
  )
}
