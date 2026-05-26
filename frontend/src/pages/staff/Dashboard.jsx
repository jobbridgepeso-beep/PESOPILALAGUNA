import { useQuery } from '@tanstack/react-query'
import { Users, Briefcase, ClipboardCheck, CalendarDays, FileText } from 'lucide-react'
import axiosInstance from '@/api/axiosInstance'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import StatCard from '@/components/ui/StatCard'
import AnimatedStatGrid from '@/components/ui/AnimatedStatGrid'
import LoadingPage from '@/components/ui/LoadingPage'

function StaffDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['staff-dashboard'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/staff/dashboard')
      return res.data
    },
  })

  return (
    <DashboardLayout
      title="PESO Staff Dashboard"
      description="Municipal employment services operations"
    >
      <PageHeader
        title="Operations overview"
        description="Monitor jobseeker registrations, vacancy approvals, job fairs, and government programs."
      />

      {isLoading ? (
        <LoadingPage message="Loading dashboard…" />
      ) : (
        <AnimatedStatGrid>
          <StatCard
            label="Registered jobseekers"
            value={data?.total_jobseekers ?? 0}
            icon={Users}
          />
          <StatCard
            label="Active vacancies"
            value={data?.active_vacancies ?? 0}
            icon={Briefcase}
          />
          <StatCard
            label="Pending approvals"
            value={data?.pending_approvals ?? 0}
            icon={ClipboardCheck}
          />
          <StatCard
            label="Upcoming job fairs"
            value={data?.upcoming_job_fairs ?? 0}
            icon={CalendarDays}
          />
          <StatCard
            label="Pending program applications"
            value={data?.pending_programs ?? 0}
            icon={FileText}
          />
        </AnimatedStatGrid>
      )}
    </DashboardLayout>
  )
}

export default StaffDashboard
