import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import LoadingPage from '@/components/ui/LoadingPage'
import DataTable from '@/components/shared/DataTable'
import Button from '@/components/ui/Button'
import StatusBadge from '@/components/ui/StatusBadge'
import axiosInstance from '@/api/axiosInstance'
import { updateApplicationStatus } from '@/api/employerApi'

export default function Applicants() {
  const qc = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ['employer-applications'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/employer/applications')
      return res.data || []
    },
  })

  const statusMut = useMutation({
    mutationFn: ({ id, status }) => updateApplicationStatus(id, status),
    onSuccess: (res) => {
      if (res.success) {
        toast.success('Application updated')
        qc.invalidateQueries({ queryKey: ['employer-applications'] })
      }
    },
  })

  const columns = [
    {
      key: 'applicant',
      label: 'Applicant',
      render: (r) =>
        `${r.jobseeker_profiles?.first_name || ''} ${r.jobseeker_profiles?.last_name || ''}`.trim(),
    },
    { key: 'vacancy', label: 'Vacancy', render: (r) => r.job_vacancies?.title },
    { key: 'status', label: 'Status', render: (r) => <StatusBadge status={r.status} /> },
    {
      key: 'actions',
      label: 'Actions',
      render: (r) =>
        r.status === 'pending' ? (
          <div className="flex flex-wrap gap-2">
            <Button size="sm" onClick={() => statusMut.mutate({ id: r.id, status: 'shortlisted' })}>
              Shortlist
            </Button>
            <Button size="sm" variant="secondary" onClick={() => statusMut.mutate({ id: r.id, status: 'rejected' })}>
              Reject
            </Button>
          </div>
        ) : r.status === 'shortlisted' ? (
          <Button size="sm" onClick={() => statusMut.mutate({ id: r.id, status: 'hired' })}>
            Mark hired
          </Button>
        ) : (
          '—'
        ),
    },
  ]

  return (
    <DashboardLayout title="Applicant Management" description="All applications across vacancies">
      <PageHeader title="Applicants" description="Review and update application status." />
      {isLoading ? <LoadingPage /> : <DataTable columns={columns} rows={data} />}
    </DashboardLayout>
  )
}
