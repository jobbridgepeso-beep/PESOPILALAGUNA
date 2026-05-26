import {
  LayoutDashboard,
  User,
  Briefcase,
  ClipboardList,
  Building2,
  CheckSquare,
} from 'lucide-react'

export const ROLE_NAV = {
  jobseeker: [
    { to: '/jobseeker/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/jobseeker/profile', label: 'My Profile', icon: User },
    { to: '/jobseeker/jobs', label: 'Job Search', icon: Briefcase },
    { to: '/jobseeker/applications', label: 'My Applications', icon: ClipboardList },
  ],
  employer: [
    { to: '/employer/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/employer/profile', label: 'Company Profile', icon: Building2 },
    { to: '/employer/vacancies', label: 'Vacancies', icon: Briefcase },
  ],
  staff: [
    { to: '/staff/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/staff/approvals', label: 'Vacancy Approvals', icon: CheckSquare },
  ],
  admin: [
    { to: '/admin/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  ],
}
