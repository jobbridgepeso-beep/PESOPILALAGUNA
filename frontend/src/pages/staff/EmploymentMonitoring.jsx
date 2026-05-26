import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import LoadingPage from '@/components/ui/LoadingPage'
import DataTable from '@/components/shared/DataTable'
import Button from '@/components/ui/Button'
import StatusBadge from '@/components/ui/StatusBadge'
import axiosInstance from '@/api/axiosInstance'
import { employmentColumns } from './managementColumns'

export default function EmploymentMonitoring() {
  const qc = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ['staff-employment'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/staff/employment')
      return res.data || []
    },
  })

  const update = useMutation({
    mutationFn: ({ id, status }) =>
      axiosInstance.patch('/api/staff/employment', { id, status }),
    onSuccess: (res) => {
      if (res.data?.success) {
        toast.success('Record updated')
        qc.invalidateQueries({ queryKey: ['staff-employment'] })
      }
    },
  })

  const columns = [
    ...employmentColumns,
    {
      key: 'actions',
      label: 'Actions',
      render: (r) =>
        r.status === 'active' ? (
          <Button size="sm" variant="secondary" onClick={() => update.mutate({ id: r.id, status: 'ended' })}>
            Mark ended
          </Button>
        ) : (
          '—'
        ),
    },
  ]

  return (
    <DashboardLayout title="Employment Monitoring" description="Track placements">
      <PageHeader title="Employment monitoring" description="Update employment record status." />
      {isLoading ? <LoadingPage /> : <DataTable columns={columns} rows={data} />}
    </DashboardLayout>
  )
}
