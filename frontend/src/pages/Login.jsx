import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Eye, EyeOff } from 'lucide-react'

// Two accounts only:
//   Admin  = tomleeatwork@gmail.com  — sees all sessions, inbox, system stats
//   User   = teamusm20@gmail.com     — sees only their own history and alerts
// Local shortcuts (offline, instant):
//   admin@demo.local / Admin@1234
//   user@demo.local  / User@1234
const DEMO_ACCOUNTS = [
  {
    label:    'Admin (Tom Lee)',
    email:    'admin@demo.local',
    password: 'Admin@1234',
    hint:     'All sessions · Inbox · System',
    badge:    'border-purple-300 text-purple-700',
  },
  {
    label:    'User (Team USM)',
    email:    'user@demo.local',
    password: 'User@1234',
    hint:     'Own history · Alerts only',
    badge:    'border-blue-300 text-blue-700',
  },
]

export default function Login() {
  const { login } = useAuth()
  const navigate  = useNavigate()
  const [email,   setEmail]   = useState('')
  const [pw,      setPw]      = useState('')
  const [showPw,  setShowPw]  = useState(false)
  const [error,   setError]   = useState('')
  const [loading, setLoading] = useState(false)

  const doLogin = async (e, pw_, email_) => {
    e?.preventDefault()
    const em = email_ ?? email
    const p  = pw_    ?? pw
    setError(''); setLoading(true)
    try {
      const user = await login(em, p)
      navigate(user.role === 'admin' ? '/admin' : '/')
    } catch (err) {
      setError(err.message || 'Login failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <img
            src="/assets/Uncle-kerja-logo.png"
            alt="Uncle Kerja"
            className="h-16 object-contain mx-auto mb-3"
          />
          <p className="text-slate-500 text-sm">AI-Powered Career Intelligence for Malaysia</p>
        </div>

        {/* Card */}
        <div className="rounded-2xl border border-slate-200 bg-white p-7">
          <h2 className="text-lg font-semibold text-slate-900 mb-5">Sign in to your account</h2>

          <form onSubmit={doLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">Email</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)}
                placeholder="you@email.com" required
                className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2.5
                           text-sm text-slate-900 placeholder-slate-400
                           focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500/30" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-600 mb-1">Password</label>
              <div className="relative">
                <input type={showPw ? 'text' : 'password'} value={pw} onChange={e => setPw(e.target.value)}
                  placeholder="••••••••" required
                  className="w-full bg-white border border-slate-200 rounded-lg px-3 py-2.5 pr-10
                             text-sm text-slate-900 placeholder-slate-400
                             focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500/30" />
                <button type="button" onClick={() => setShowPw(!showPw)}
                  className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-700">
                  {showPw ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-3 py-2 rounded-lg">
                {error}
              </div>
            )}

            <button type="submit" disabled={loading}
              className="w-full bg-purple-600 hover:bg-purple-500 disabled:opacity-50
                         text-white font-semibold py-2.5 rounded-lg transition-colors text-sm">
              {loading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>

          {/* Demo accounts */}
          <div className="mt-6 pt-5 border-t border-slate-100">
            <p className="text-xs text-slate-400 text-center mb-3">Demo accounts — click to log in instantly</p>
            <div className="grid grid-cols-2 gap-2">
              {DEMO_ACCOUNTS.map(acc => (
                <button key={acc.email} onClick={() => doLogin(null, acc.password, acc.email)}
                  disabled={loading}
                  className={`flex flex-col items-start gap-0.5 bg-slate-50 border rounded-xl p-3
                              hover:bg-slate-100 transition-all text-left ${acc.badge}`}>
                  <span className="text-xs font-semibold text-slate-800">{acc.label}</span>
                  <span className="text-xs text-slate-400">{acc.hint}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Z AI */}
          <div className="mt-5 flex items-center justify-center gap-2 opacity-50">
            <img src="/assets/Z-AI-logo.png" alt="Z AI"
                 className="w-4 h-4 object-contain brightness-0" />
            <span className="text-xs text-slate-500">Powered by Z AI GLM-5.1</span>
          </div>
        </div>
      </div>
    </div>
  )
}
