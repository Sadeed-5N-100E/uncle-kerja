import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Target, Eye, EyeOff } from 'lucide-react'

const DEMO_ACCOUNTS = [
  { label: 'Admin',       email: 'admin@demo.local', password: 'Admin@1234', badge: 'bg-purple-100 text-purple-700' },
  { label: 'Demo User',   email: 'user@demo.local',  password: 'User@1234',  badge: 'bg-blue-100 text-blue-700' },
]

export default function Login() {
  const { login } = useAuth()
  const navigate  = useNavigate()
  const [email,   setEmail]   = useState('')
  const [pw,      setPw]      = useState('')
  const [showPw,  setShowPw]  = useState(false)
  const [error,   setError]   = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setError(''); setLoading(true)
    try {
      const user = await login(email, pw)
      navigate(user.role === 'admin' ? '/admin' : '/')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const quickLogin = async (acc) => {
    setError(''); setLoading(true)
    try {
      const user = await login(acc.email, acc.password)
      navigate(user.role === 'admin' ? '/admin' : '/')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-orange-500 rounded-xl mb-3">
            <Target size={24} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Career Copilot MY</h1>
          <p className="text-slate-500 text-sm mt-1">AI-powered career intelligence</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
          <h2 className="text-lg font-semibold text-slate-900 mb-6">Sign in to your account</h2>

          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
              <input
                type="email" value={email} onChange={e => setEmail(e.target.value)}
                placeholder="you@example.com" required
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
              <div className="relative">
                <input
                  type={showPw ? 'text' : 'password'} value={pw} onChange={e => setPw(e.target.value)}
                  placeholder="••••••••" required
                  className="w-full border border-slate-300 rounded-lg px-3 py-2 pr-10 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button type="button" onClick={() => setShowPw(!showPw)}
                  className="absolute right-3 top-2.5 text-slate-400 hover:text-slate-600">
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
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-medium py-2.5 rounded-lg transition-colors text-sm">
              {loading ? 'Signing in…' : 'Sign in'}
            </button>
          </form>

          {/* Demo quick-login */}
          <div className="mt-6 pt-6 border-t border-slate-100">
            <p className="text-xs text-slate-400 text-center mb-3">Demo accounts</p>
            <div className="grid grid-cols-2 gap-2">
              {DEMO_ACCOUNTS.map(acc => (
                <button key={acc.email} onClick={() => quickLogin(acc)} disabled={loading}
                  className="flex flex-col items-center gap-1 border border-slate-200 rounded-lg p-3 hover:bg-slate-50 transition-colors text-left">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${acc.badge}`}>
                    {acc.label}
                  </span>
                  <span className="text-xs text-slate-500">{acc.email}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
