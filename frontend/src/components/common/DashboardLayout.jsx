import { Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { logout } from '@/api/authApi'
import toast from 'react-hot-toast'

const NAV = {
  jobseeker: [
    { to: '/jobseeker/dashboard', label: 'Dashboard' },
  ],
  employer: [{ to: '/employer/dashboard', label: 'Dashboard' }],
  staff: [{ to: '/staff/dashboard', label: 'Dashboard' }],
  admin: [{ to: '/admin/dashboard', label: 'Dashboard' }],
}

export default function DashboardLayout({ children, title }) {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, role, clearAuth } = useAuthStore()
  const links = NAV[role] || []

  const handleLogout = async () => {
    try {
      await logout()
    } catch {
      /* cookie may already be cleared */
    }
    clearAuth()
    toast.success('Logged out')
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="w-56 border-r border-slate-200 bg-white p-4">
        <p className="mb-6 text-lg font-bold text-blue-700">JobBridge</p>
        <p className="mb-4 text-xs uppercase tracking-wide text-slate-500">PESO Pila</p>
        <nav className="space-y-1">
          {links.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className={`block rounded-md px-3 py-2 text-sm ${
                location.pathname === item.to
                  ? 'bg-blue-100 font-medium text-blue-800'
                  : 'text-slate-700 hover:bg-slate-100'
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
          <h1 className="text-xl font-semibold text-slate-800">{title}</h1>
          <div className="flex items-center gap-4">
            <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-medium capitalize text-blue-800">
              {role}
            </span>
            <span className="text-sm text-slate-600">{user?.email}</span>
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-md bg-slate-800 px-3 py-1.5 text-sm text-white hover:bg-slate-700"
            >
              Logout
            </button>
          </div>
        </header>
        <main className="flex-1 p-6">{children}</main>
      </div>
    </div>
  )
}
