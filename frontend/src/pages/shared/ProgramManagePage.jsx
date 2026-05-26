import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import LoadingPage from '@/components/ui/LoadingPage'
import DataTable from '@/components/shared/DataTable'
import Button from '@/components/ui/Button'
import StatusBadge from '@/components/ui/StatusBadge'
import axiosInstance from '@/api/axiosInstance'

const LABELS = {
  spes: 'SPES Management',
  mst: 'Manpower Skills Management',
  dilp: 'DILP Management',
  owwa: 'OWWA Management',
}

export default function ProgramManagePage({ role = 'staff', programType: programTypeProp }) {
  const { type: typeParam } = useParams()
  const type = programTypeProp || typeParam
  const qc = useQueryClient()
  const title = LABELS[type] || 'Program Management'
  const base = `/api/${role}`

  const { data, isLoading } = useQuery({
    queryKey: [`${role}-programs`, type],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get(`${base}/programs/${type}`)
      return res.data || []
    },
  })

  const review = useMutation({
    mutationFn: ({ id, status }) =>
      axiosInstance.patch(`${base}/programs/${type}`, { id, status }),
    onSuccess: (res) => {
      if (res.data?.success) {
        toast.success('Application updated')
        qc.invalidateQueries({ queryKey: [`${role}-programs`, type] })
      }
    },
  })

  const columns = [
    {
      key: 'name',
      label: 'Applicant',
      render: (r) =>
        `${r.jobseeker_profiles?.first_name || ''} ${r.jobseeker_profiles?.last_name || ''}`.trim() ||
        '—',
    },
    { key: 'phone', label: 'Phone', render: (r) => r.jobseeker_profiles?.phone || '—' },
    { key: 'status', label: 'Status', render: (r) => <StatusBadge status={r.status} /> },
    ...(role === 'staff'
      ? [
          {
            key: 'actions',
            label: 'Actions',
            render: (r) =>
              r.status === 'pending' ? (
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    onClick={() => review.mutate({ id: r.id, status: 'approved' })}
                  >
                    Approve
                  </Button>
                  <Button
                    size="sm"
                    variant="secondary"
                    onClick={() => review.mutate({ id: r.id, status: 'rejected' })}
                  >
                    Reject
                  </Button>
                </div>
              ) : (
                '—'
              ),
          },
        ]
      : []),
  ]

  return (
    <DashboardLayout title={title} description="Review program applications">
      <PageHeader title={title} description="Approve or reject jobseeker program applications." />
      {isLoading ? <LoadingPage /> : <DataTable columns={columns} rows={data} />}
    </DashboardLayout>
  )
}
