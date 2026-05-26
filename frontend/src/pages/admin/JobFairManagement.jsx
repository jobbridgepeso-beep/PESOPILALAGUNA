import { useQuery } from '@tanstack/react-query'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import LoadingPage from '@/components/ui/LoadingPage'
import StatusBadge from '@/components/ui/StatusBadge'
import { Card, CardContent } from '@/components/ui/Card'
import axiosInstance from '@/api/axiosInstance'

export default function JobFairManagement() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-job-fairs'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/admin/job-fairs')
      return res.data || []
    },
  })

  return (
    <DashboardLayout title="Job Fair Management" description="All job fairs">
      <PageHeader title="Job fair management" description="Overview of job fairs on the platform." />
      {isLoading ? (
        <LoadingPage />
      ) : (
        <ul className="space-y-3">
          {(data || []).map((fair) => (
            <li key={fair.id}>
              <Card>
                <CardContent className="flex flex-wrap items-center justify-between gap-2 p-5">
                  <div>
                    <p className="font-semibold">{fair.title}</p>
                    <p className="text-sm text-muted-foreground">
                      {fair.event_date} · {fair.venue}
                    </p>
                  </div>
                  <StatusBadge status={fair.status} />
                </CardContent>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </DashboardLayout>
  )
}
