import { motion } from 'framer-motion'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import PageMotion from './PageMotion'
import { LayoutDashboard, LogOut, User } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { logout } from '@/api/authApi'
import toast from 'react-hot-toast'
import GovBrand from './GovBrand'
import Badge from '@/components/ui/Badge'
import Button from '@/components/ui/Button'
import { cn } from '@/utils/cn'

const ROLE_LABELS = {
  jobseeker: 'Jobseeker',
  employer: 'Employer',
  staff: 'PESO Staff',
  admin: 'Administrator',
}

const NAV = {
  jobseeker: [{ to: '/jobseeker/dashboard', label: 'Dashboard', icon: LayoutDashboard }],
  employer: [{ to: '/employer/dashboard', label: 'Dashboard', icon: LayoutDashboard }],
  staff: [{ to: '/staff/dashboard', label: 'Dashboard', icon: LayoutDashboard }],
  admin: [{ to: '/admin/dashboard', label: 'Dashboard', icon: LayoutDashboard }],
}

export default function DashboardLayout({ children, title, description }) {
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
    toast.success('You have been signed out.')
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <div className="gov-strip" />
      <div className="gov-strip-navy" />

      <div className="flex flex-1">
        {/* Sidebar */}
        <aside className="hidden w-64 shrink-0 flex-col border-r border-border bg-card lg:flex">
          <div className="border-b border-border px-5 py-6">
            <GovBrand compact />
          </div>
          <nav className="flex-1 space-y-1 p-4" aria-label="Main navigation">
            {links.map((item) => {
              const active = location.pathname === item.to
              const Icon = item.icon
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={cn(
                    'flex items-center gap-3 rounded-md px-4 py-3 text-sm font-medium transition-colors',
                    active
                      ? 'border-l-4 border-gov-gold bg-primary text-primary-foreground pl-3 shadow-sm'
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground',
                  )}
                >
                  <Icon className="h-5 w-5 shrink-0" strokeWidth={1.75} />
                  {item.label}
                </Link>
              )
            })}
          </nav>
          <div className="border-t border-border p-4">
            <p className="px-4 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              PESO Pila, Laguna
            </p>
          </div>
        </aside>

        {/* Main */}
        <div className="flex min-w-0 flex-1 flex-col">
          <header className="sticky top-0 z-10 border-b border-border bg-card/95 backdrop-blur supports-[backdrop-filter]:bg-card/90">
            <div className="flex h-16 items-center justify-between gap-4 px-6 lg:px-8">
              <div className="lg:hidden">
                <GovBrand compact />
              </div>
              <div className="hidden min-w-0 flex-1 lg:block">
                <h1 className="truncate text-lg font-bold text-foreground">{title}</h1>
                {description && (
                  <p className="truncate text-xs text-muted-foreground">{description}</p>
                )}
              </div>
              <div className="flex items-center gap-3 sm:gap-4">
                <Badge variant="gold">{ROLE_LABELS[role] || role}</Badge>
                <div className="hidden items-center gap-2 text-sm text-muted-foreground sm:flex">
                  <User className="h-4 w-4" aria-hidden />
                  <span className="max-w-[180px] truncate">{user?.email}</span>
                </div>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={handleLogout}
                  className="shrink-0"
                >
                  <LogOut className="h-4 w-4" />
                  <span className="hidden sm:inline">Sign out</span>
                </Button>
              </div>
            </div>
          </header>

          <main className="flex-1">
            <div className="page-container">
              <div className="mb-2 lg:hidden">
                <h1 className="text-xl font-bold">{title}</h1>
                {description && (
                  <p className="mt-1 text-sm text-muted-foreground">{description}</p>
                )}
              </div>
              <PageMotion key={location.pathname}>{children}</PageMotion>
            </div>
          </main>

          <footer className="border-t border-border bg-card px-6 py-4 text-center text-xs text-muted-foreground lg:px-8">
            © {new Date().getFullYear()} Public Employment Service Office — Pila, Laguna ·
            JobBridge
          </footer>
        </div>
      </div>
    </div>
  )
}
