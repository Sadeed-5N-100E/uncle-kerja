import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Target, Bell, LayoutDashboard, Shield, LogOut, LogIn } from 'lucide-react'

export default function NavBar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const { pathname } = useLocation()

  const navLink = (to, icon, label) => {
    const active = pathname === to
    return (
      <Link to={to}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors
          ${active ? 'bg-blue-50 text-blue-700' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'}`}>
        {icon}
        <span className="hidden sm:inline">{label}</span>
      </Link>
    )
  }

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-bold text-slate-900">
          <Target size={20} className="text-orange-500" />
          <span>Career Copilot <span className="text-orange-500">MY</span></span>
        </Link>

        <nav className="flex items-center gap-1">
          {navLink('/analyse', <LayoutDashboard size={15} />, 'Analyse')}
          {user && navLink('/alerts', <Bell size={15} />, 'Job Alerts')}
          {user?.role === 'admin' && navLink('/admin', <Shield size={15} />, 'Admin')}
        </nav>

        <div className="flex items-center gap-2">
          {user ? (
            <>
              <span className="text-xs text-slate-500 hidden sm:inline">
                {user.email} · <span className="capitalize">{user.role}</span>
              </span>
              <button onClick={() => { logout(); navigate('/login') }}
                className="flex items-center gap-1 text-sm text-slate-500 hover:text-slate-800 px-2 py-1 rounded transition-colors">
                <LogOut size={14} /> <span className="hidden sm:inline">Sign out</span>
              </button>
            </>
          ) : (
            <Link to="/login"
              className="flex items-center gap-1 text-sm bg-blue-600 text-white px-3 py-1.5 rounded-md hover:bg-blue-700 transition-colors">
              <LogIn size={14} /> Sign in
            </Link>
          )}
        </div>
      </div>
    </header>
  )
}
