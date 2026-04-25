import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { api } from '../lib/api'
import {
  Target, ChevronRight, Sparkles, Flame, MapPin, Briefcase,
  Mail, Bot, BarChart3, Clock, ExternalLink, ArrowRight,
} from 'lucide-react'

// ── Hero Slider ───────────────────────────────────────────────────────────────
const SLIDES = [
  {
    tag:   'AI-Powered Resume Intelligence',
    title: 'Know exactly where you stand.',
    sub:   'Upload your resume. Paste a job description. Get a calibrated score across skills, experience, education, and ATS keywords — in under 2 minutes.',
    accent: 'bg-blue-600',
    img:  'score',
  },
  {
    tag:   'Brutally Honest Feedback',
    title: 'Your resume, roasted.',
    sub:   'No sugar-coating. Our AI gives you the kind of feedback a senior recruiter would give — specific, sharp, and actionable. Because honesty gets you hired.',
    accent: 'bg-orange-500',
    img:  'roast',
  },
  {
    tag:   'Real Job Matches',
    title: 'Jobs that actually fit you.',
    sub:   'Live listings from Google Jobs, filtered for Malaysia. Daily alerts sent straight to your inbox. Reply to the email to refine your search.',
    accent: 'bg-emerald-600',
    img:  'jobs',
  },
]

function SlideVisual({ type }) {
  if (type === 'score') return (
    <div className="bg-white rounded-2xl p-5 shadow-lg border border-slate-200 max-w-xs">
      <div className="flex items-center gap-3 mb-4">
        <div className="relative w-16 h-16">
          <svg viewBox="0 0 60 60" className="w-16 h-16 -rotate-90">
            <circle cx="30" cy="30" r="24" fill="none" stroke="#f1f5f9" strokeWidth="5"/>
            <circle cx="30" cy="30" r="24" fill="none" stroke="#f97316" strokeWidth="5"
              strokeDasharray="150" strokeDashoffset="60" strokeLinecap="round"/>
          </svg>
          <div className="absolute inset-0 flex items-center justify-center text-xl font-bold text-slate-900">64</div>
        </div>
        <div>
          <div className="text-sm font-bold text-slate-900">Partial Fit</div>
          <div className="text-xs text-slate-400">out of 100</div>
        </div>
      </div>
      {[['Skills', 65, 'bg-blue-500'], ['Experience', 50, 'bg-purple-500'], ['Keywords', 72, 'bg-amber-400']].map(([l,v,c]) => (
        <div key={l} className="flex items-center gap-2 mb-1.5">
          <span className="text-xs text-slate-400 w-20">{l}</span>
          <div className="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div className={`h-full ${c} rounded-full`} style={{width:`${v}%`}}/>
          </div>
          <span className="text-xs font-medium text-slate-600 w-6">{v}</span>
        </div>
      ))}
    </div>
  )
  if (type === 'roast') return (
    <div className="bg-orange-950 rounded-2xl p-5 shadow-lg max-w-xs">
      <div className="flex items-center gap-2 mb-3">
        <Flame size={18} className="text-orange-400"/>
        <span className="text-orange-300 font-semibold text-sm">The Roast</span>
        <span className="ml-auto text-xl">🔥🔥</span>
      </div>
      <p className="text-orange-100 text-sm leading-relaxed mb-3 italic">
        "You're applying to a Senior role with a Junior resume — that's like showing up to a marathon in flip-flops."
      </p>
      <div className="bg-green-900/50 rounded-lg p-2.5">
        <p className="text-xs text-green-300 font-semibold mb-1">Silver Lining</p>
        <p className="text-green-200 text-xs">You DO know Python, REST APIs and SQL. That's a real foundation.</p>
      </div>
    </div>
  )
  return (
    <div className="bg-white rounded-2xl p-4 shadow-lg border border-slate-200 max-w-xs space-y-2">
      {[
        { c: 'Shopee', t: 'Junior Backend Developer', s: 'RM4,000–RM6,000/month', m: 82 },
        { c: 'Revenue Monster', t: 'Software Developer', s: 'RM3,500–RM5,500/month', m: 85 },
        { c: 'TNG Digital', t: 'Backend Engineer', s: 'RM3,800–RM5,500/month', m: 75 },
      ].map(j => (
        <div key={j.c} className="flex items-center gap-3 p-2.5 rounded-xl bg-slate-50">
          <div className={`text-sm font-bold ${j.m>=80?'text-green-600':'text-orange-500'}`}>{j.m}%</div>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-semibold text-slate-800 truncate">{j.t}</div>
            <div className="text-xs text-slate-400">{j.c} · {j.s}</div>
          </div>
        </div>
      ))}
    </div>
  )
}

function HeroSlider() {
  const [idx, setIdx] = useState(0)
  useEffect(() => {
    const t = setInterval(() => setIdx(i => (i + 1) % SLIDES.length), 4500)
    return () => clearInterval(t)
  }, [])
  const s = SLIDES[idx]
  return (
    <section className="relative bg-slate-900 overflow-hidden">
      {/* Gradient bg */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900"/>
      <div className="absolute top-0 right-0 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl"/>
      <div className="absolute bottom-0 left-0 w-80 h-80 bg-orange-500/10 rounded-full blur-3xl"/>

      <div className="relative max-w-6xl mx-auto px-4 py-20 sm:py-28 flex flex-col lg:flex-row items-center gap-12">
        {/* Text */}
        <div className="flex-1 text-center lg:text-left">
          <span className={`inline-block text-xs font-semibold px-3 py-1 rounded-full text-white mb-4 ${s.accent}`}>
            {s.tag}
          </span>
          <h1 className="text-4xl sm:text-5xl font-extrabold text-white leading-tight mb-4">
            {s.title}
          </h1>
          <p className="text-slate-400 text-lg max-w-xl mb-8 leading-relaxed">{s.sub}</p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center lg:justify-start">
            <Link to="/analyse"
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold px-6 py-3 rounded-xl transition-all hover:scale-105">
              Analyse My Resume <ChevronRight size={18}/>
            </Link>
            <Link to="/login"
              className="inline-flex items-center gap-2 bg-white/10 hover:bg-white/20 text-white font-semibold px-6 py-3 rounded-xl transition-all border border-white/10">
              Sign In
            </Link>
          </div>
        </div>

        {/* Visual */}
        <div className="shrink-0 flex flex-col items-center gap-4">
          <SlideVisual type={s.img}/>
          {/* Dots */}
          <div className="flex gap-2">
            {SLIDES.map((_, i) => (
              <button key={i} onClick={() => setIdx(i)}
                className={`h-1.5 rounded-full transition-all ${i===idx ? `w-6 ${s.accent}` : 'w-1.5 bg-white/30'}`}/>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

// ── Agent Showcase ────────────────────────────────────────────────────────────
const AGENTS = [
  { icon: <BarChart3 size={20}/>, name: 'Score Agent',   desc: 'Grades your resume across 4 dimensions with a weighted rubric. No guessing — just data.',    color: 'text-blue-600 bg-blue-50' },
  { icon: <Flame size={20}/>,     name: 'Roast Agent',   desc: 'Delivers a sharp, specific critique of your resume. Simon Cowell meets HR.',                  color: 'text-orange-600 bg-orange-50' },
  { icon: <MapPin size={20}/>,    name: 'Coach Agent',   desc: 'Turns your gaps into a ranked 6-week action plan with exact courses and fixes.',               color: 'text-purple-600 bg-purple-50' },
  { icon: <Briefcase size={20}/>, name: 'Job Finder',    desc: 'Searches Google Jobs + aidevboard for real Malaysian listings. Real URLs, no placeholders.',   color: 'text-emerald-600 bg-emerald-50' },
  { icon: <Mail size={20}/>,      name: 'Email Agent',   desc: 'Drafts cover letters in English and Bahasa Malaysia. Sends daily job alerts via AgentMail.',   color: 'text-sky-600 bg-sky-50' },
  { icon: <Bot size={20}/>,       name: 'Reply Agent',   desc: 'Reads replies to your job alerts and responds intelligently. Ask for different jobs by email.', color: 'text-rose-600 bg-rose-50' },
]

// ── Feature Cards (Cubes) ─────────────────────────────────────────────────────
function FeatureCard({ to, icon, title, description, cta, gradient }) {
  return (
    <Link to={to} className="group block">
      <div className={`relative rounded-2xl p-8 h-full overflow-hidden transition-all
        hover:scale-[1.02] hover:shadow-xl border border-white/20 ${gradient}`}>
        <div className="relative z-10">
          <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-5 text-white">
            {icon}
          </div>
          <h3 className="text-2xl font-bold text-white mb-3">{title}</h3>
          <p className="text-white/80 text-sm leading-relaxed mb-6">{description}</p>
          <span className="inline-flex items-center gap-2 text-white font-semibold text-sm
            group-hover:gap-3 transition-all">
            {cta} <ArrowRight size={16}/>
          </span>
        </div>
      </div>
    </Link>
  )
}

// ── Recent Job Emails ─────────────────────────────────────────────────────────
function RecentEmails() {
  const [emails,  setEmails]  = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.jobEmails().then(d => setEmails(d.emails || [])).catch(()=>{}).finally(()=>setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex justify-center py-8">
      <div className="animate-spin w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full"/>
    </div>
  )
  if (!emails.length) return (
    <div className="text-center py-8">
      <Mail size={32} className="text-slate-300 mx-auto mb-2"/>
      <p className="text-slate-400 text-sm">No job alert emails yet.</p>
      <Link to="/analyse" className="text-blue-600 text-sm hover:underline mt-1 inline-block">
        Analyse your resume to get started →
      </Link>
    </div>
  )

  return (
    <div className="space-y-3">
      {emails.map((m, i) => (
        <div key={i} className="flex items-center gap-4 p-4 bg-white rounded-xl border border-slate-200 hover:border-slate-300 transition-colors">
          <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center shrink-0">
            <Mail size={16} className="text-blue-600"/>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-slate-800 truncate">{m.subject || '(no subject)'}</p>
            <p className="text-xs text-slate-400 mt-0.5 flex items-center gap-1">
              <Clock size={11}/>
              {m.created_at ? new Date(m.created_at).toLocaleDateString('en-MY', {
                day:'numeric', month:'short', hour:'2-digit', minute:'2-digit'}) : '—'}
            </p>
          </div>
          <Link to="/alerts" className="text-blue-600 hover:text-blue-800 shrink-0">
            <ExternalLink size={14}/>
          </Link>
        </div>
      ))}
      <div className="text-center pt-2">
        <Link to="/alerts" className="text-sm text-blue-600 hover:underline">
          Manage all alerts →
        </Link>
      </div>
    </div>
  )
}

// ── Landing page ──────────────────────────────────────────────────────────────
export default function Landing() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-slate-50">
      <HeroSlider/>

      {/* Agent showcase */}
      <section className="max-w-6xl mx-auto px-4 py-20">
        <div className="text-center mb-12">
          <span className="text-xs font-semibold text-blue-600 uppercase tracking-widest">How it works</span>
          <h2 className="text-3xl font-bold text-slate-900 mt-2">Six AI agents, one mission</h2>
          <p className="text-slate-500 mt-2 max-w-xl mx-auto">
            Each agent specialises in one thing. They run in parallel — your full analysis in under 90 seconds.
          </p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {AGENTS.map(a => (
            <div key={a.name} className="bg-white rounded-2xl border border-slate-200 p-6 hover:border-slate-300 hover:shadow-sm transition-all">
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center mb-4 ${a.color}`}>
                {a.icon}
              </div>
              <h3 className="font-semibold text-slate-900 mb-2">{a.name}</h3>
              <p className="text-sm text-slate-500 leading-relaxed">{a.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Feature cubes */}
      <section className="max-w-6xl mx-auto px-4 pb-20">
        <div className="grid md:grid-cols-2 gap-6">
          <FeatureCard
            to="/analyse"
            icon={<Flame size={22}/>}
            title="Resume Roast"
            description="Upload your resume and get brutally honest, specific feedback from an AI trained on thousands of job descriptions. Score, roast, fix — all in one flow."
            cta="Roast my resume"
            gradient="bg-gradient-to-br from-orange-500 to-orange-700"
          />
          <FeatureCard
            to={user ? '/alerts' : '/login'}
            icon={<Mail size={22}/>}
            title="Job Email Alerts"
            description="Daily job matches delivered to your inbox. Reply to any alert to ask for different roles or locations. The AI reads your reply and responds within minutes."
            cta={user ? 'View my alerts' : 'Sign in to subscribe'}
            gradient="bg-gradient-to-br from-blue-600 to-blue-800"
          />
        </div>
      </section>

      {/* Recent emails — logged-in only */}
      {user && (
        <section className="max-w-2xl mx-auto px-4 pb-20">
          <div className="bg-white rounded-2xl border border-slate-200 p-6">
            <div className="flex items-center gap-2 mb-5">
              <Mail size={18} className="text-blue-600"/>
              <h2 className="font-semibold text-slate-900">Recent Job Alerts</h2>
              <span className="ml-auto text-xs text-slate-400">sent from {user.email}</span>
            </div>
            <RecentEmails/>
          </div>
        </section>
      )}
    </div>
  )
}
