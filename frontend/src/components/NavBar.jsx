import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Bell, LayoutDashboard, Shield, LogOut, LogIn, Clock } from 'lucide-react'

export default function NavBar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const { pathname } = useLocation()

  const navLink = (to, icon, label) => {
    const active = pathname === to || pathname.startsWith(to + '/')
    return (
      <Link to={to}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors
          ${active
            ? 'bg-purple-100 text-purple-700'
            : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100'
          }`}>
        {icon}
        <span className="hidden sm:inline">{label}</span>
      </Link>
    )
  }

  return (
    <header className="bg-white/95 backdrop-blur border-b border-slate-200 sticky top-0 z-40">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link to="/" className="flex items-center shrink-0">
          <img
            src="/assets/Uncle-kerja-logo.png"
            alt="Uncle Kerja"
            className="h-10 object-contain"
          />
        </Link>

        <nav className="flex items-center gap-1">
          {navLink('/analyse', <LayoutDashboard size={15} />, 'Analyse')}
          {user && navLink('/history', <Clock size={15} />, 'History')}
          {user && navLink('/alerts', <Bell size={15} />, 'Alerts')}
          {user?.role === 'admin' && navLink('/admin', <Shield size={15} />, 'Admin')}
        </nav>

        <div className="flex items-center gap-2">
          {user ? (
            <>
              <span className="text-xs text-slate-500 hidden sm:inline truncate max-w-[160px]">
                {user.email}
              </span>
              <button onClick={() => { logout(); navigate('/login') }}
                className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-900
                           px-2 py-1 rounded transition-colors">
                <LogOut size={14} />
                <span className="hidden sm:inline">Sign out</span>
              </button>
            </>
          ) : (
            <Link to="/login"
              className="flex items-center gap-1.5 text-sm font-semibold px-4 py-1.5
                         rounded-lg bg-purple-600 hover:bg-purple-500 text-white transition-colors">
              <LogIn size={14} /> Sign In
            </Link>
          )}
        </div>
      </div>
    </header>
  )
}
