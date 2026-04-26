import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { api } from '../lib/api'
import heroCube from '../assets/hero.png'
import { ChevronRight, ArrowRight, Clock, ExternalLink } from 'lucide-react'

// ── Slide data ────────────────────────────────────────────────────────────────
const SLIDES = [
  {
    tag:    'AI-Powered Resume Intelligence',
    title:  'Know exactly where you stand.',
    subBM:  'Semak resume awak sekarang',
    sub:    'Upload your resume, paste a job description. Get a calibrated score across skills, experience, education, and ATS keywords — in under 2 minutes.',
    accent: '#7e14ff',
  },
  {
    tag:    'Brutally Honest Feedback',
    title:  'Your resume, roasted.',
    subBM:  'Tiada sorok-sorok',
    sub:    "No sugar-coating. Our AI gives you the kind of feedback a senior recruiter would — specific, sharp, and actionable. Because honesty gets you hired.",
    accent: '#f97316',
  },
  {
    tag:    'Real Malaysian Job Matches',
    title:  'Jobs that actually fit you.',
    subBM:  'Kerja sebenar, bukan placeholder',
    sub:    'Live listings from Google Jobs, filtered for Malaysia. Daily alerts to your inbox. Reply to the email to change location, role, or stop anytime.',
    accent: '#059669',
  },
]

// ── 6 Agent mascot cards ──────────────────────────────────────────────────────
const AGENTS = [
  {
    mascot: '/assets/score-agent-mascot.png',
    name:   'Score Agent',
    tagBM:  'Penggredan Resume',
    desc:   'Grades your resume across 4 dimensions — skills, experience, education, and ATS keywords — with a weighted rubric.',
    color:  '#3b82f6', bgGlow: '#3b82f618',
  },
  {
    mascot: '/assets/roast-agent-mascot.png',
    name:   'Roast Agent',
    tagBM:  'Kritikan Jujur',
    desc:   'Delivers a sharp, specific critique. Simon Cowell meets HR. No filler — only the facts that matter.',
    color:  '#f97316', bgGlow: '#f9731618',
  },
  {
    mascot: '/assets/coach-agent-mascot.png',
    name:   'Coach Agent',
    tagBM:  'Pelan Tindakan',
    desc:   'Turns your gaps into a ranked 6-week action plan with HRDF-claimable courses and specific resume rewrites.',
    color:  '#a855f7', bgGlow: '#a855f718',
  },
  {
    mascot: '/assets/Job-finder-mascot.png',
    name:   'Job Finder',
    tagBM:  'Pencari Kerja',
    desc:   'Searches Google Jobs and aidevboard for live Malaysian listings. Real URLs, posted this week.',
    color:  '#10b981', bgGlow: '#10b98118',
  },
  {
    mascot: '/assets/email-agent-mascot.png',
    name:   'Email Agent',
    tagBM:  'Ejen Emel',
    desc:   'Drafts cover letters in English AND Bahasa Malaysia (Surat Permohonan Pekerjaan). Sends daily job alerts via usm.z.ai@agentmail.to.',
    color:  '#0ea5e9', bgGlow: '#0ea5e918',
  },
  {
    mascot: '/assets/reply-agent-mascot.png',
    name:   'Reply Agent',
    tagBM:  'Ejen Balas',
    desc:   'Reads replies to your job alert emails and responds intelligently. Just reply to change your search.',
    color:  '#ec4899', bgGlow: '#ec489918',
  },
]

const MY_FEATURES = [
  { flag: '🇲🇾', title: 'HRDF / HRD Corp Courses',  desc: 'Coach Agent recommends HRDF-claimable training to close your skill gaps — subsidised for Malaysian workers.' },
  { flag: '🏦',  title: 'EPF & SOCSO Awareness',     desc: 'Job descriptions are assessed for EPF registration status — important for long-term financial security.' },
  { flag: '🏙️', title: 'Malaysian Job Hubs',         desc: 'Specialised search for KL, Petaling Jaya, Cyberjaya, Penang, and other key Malaysian tech cities.' },
  { flag: '🎓',  title: 'Local University Recognition', desc: 'Score Agent recognises UM, UTM, UiTM, MMU, UTAR and other Malaysian institutions accurately.' },
  { flag: '💬',  title: 'Bilingual Cover Letters',   desc: 'Cover letters drafted in English AND Bahasa Malaysia (Surat Permohonan Pekerjaan formal format).' },
  { flag: '💰',  title: 'MYR Salary Benchmarks',     desc: 'All salary data in Ringgit Malaysia, benchmarked against JobStreet MY and Robert Walters Salary Guide.' },
]

// ── Hero Slider ───────────────────────────────────────────────────────────────
function HeroSlider() {
  const [idx, setIdx] = useState(0)
  useEffect(() => {
    const t = setInterval(() => setIdx(i => (i + 1) % SLIDES.length), 4500)
    return () => clearInterval(t)
  }, [])
  const s = SLIDES[idx]

  return (
    <section className="relative overflow-hidden bg-slate-50">
      <div className="absolute inset-0"
           style={{ background: `radial-gradient(700px at 75% 50%, ${s.accent}12, transparent)` }} />

      <div className="relative max-w-6xl mx-auto px-4 py-16 sm:py-24
                      flex flex-col lg:flex-row items-center gap-10">
        {/* Left */}
        <div className="flex-1 text-center lg:text-left">
          <div className="flex items-center gap-3 justify-center lg:justify-start mb-6">
            <img src="/assets/Uncle-kerja-logo.png" alt="Uncle Kerja" className="h-14 object-contain" />
          </div>

          <span className="inline-block text-xs font-semibold px-3 py-1.5 rounded-full
                           text-slate-700 mb-4 border border-slate-200 bg-slate-100">
            {s.tag}
          </span>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 leading-tight mb-1">
            {s.title}
          </h1>
          <p className="text-purple-600 text-sm italic mb-4">{s.subBM}</p>
          <p className="text-slate-600 text-base max-w-xl mb-8 leading-relaxed">{s.sub}</p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center lg:justify-start">
            <Link to="/analyse"
              className="inline-flex items-center gap-2 text-white font-semibold
                         px-7 py-3 rounded-xl transition-all hover:scale-105"
              style={{ background: s.accent }}>
              Analyse My Resume <ChevronRight size={17} />
            </Link>
            <Link to="/login"
              className="inline-flex items-center gap-2 text-slate-700 font-semibold px-7 py-3
                         rounded-xl transition-all border border-slate-300 hover:bg-slate-100">
              Sign In
            </Link>
          </div>
        </div>

        {/* Right — cube */}
        <div className="shrink-0 flex flex-col items-center gap-5">
          <img src={heroCube} alt="Uncle Kerja"
               className="w-64 sm:w-72 drop-shadow-2xl select-none" draggable={false} />
          <div className="flex gap-2">
            {SLIDES.map((_, i) => (
              <button key={i} onClick={() => setIdx(i)}
                className="h-1.5 rounded-full transition-all duration-300"
                style={{ width: i === idx ? 28 : 8,
                         background: i === idx ? s.accent : 'rgba(0,0,0,0.15)' }} />
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

// ── 6 Agent Cards ─────────────────────────────────────────────────────────────
function AgentCards() {
  return (
    <section className="bg-white max-w-6xl mx-auto px-4 py-20">
      <div className="text-center mb-10">
        <span className="text-xs font-semibold text-purple-600 uppercase tracking-widest">How it works</span>
        <h2 className="text-3xl font-bold text-slate-900 mt-2">6 AI Agents. One Mission.</h2>
        <p className="text-slate-500 mt-2 max-w-xl mx-auto text-sm">
          Each agent specialises in one task. They run sequentially for reliability —
          full analysis in around 90 seconds.
        </p>
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {AGENTS.map(a => (
          <div key={a.name}
            className="relative rounded-2xl overflow-hidden border border-slate-200 bg-white transition-all duration-300
                       hover:scale-[1.02] hover:shadow-lg group cursor-default">
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity"
                 style={{ background: `radial-gradient(250px at 50% 0%, ${a.bgGlow}, transparent)` }} />
            <div className="relative z-10 p-6">
              <div className="flex justify-center mb-4">
                <img src={a.mascot} alt={a.name}
                     className="h-32 w-32 object-contain drop-shadow-lg" />
              </div>
              <div className="text-center mb-2">
                <h3 className="font-bold text-slate-900 text-base">{a.name}</h3>
                <span className="text-xs px-2 py-0.5 rounded-full font-medium"
                      style={{ background: `${a.color}1a`, color: a.color }}>
                  {a.tagBM}
                </span>
              </div>
              <p className="text-xs text-slate-500 leading-relaxed text-center">{a.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

// ── Feature Cubes ─────────────────────────────────────────────────────────────
function FeatureCubes({ user }) {
  return (
    <section className="bg-white max-w-6xl mx-auto px-4 pb-20">
      <div className="grid md:grid-cols-2 gap-5">
        <Link to="/analyse" className="group block">
          <div className="relative rounded-2xl overflow-hidden border h-full transition-all
                          duration-300 hover:scale-[1.02] hover:shadow-lg"
               style={{ background: 'linear-gradient(135deg, #fff8f5 0%, #fff3ed 100%)',
                        borderColor: '#f97316aa' }}>
            <img src={heroCube} alt="" draggable={false}
                 className="absolute -right-10 -bottom-8 w-44 opacity-10 pointer-events-none select-none" />
            <div className="relative z-10 p-7 flex gap-5 items-center">
              <img src="/assets/roast-agent-mascot.png" alt="Roast"
                   className="w-24 h-24 object-contain shrink-0" />
              <div>
                <h3 className="text-xl font-bold text-slate-900 mb-2">Resume Roast</h3>
                <p className="text-orange-700 text-sm mb-3 leading-relaxed">
                  Get a brutally honest, specific score and critique — then a fix plan. No fluff.
                </p>
                <span className="inline-flex items-center gap-1.5 text-orange-600 font-semibold text-sm
                                 group-hover:gap-3 transition-all">
                  Roast my resume <ArrowRight size={14} />
                </span>
              </div>
            </div>
          </div>
        </Link>

        <Link to={user ? '/alerts' : '/login'} className="group block">
          <div className="relative rounded-2xl overflow-hidden border h-full transition-all
                          duration-300 hover:scale-[1.02] hover:shadow-lg"
               style={{ background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
                        borderColor: '#0ea5e9aa' }}>
            <img src={heroCube} alt="" draggable={false}
                 className="absolute -right-10 -bottom-8 w-44 opacity-10 pointer-events-none select-none" />
            <div className="relative z-10 p-7 flex gap-5 items-center">
              <img src="/assets/email-agent-mascot.png" alt="Alerts"
                   className="w-24 h-24 object-contain shrink-0" />
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-xl font-bold text-slate-900">Job Email Alerts</h3>
                </div>
                <p className="text-sky-700 text-sm mb-3 leading-relaxed">
                  Daily matching jobs to your inbox from <strong>usm.z.ai@agentmail.to</strong>. Reply to refine your search anytime.
                </p>
                <span className="inline-flex items-center gap-1.5 text-sky-600 font-semibold text-sm
                                 group-hover:gap-3 transition-all">
                  {user ? 'View my alerts' : 'Sign in to subscribe'} <ArrowRight size={14} />
                </span>
              </div>
            </div>
          </div>
        </Link>
      </div>
    </section>
  )
}

// ── Malaysia features ─────────────────────────────────────────────────────────
function MalaysiaSection() {
  return (
    <section className="bg-white max-w-6xl mx-auto px-4 pb-20">
      <div className="text-center mb-10">
        <span className="text-xs font-semibold text-green-600 uppercase tracking-widest">
          Built for Malaysia
        </span>
        <h2 className="text-2xl font-bold text-slate-900 mt-2">More than a resume checker</h2>
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {MY_FEATURES.map(f => (
          <div key={f.title} className="rounded-xl border border-slate-200 bg-slate-50 p-5 hover:border-slate-300 transition-colors">
            <div className="text-2xl mb-2">{f.flag}</div>
            <h4 className="text-sm font-semibold text-slate-900 mb-1">{f.title}</h4>
            <p className="text-xs text-slate-600 leading-relaxed">{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

// ── Recent job emails (logged-in only) ────────────────────────────────────────
function RecentEmails({ userEmail }) {
  const [emails, setEmails] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.jobEmails(userEmail)
      .then(d => setEmails(d.emails || []))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [userEmail])

  if (loading) return (
    <div className="flex justify-center py-6">
      <div className="animate-spin w-5 h-5 border-2 border-purple-500 border-t-transparent rounded-full" />
    </div>
  )
  if (!emails.length) return (
    <div className="text-center py-6">
      <img src="/assets/reply-agent-mascot.png" alt=""
           className="w-16 h-16 object-contain mx-auto mb-2 opacity-40" />
      <p className="text-slate-500 text-sm">No job alert emails yet.</p>
      <Link to="/analyse" className="text-purple-600 hover:text-purple-700 text-xs mt-1 inline-block">
        Analyse your resume to start receiving alerts →
      </Link>
    </div>
  )

  return (
    <div className="space-y-2">
      {emails.map((m, i) => (
        <div key={i}
          className="flex items-center gap-3 px-4 py-3 rounded-xl
                     bg-slate-50 border border-slate-200 hover:border-purple-400/50 transition-colors">
          <img src="/assets/gmail-logo.png" alt="Gmail"
               className="w-7 h-7 object-contain shrink-0" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-800 truncate">{m.subject || '(no subject)'}</p>
            <p className="text-xs text-slate-500 flex items-center gap-1 mt-0.5">
              <Clock size={10} />
              {m.created_at
                ? new Date(m.created_at).toLocaleString('en-MY', {
                    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
                  })
                : '—'}
            </p>
          </div>
          <Link to="/alerts" className="text-slate-400 hover:text-purple-600 transition-colors shrink-0">
            <ExternalLink size={13} />
          </Link>
        </div>
      ))}
      <div className="text-center pt-1">
        <Link to="/alerts" className="text-xs text-purple-600 hover:text-purple-700 transition-colors">
          Manage all alerts →
        </Link>
      </div>
    </div>
  )
}

// ── Main ──────────────────────────────────────────────────────────────────────
export default function Landing() {
  const { user } = useAuth()

  return (
    <div className="bg-white">
      <HeroSlider />
      <AgentCards />
      <FeatureCubes user={user} />
      <MalaysiaSection />

      {/* Recent emails — only for logged-in users */}
      {user && (
        <section className="max-w-2xl mx-auto px-4 pb-20">
          <div className="rounded-2xl border border-slate-200 bg-white p-6">
            <div className="flex items-center gap-2 mb-4">
              <img src="/assets/gmail-logo.png" alt="Gmail" className="w-5 h-5 object-contain" />
              <h2 className="font-semibold text-slate-900 text-sm">Your Recent Job Alert Emails</h2>
              <span className="ml-auto text-xs text-slate-500">{user.email}</span>
            </div>
            <RecentEmails userEmail={user.email} />
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="border-t border-slate-200 py-10">
        <div className="max-w-6xl mx-auto px-4">
          {/* Powered by Z AI */}
          <div className="flex flex-col items-center mb-8">
            <p className="text-slate-400 text-xs uppercase tracking-widest mb-3">Powered by</p>
            <div className="flex items-center gap-3 bg-slate-50 border border-slate-200 px-6 py-3 rounded-xl">
              <img src="/assets/Z-AI-logo.png" alt="Z AI"
                   className="h-9 w-9 object-contain brightness-0" />
              <div>
                <p className="text-slate-900 font-bold text-lg leading-none">Z AI</p>
                <p className="text-slate-500 text-xs">GLM-5.1 Language Model</p>
              </div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <img src="/assets/Uncle-kerja-logo.png" alt="Uncle Kerja"
                 className="h-8 object-contain" />
            <p className="text-xs text-slate-500 text-center">
              AgentMail · TheirStack · Google Jobs · HRDF Malaysia
            </p>
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-500">usm.z.ai@agentmail.to</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
