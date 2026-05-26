import { Navigate, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'

/**
 * ProtectedRoute — redirects unauthenticated users to /login.
 *
 * Wraps any route that requires a valid session. The current path is
 * preserved in location state so the user can be redirected back after
 * logging in.
 *
 * Requirement 3.1
 */
function ProtectedRoute({ children }) {
  const accessToken = useAuthStore((state) => state.accessToken)
  const location = useLocation()

  if (!accessToken) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return children
}

export default ProtectedRoute
