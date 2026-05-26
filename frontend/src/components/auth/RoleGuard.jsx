import { Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'

/**
 * RoleGuard — enforces role-based access control on protected routes.
 * Requirement 3.2
 */
function RoleGuard({ children, allowedRoles = [] }) {
  const role = useAuthStore((state) => state.role)

  if (!role || !allowedRoles.includes(role)) {
    const dashboardPath = role ? `/${role}/dashboard` : '/login'
    return <Navigate to={dashboardPath} replace />
  }

  return children
}

export default RoleGuard
