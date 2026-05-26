import { useQuery } from '@tanstack/react-query'
import { Briefcase, Users, UserCheck, Clock } from 'lucide-react'
import axiosInstance from '@/api/axiosInstance'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import StatCard from '@/components/ui/StatCard'
import AnimatedStatGrid from '@/components/ui/AnimatedStatGrid'
import LoadingPage from '@/components/ui/LoadingPage'

function EmployerDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['employer-dashboard'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/employer/dashboard')
      return res.data
    },
  })

  return (
    <DashboardLayout
      title="Employer Dashboard"
      description="Manage vacancies and review applicants"
    >
      <PageHeader
        title="Hiring overview"
        description="Monitor your job postings, applicant pipeline, and hiring progress."
      />

      {isLoading ? (
        <LoadingPage message="Loading dashboard…" />
      ) : (
        <AnimatedStatGrid>
          <StatCard
            label="Active vacancies"
            value={data?.active_vacancies ?? 0}
            icon={Briefcase}
          />
          <StatCard
            label="Total applicants"
            value={data?.total_applicants ?? 0}
            icon={Users}
          />
          <StatCard
            label="Pending reviews"
            value={data?.pending_reviews ?? 0}
            icon={Clock}
          />
          <StatCard label="Hired" value={data?.hired ?? 0} icon={UserCheck} />
        </AnimatedStatGrid>
      )}
    </DashboardLayout>
  )
}

export default EmployerDashboard
