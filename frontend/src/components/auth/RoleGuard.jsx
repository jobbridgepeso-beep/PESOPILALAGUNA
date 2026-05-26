import { Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'

/**
 * RoleGuard — enforces role-based access control on protected routes.
 *
 * If the authenticated user's role is not in `allowedRoles`, they are
 * redirected to their own role dashboard. A 403 UI is shown briefly
 * before the redirect (handled via the Navigate component).
 *
 * Requirement 3.2
 *
 * @param {string[]} allowedRoles - Roles permitted to access the wrapped route.
 */
function RoleGuard({ children, allowedRoles = [] }) {
  const role = useAuthStore((state) => state.role)

  if (!role || !allowedRoles.includes(role)) {
    // Redirect to the user's own dashboard rather than a blank 403 page
    const dashboardPath = role ? `/${role}/dashboard` : '/login'
    return <Navigate to={dashboardPath} replace />
  }

  return children
}

export default RoleGuard
