import { Routes, Route, Navigate } from 'react-router-dom'
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

function App() {
  return (
    <Routes>
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
                <Route path="dashboard" element={<JobseekerDashboard />} />
                {/* Additional jobseeker routes added in task 20 */}
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
                <Route path="dashboard" element={<EmployerDashboard />} />
                {/* Additional employer routes added in task 21 */}
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
                <Route path="dashboard" element={<StaffDashboard />} />
                {/* Additional staff routes added in task 22 */}
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
                <Route path="dashboard" element={<AdminDashboard />} />
                {/* Additional admin routes added in task 23 */}
              </Routes>
            </RoleGuard>
          </ProtectedRoute>
        }
      />

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  )
}

export default App
