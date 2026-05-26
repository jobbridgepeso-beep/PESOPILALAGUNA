import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import LoadingPage from '@/components/ui/LoadingPage'
import Button from '@/components/ui/Button'
import StatusBadge from '@/components/ui/StatusBadge'
import { Card, CardContent } from '@/components/ui/Card'
import axiosInstance from '@/api/axiosInstance'

export default function JobFairs() {
  const qc = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ['jobseeker-job-fairs'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/jobseeker/job-fairs')
      return res.data || []
    },
  })

  const register = useMutation({
    mutationFn: (fairId) =>
      axiosInstance.post(`/api/jobseeker/job-fairs/${fairId}/register`),
    onSuccess: (res) => {
      if (res.data?.success) {
        toast.success('Registered — QR code generated')
        qc.invalidateQueries({ queryKey: ['jobseeker-job-fairs'] })
      } else toast.error(res.data?.message)
    },
    onError: (e) => toast.error(e.response?.data?.message || 'Registration failed'),
  })

  return (
    <DashboardLayout title="Job Fair" description="Register for PESO job fairs">
      <PageHeader
        title="Job fairs"
        description="Register to receive a QR code for attendance check-in."
      />
      {isLoading ? (
        <LoadingPage />
      ) : !data?.length ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            No upcoming job fairs at this time.
          </CardContent>
        </Card>
      ) : (
        <ul className="space-y-4">
          {data.map((fair) => (
            <li key={fair.id}>
              <Card>
                <CardContent className="flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <h3 className="text-lg font-semibold">{fair.title}</h3>
                    <p className="text-sm text-muted-foreground">{fair.venue}</p>
                    <p className="text-sm">
                      {fair.event_date} · {fair.start_time}–{fair.end_time}
                    </p>
                    <StatusBadge status={fair.status} className="mt-2" />
                  </div>
                  <div className="shrink-0">
                    {fair.registered ? (
                      <div className="text-sm">
                        <p className="font-medium text-primary">Registered</p>
                        {fair.registration?.qr_url && (
                          <a
                            href={fair.registration.qr_url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-xs text-muted-foreground underline"
                          >
                            View QR code
                          </a>
                        )}
                      </div>
                    ) : (
                      <Button
                        onClick={() => register.mutate(fair.id)}
                        disabled={register.isPending}
                      >
                        Register
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </DashboardLayout>
  )
}
