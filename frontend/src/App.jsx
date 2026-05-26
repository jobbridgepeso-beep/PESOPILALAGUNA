import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import ProtectedRoute from '@/components/auth/ProtectedRoute'
import RoleGuard from '@/components/auth/RoleGuard'
import { JOBSEEKER, EMPLOYER, STAFF, ADMIN } from '@/config/modulePaths'

import LoginPage from '@/pages/auth/LoginPage'
import RegisterPage from '@/pages/auth/RegisterPage'
import OTPVerificationPage from '@/pages/auth/OTPVerificationPage'
import ForgotPasswordPage from '@/pages/auth/ForgotPasswordPage'
import ResetPasswordPage from '@/pages/auth/ResetPasswordPage'

import JobseekerDashboard from '@/pages/jobseeker/Dashboard'
import JobseekerProfile from '@/pages/jobseeker/Profile'
import JobSearch from '@/pages/jobseeker/JobSearch'
import MyApplications from '@/pages/jobseeker/MyApplications'
import JobseekerEmployment from '@/pages/jobseeker/Employment'
import JobseekerInterviews from '@/pages/jobseeker/Interviews'
import JobseekerJobFairs from '@/pages/jobseeker/JobFairs'
import JobseekerSPES from '@/pages/jobseeker/SPES'
import JobseekerMST from '@/pages/jobseeker/ManpowerSkillsTraining'
import JobseekerDILP from '@/pages/jobseeker/DILP'
import JobseekerOWWA from '@/pages/jobseeker/OWWA'
import NotificationsPage from '@/pages/shared/NotificationsPage'
import SettingsPage from '@/pages/shared/SettingsPage'

import EmployerDashboard from '@/pages/employer/Dashboard'
import EmployerMyProfile from '@/pages/employer/MyProfile'
import EmployerCompany from '@/pages/employer/Profile'
import EmployerVacancies from '@/pages/employer/Vacancies'
import EmployerApplicants from '@/pages/employer/Applicants'
import EmployerInterviews from '@/pages/employer/Interviews'
import EmployerJobFairs from '@/pages/employer/JobFairs'
import EmployerEmployment from '@/pages/employer/Employment'

import StaffDashboard from '@/pages/staff/Dashboard'
import StaffJobseekers from '@/pages/staff/JobseekerManagement'
import StaffEmployers from '@/pages/staff/EmployerManagement'
import StaffVacancies from '@/pages/staff/VacancyManagement'
import StaffInterviews from '@/pages/staff/InterviewOversight'
import StaffEmployment from '@/pages/staff/EmploymentMonitoring'
import StaffJobFairs from '@/pages/staff/JobFairManagement'
import StaffMST from '@/pages/staff/ManpowerSkillsManagement'
import StaffDILP from '@/pages/staff/DILPManagement'
import StaffOWWA from '@/pages/staff/OWWAManagement'
import StaffSPES from '@/pages/staff/SPESManagement'
import StaffLMI from '@/pages/staff/LMIReports'
import StaffAnnouncements from '@/pages/staff/Announcements'

import AdminDashboard from '@/pages/admin/Dashboard'
import AdminJobseekers from '@/pages/admin/JobseekerManagement'
import AdminEmployers from '@/pages/admin/EmployerManagement'
import AdminStaff from '@/pages/admin/StaffManagement'
import AdminVacancies from '@/pages/admin/VacancyManagement'
import AdminInterviews from '@/pages/admin/InterviewOversight'
import AdminEmployment from '@/pages/admin/EmploymentMonitoring'
import AdminJobFairs from '@/pages/admin/JobFairManagement'
import AdminMST from '@/pages/admin/ManpowerSkillsManagement'
import AdminDILP from '@/pages/admin/DILPManagement'
import AdminOWWA from '@/pages/admin/OWWAManagement'
import AdminSPES from '@/pages/admin/SPESManagement'
import AdminLMI from '@/pages/admin/LMIReports'
import AdminAnnouncements from '@/pages/admin/Announcements'
import AdminAudit from '@/pages/admin/AuditTrail'

function AppRoutes() {
  const location = useLocation()

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/verify-otp" element={<OTPVerificationPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />

        <Route
          path="/jobseeker/*"
          element={
            <ProtectedRoute>
              <RoleGuard allowedRoles={['jobseeker']}>
                <Routes>
                  <Route index element={<Navigate to="dashboard" replace />} />
                  <Route path="dashboard" element={<JobseekerDashboard />} />
                  <Route path="profile" element={<JobseekerProfile />} />
                  <Route path="jobs" element={<JobSearch />} />
                  <Route path="applications" element={<MyApplications />} />
                  <Route path="employment" element={<JobseekerEmployment />} />
                  <Route path="interviews" element={<JobseekerInterviews />} />
                  <Route path="job-fairs" element={<JobseekerJobFairs />} />
                  <Route path="spes" element={<JobseekerSPES />} />
                  <Route path="manpower-skills-training" element={<JobseekerMST />} />
                  <Route path="dilp" element={<JobseekerDILP />} />
                  <Route path="owwa" element={<JobseekerOWWA />} />
                  <Route path="notifications" element={<NotificationsPage role="jobseeker" />} />
                  <Route path="settings" element={<SettingsPage role="jobseeker" />} />
                  <Route path="programs/spes" element={<Navigate to={JOBSEEKER.spes} replace />} />
                  <Route path="programs/mst" element={<Navigate to={JOBSEEKER.manpowerSkills} replace />} />
                  <Route path="programs/dilp" element={<Navigate to={JOBSEEKER.dilp} replace />} />
                  <Route path="programs/owwa" element={<Navigate to={JOBSEEKER.owwa} replace />} />
                  <Route path="programs/:type" element={<Navigate to={JOBSEEKER.spes} replace />} />
                </Routes>
              </RoleGuard>
            </ProtectedRoute>
          }
        />

        <Route
          path="/employer/*"
          element={
            <ProtectedRoute>
              <RoleGuard allowedRoles={['employer']}>
                <Routes>
                  <Route index element={<Navigate to="dashboard" replace />} />
                  <Route path="dashboard" element={<EmployerDashboard />} />
                  <Route path="my-profile" element={<EmployerMyProfile />} />
                  <Route path="company" element={<EmployerCompany />} />
                  <Route path="profile" element={<Navigate to={EMPLOYER.company} replace />} />
                  <Route path="vacancies" element={<EmployerVacancies />} />
                  <Route path="applicants" element={<EmployerApplicants />} />
                  <Route path="interviews" element={<EmployerInterviews />} />
                  <Route path="job-fairs" element={<EmployerJobFairs />} />
                  <Route path="employment" element={<EmployerEmployment />} />
                  <Route path="notifications" element={<NotificationsPage role="employer" />} />
                  <Route path="settings" element={<SettingsPage role="employer" />} />
                </Routes>
              </RoleGuard>
            </ProtectedRoute>
          }
        />

        <Route
          path="/staff/*"
          element={
            <ProtectedRoute>
              <RoleGuard allowedRoles={['staff']}>
                <Routes>
                  <Route index element={<Navigate to="dashboard" replace />} />
                  <Route path="dashboard" element={<StaffDashboard />} />
                  <Route path="jobseekers" element={<StaffJobseekers />} />
                  <Route path="employers" element={<StaffEmployers />} />
                  <Route path="vacancies" element={<StaffVacancies />} />
                  <Route path="interviews" element={<StaffInterviews />} />
                  <Route path="employment" element={<StaffEmployment />} />
                  <Route path="job-fairs" element={<StaffJobFairs />} />
                  <Route path="manpower-skills" element={<StaffMST />} />
                  <Route path="dilp" element={<StaffDILP />} />
                  <Route path="owwa" element={<StaffOWWA />} />
                  <Route path="spes" element={<StaffSPES />} />
                  <Route path="lmi-reports" element={<StaffLMI />} />
                  <Route path="announcements" element={<StaffAnnouncements />} />
                  <Route path="notifications" element={<NotificationsPage role="staff" />} />
                  <Route path="settings" element={<SettingsPage role="staff" />} />
                  <Route path="approvals" element={<Navigate to={`${STAFF.vacancies}?tab=pending`} replace />} />
                  <Route path="programs/mst" element={<Navigate to={STAFF.manpowerSkills} replace />} />
                  <Route path="programs/dilp" element={<Navigate to={STAFF.dilp} replace />} />
                  <Route path="programs/owwa" element={<Navigate to={STAFF.owwa} replace />} />
                  <Route path="programs/spes" element={<Navigate to={STAFF.spes} replace />} />
                  <Route path="programs/:type" element={<Navigate to={STAFF.spes} replace />} />
                </Routes>
              </RoleGuard>
            </ProtectedRoute>
          }
        />

        <Route
          path="/admin/*"
          element={
            <ProtectedRoute>
              <RoleGuard allowedRoles={['admin']}>
                <Routes>
                  <Route index element={<Navigate to="dashboard" replace />} />
                  <Route path="dashboard" element={<AdminDashboard />} />
                  <Route path="jobseekers" element={<AdminJobseekers />} />
                  <Route path="employers" element={<AdminEmployers />} />
                  <Route path="staff" element={<AdminStaff />} />
                  <Route path="vacancies" element={<AdminVacancies />} />
                  <Route path="interviews" element={<AdminInterviews />} />
                  <Route path="employment" element={<AdminEmployment />} />
                  <Route path="job-fairs" element={<AdminJobFairs />} />
                  <Route path="manpower-skills" element={<AdminMST />} />
                  <Route path="dilp" element={<AdminDILP />} />
                  <Route path="owwa" element={<AdminOWWA />} />
                  <Route path="spes" element={<AdminSPES />} />
                  <Route path="lmi-reports" element={<AdminLMI />} />
                  <Route path="announcements" element={<AdminAnnouncements />} />
                  <Route path="audit-trail" element={<AdminAudit />} />
                  <Route path="notifications" element={<NotificationsPage role="admin" />} />
                  <Route path="settings" element={<SettingsPage role="admin" canEdit />} />
                  <Route path="programs/mst" element={<Navigate to={ADMIN.manpowerSkills} replace />} />
                  <Route path="programs/dilp" element={<Navigate to={ADMIN.dilp} replace />} />
                  <Route path="programs/owwa" element={<Navigate to={ADMIN.owwa} replace />} />
                  <Route path="programs/spes" element={<Navigate to={ADMIN.spes} replace />} />
                  <Route path="programs/:type" element={<Navigate to={ADMIN.spes} replace />} />
                </Routes>
              </RoleGuard>
            </ProtectedRoute>
          }
        />

        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </AnimatePresence>
  )
}

function App() {
  return <AppRoutes />
}

export default App
