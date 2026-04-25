import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import NavBar    from './components/NavBar'
import Landing   from './pages/Landing'
import Login     from './pages/Login'
import Analyse   from './pages/Analyse'
import Results   from './pages/Results'
import Alerts    from './pages/Alerts'
import Admin     from './pages/Admin'

function ProtectedRoute({ children, adminOnly = false }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex items-center justify-center h-64 text-slate-400">Loading...</div>
  if (!user) return <Navigate to="/login" replace />
  if (adminOnly && user.role !== 'admin') return <Navigate to="/" replace />
  return children
}

function AppRoutes() {
  return (
    <div className="min-h-screen bg-slate-50">
      <NavBar />
      <main>
        <Routes>
          <Route path="/"                   element={<Landing />} />
          <Route path="/login"              element={<Login />} />
          <Route path="/analyse"            element={<Analyse />} />
          <Route path="/results/:sessionId" element={<Results />} />
          <Route path="/alerts"             element={<ProtectedRoute><Alerts /></ProtectedRoute>} />
          <Route path="/admin"              element={<ProtectedRoute adminOnly><Admin /></ProtectedRoute>} />
          <Route path="*"                   element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  )
}
