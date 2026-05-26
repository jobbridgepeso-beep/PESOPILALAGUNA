import { useQuery } from '@tanstack/react-query'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import LoadingPage from '@/components/ui/LoadingPage'
import DataTable from '@/components/shared/DataTable'
import StatusBadge from '@/components/ui/StatusBadge'
import axiosInstance from '@/api/axiosInstance'

export default function Interviews() {
  const { data, isLoading } = useQuery({
    queryKey: ['jobseeker-interviews'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/jobseeker/interviews')
      return res.data || []
    },
  })

  const columns = [
    {
      key: 'job',
      label: 'Vacancy',
      render: (r) => r.job_applications?.job_vacancies?.title || '—',
    },
    {
      key: 'when',
      label: 'Scheduled',
      render: (r) =>
        r.scheduled_at ? new Date(r.scheduled_at).toLocaleString('en-PH') : '—',
    },
    { key: 'location', label: 'Location' },
    { key: 'status', label: 'Status', render: (r) => <StatusBadge status={r.status} /> },
  ]

  return (
    <DashboardLayout title="Interview Schedule" description="Upcoming and past interviews">
      <PageHeader title="Interview schedule" description="Interviews scheduled by employers." />
      {isLoading ? <LoadingPage /> : <DataTable columns={columns} rows={data} />}
    </DashboardLayout>
  )
}
