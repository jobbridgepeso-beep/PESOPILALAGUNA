import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import RoleGuard from '@/components/auth/RoleGuard'

// Public pages (stubs — implemented in task 18.4)
import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'
import OTPVerificationPage from '@/pages/auth/OTPVerificationPage'
import ForgotPasswordPage from '@/pages/auth/ForgotPasswordPage'
import ResetPasswordPage from '@/pages/auth/ResetPasswordPage'

// Role dashboards (stubs — implemented in tasks 20–23)
import JobseekerDashboard from '@/pages/jobseeker/Dashboard'
import EmployerDashboard from '@/pages/employer/Dashboard'
import StaffDashboard from '@/pages/staff/Dashboard'
import AdminDashboard from '@/pages/admin/Dashboard'

function AppRoutes() {
  const location = useLocation()

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
      {/* Public routes */}
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/verify-otp" element={<OTPVerificationPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />

      {/* Jobseeker routes — Requirement 3.3 */}
      <Route
        path="/jobseeker/*"
        element={
          <ProtectedRoute>
            <RoleGuard allowedRoles={['jobseeker']}>
              <Routes>
                <Route index element={<Navigate to="dashboard" replace />} />
                <Route path="dashboard" element={<JobseekerDashboard />} />
              </Routes>
            </RoleGuard>
          </ProtectedRoute>
        }
      />

      {/* Employer routes — Requirement 3.4 */}
      <Route
        path="/employer/*"
        element={
          <ProtectedRoute>
            <RoleGuard allowedRoles={['employer']}>
              <Routes>
                <Route index element={<Navigate to="dashboard" replace />} />
                <Route path="dashboard" element={<EmployerDashboard />} />
              </Routes>
            </RoleGuard>
          </ProtectedRoute>
        }
      />

      {/* PESO Staff routes — Requirement 3.5 */}
      <Route
        path="/staff/*"
        element={
          <ProtectedRoute>
            <RoleGuard allowedRoles={['staff']}>
              <Routes>
                <Route index element={<Navigate to="dashboard" replace />} />
                <Route path="dashboard" element={<StaffDashboard />} />
              </Routes>
            </RoleGuard>
          </ProtectedRoute>
        }
      />

      {/* Admin routes — Requirement 3.6 */}
      <Route
        path="/admin/*"
        element={
          <ProtectedRoute>
            <RoleGuard allowedRoles={['admin']}>
              <Routes>
                <Route index element={<Navigate to="dashboard" replace />} />
                <Route path="dashboard" element={<AdminDashboard />} />
              </Routes>
            </RoleGuard>
          </ProtectedRoute>
        }
      />

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </AnimatePresence>
  )
}

function App() {
  return <AppRoutes />
}

export default App
