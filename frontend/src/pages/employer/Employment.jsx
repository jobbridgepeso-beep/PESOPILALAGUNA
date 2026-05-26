import { useQuery } from '@tanstack/react-query'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import LoadingPage from '@/components/ui/LoadingPage'
import DataTable from '@/components/shared/DataTable'
import StatusBadge from '@/components/ui/StatusBadge'
import axiosInstance from '@/api/axiosInstance'

export default function Employment() {
  const { data, isLoading } = useQuery({
    queryKey: ['employer-employment'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/employer/employment')
      return res.data || []
    },
  })

  const columns = [
    {
      key: 'name',
      label: 'Jobseeker',
      render: (r) =>
        `${r.jobseeker_profiles?.first_name || ''} ${r.jobseeker_profiles?.last_name || ''}`.trim(),
    },
    { key: 'vacancy', label: 'Vacancy', render: (r) => r.job_vacancies?.title || '—' },
    { key: 'start_date', label: 'Start' },
    { key: 'status', label: 'Status', render: (r) => <StatusBadge status={r.status} /> },
  ]

  return (
    <DashboardLayout title="Employment Monitoring" description="Hired jobseekers">
      <PageHeader title="Employment records" description="Workers hired through JobBridge." />
      {isLoading ? <LoadingPage /> : <DataTable columns={columns} rows={data} />}
    </DashboardLayout>
  )
}
