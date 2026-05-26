import { useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import LoadingPage from '@/components/ui/LoadingPage'
import Button from '@/components/ui/Button'
import StatusBadge from '@/components/ui/StatusBadge'
import { Card, CardContent } from '@/components/ui/Card'
import axiosInstance from '@/api/axiosInstance'

const LABELS = {
  spes: 'Special Program for Employment of Students (SPES)',
  mst: 'Manpower Skills Training',
  dilp: 'Displaced Workers / DILP',
  owwa: 'OWWA Programs',
}

export default function ProgramApplyPage({ programType: programTypeProp }) {
  const { type: typeParam } = useParams()
  const type = programTypeProp || typeParam
  const qc = useQueryClient()
  const label = LABELS[type] || type?.toUpperCase()

  const { data: apps, isLoading } = useQuery({
    queryKey: ['jobseeker-programs'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/jobseeker/programs')
      return res.data || []
    },
  })

  const mine = (apps || []).filter((a) => a.program_type === type)
  const active = mine.find((a) => ['pending', 'approved'].includes(a.status))

  const apply = useMutation({
    mutationFn: () => axiosInstance.post(`/api/jobseeker/programs/${type}/apply`),
    onSuccess: (res) => {
      if (res.data?.success) {
        toast.success(res.data.message || 'Application submitted')
        qc.invalidateQueries({ queryKey: ['jobseeker-programs'] })
      } else toast.error(res.data?.message)
    },
    onError: (e) => toast.error(e.response?.data?.message || 'Could not apply'),
  })

  return (
    <DashboardLayout title={label} description="PESO program application">
      <PageHeader
        title={label}
        description="Submit an application to participate in this PESO program."
      />
      {isLoading ? (
        <LoadingPage />
      ) : (
        <div className="space-y-4 max-w-2xl">
          {active ? (
            <Card>
              <CardContent className="flex flex-wrap items-center justify-between gap-4 p-6">
                <div>
                  <p className="font-semibold">Your application</p>
                  <p className="text-sm text-muted-foreground">
                    Submitted {new Date(active.created_at).toLocaleDateString('en-PH')}
                  </p>
                </div>
                <StatusBadge status={active.status} />
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="space-y-4 p-6">
                <p className="text-sm text-muted-foreground">
                  You have not applied to this program yet. PESO staff will review your
                  application after submission.
                </p>
                <Button onClick={() => apply.mutate()} disabled={apply.isPending}>
                  Apply now
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </DashboardLayout>
  )
}
