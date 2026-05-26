import { useQuery } from '@tanstack/react-query'
import { Briefcase, ClipboardList, Calendar } from 'lucide-react'
import axiosInstance from '@/api/axiosInstance'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import StatCard from '@/components/ui/StatCard'
import AnimatedStatGrid from '@/components/ui/AnimatedStatGrid'
import LoadingPage from '@/components/ui/LoadingPage'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'

function JobseekerDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['jobseeker-dashboard'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/jobseeker/dashboard')
      return res.data
    },
  })

  return (
    <DashboardLayout
      title="Jobseeker Dashboard"
      description="Overview of your applications and job opportunities"
    >
      <PageHeader
        title="Overview"
        description="Track your job applications, interviews, and available positions in Pila, Laguna."
      />

      {isLoading ? (
        <LoadingPage message="Loading dashboard…" />
      ) : (
        <>
          <AnimatedStatGrid>
            <StatCard
              label="Total applications"
              value={data?.applications?.total ?? 0}
              icon={ClipboardList}
            />
            <StatCard
              label="Pending review"
              value={data?.applications?.pending ?? 0}
              icon={Calendar}
            />
            <StatCard
              label="Active job openings"
              value={data?.active_jobs ?? 0}
              icon={Briefcase}
            />
          </AnimatedStatGrid>

          <Card>
            <CardHeader>
              <CardTitle>Quick information</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm leading-relaxed text-muted-foreground">
                Visit the job search module to browse vacancies matched to your profile.
                For assistance, contact PESO Pila staff during office hours.
              </p>
            </CardContent>
          </Card>
        </>
      )}
    </DashboardLayout>
  )
}

export default JobseekerDashboard
