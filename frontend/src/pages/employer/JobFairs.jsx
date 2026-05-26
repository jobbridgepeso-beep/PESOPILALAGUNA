import { useQuery } from '@tanstack/react-query'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import LoadingPage from '@/components/ui/LoadingPage'
import StatusBadge from '@/components/ui/StatusBadge'
import { Card, CardContent } from '@/components/ui/Card'
import axiosInstance from '@/api/axiosInstance'

export default function JobFairs() {
  const { data, isLoading } = useQuery({
    queryKey: ['employer-job-fairs'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/employer/job-fairs')
      return res.data || []
    },
  })

  return (
    <DashboardLayout title="Job Fair" description="Upcoming PESO job fairs">
      <PageHeader title="Job fairs" description="Participate in PESO-organized job fairs in Laguna." />
      {isLoading ? (
        <LoadingPage />
      ) : !data?.length ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            No upcoming job fairs.
          </CardContent>
        </Card>
      ) : (
        <ul className="space-y-4">
          {data.map((fair) => (
            <li key={fair.id}>
              <Card>
                <CardContent className="p-6">
                  <h3 className="text-lg font-semibold">{fair.title}</h3>
                  <p className="text-sm text-muted-foreground">{fair.venue}</p>
                  <p className="mt-1 text-sm">
                    {fair.event_date} · {fair.start_time}–{fair.end_time}
                  </p>
                  <StatusBadge status={fair.status} className="mt-2" />
                </CardContent>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </DashboardLayout>
  )
}
