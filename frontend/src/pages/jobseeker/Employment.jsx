import { useQuery } from '@tanstack/react-query'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import LoadingPage from '@/components/ui/LoadingPage'
import DataTable from '@/components/shared/DataTable'
import StatusBadge from '@/components/ui/StatusBadge'
import axiosInstance from '@/api/axiosInstance'

export default function Employment() {
  const { data, isLoading } = useQuery({
    queryKey: ['jobseeker-employment'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/jobseeker/employment')
      return res.data || []
    },
  })

  const columns = [
    {
      key: 'employer',
      label: 'Employer',
      render: (r) => r.employer_profiles?.company_name || '—',
    },
    { key: 'position', label: 'Position' },
    { key: 'start_date', label: 'Start', render: (r) => r.start_date || '—' },
    { key: 'status', label: 'Status', render: (r) => <StatusBadge status={r.status} /> },
  ]

  return (
    <DashboardLayout title="Employment Monitoring" description="Your employment records">
      <PageHeader
        title="Employment monitoring"
        description="Records created when employers mark you as hired."
      />
      {isLoading ? <LoadingPage /> : <DataTable columns={columns} rows={data} />}
    </DashboardLayout>
  )
}
