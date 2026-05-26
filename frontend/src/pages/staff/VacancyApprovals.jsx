import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import Button from '@/components/ui/Button'
import LoadingPage from '@/components/ui/LoadingPage'
import StatusBadge from '@/components/ui/StatusBadge'
import { Card, CardContent } from '@/components/ui/Card'
import { getPendingVacancies, approveVacancy, rejectVacancy } from '@/api/staffApi'

function VacancyApprovals() {
  const qc = useQueryClient()
  const [rejectId, setRejectId] = useState(null)
  const [reason, setReason] = useState('')

  const { data: pending, isLoading } = useQuery({
    queryKey: ['staff-pending-vacancies'],
    queryFn: async () => (await getPendingVacancies()).data || [],
  })

  const approveMut = useMutation({
    mutationFn: approveVacancy,
    onSuccess: (res) => {
      if (res.success) {
        toast.success('Vacancy approved — now visible to jobseekers')
        qc.invalidateQueries({ queryKey: ['staff-pending-vacancies'] })
        qc.invalidateQueries({ queryKey: ['staff-dashboard'] })
      }
    },
  })

  const rejectMut = useMutation({
    mutationFn: ({ id, reason: r }) => rejectVacancy(id, r),
    onSuccess: (res) => {
      if (res.success) {
        toast.success('Vacancy rejected')
        setRejectId(null)
        setReason('')
        qc.invalidateQueries({ queryKey: ['staff-pending-vacancies'] })
      }
    },
  })

  return (
    <DashboardLayout title="Vacancy Approvals" description="Review employer job postings">
      <PageHeader
        title="Pending vacancies"
        description="Approve vacancies to publish them for jobseekers in Pila, Laguna."
      />
      {isLoading ? (
        <LoadingPage />
      ) : !pending?.length ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            No vacancies awaiting approval.
          </CardContent>
        </Card>
      ) : (
        <ul className="space-y-4">
          {pending.map((v) => (
            <li key={v.id}>
              <Card>
                <CardContent className="space-y-4 p-6">
                  <div className="flex flex-wrap items-start justify-between gap-2">
                    <div>
                      <h3 className="text-lg font-semibold">{v.title}</h3>
                      <p className="text-sm font-medium text-primary">
                        {v.employer_profiles?.company_name}
                      </p>
                      <p className="text-xs text-muted-foreground">{v.employer_profiles?.industry}</p>
                    </div>
                    <StatusBadge status="pending" />
                  </div>
                  <p className="text-sm text-muted-foreground line-clamp-3">{v.description}</p>
                  <p className="text-sm">
                    <span className="font-medium">Requirements: </span>
                    {v.requirements}
                  </p>
                  {rejectId === v.id ? (
                    <div className="space-y-2 rounded-md border border-border bg-muted/50 p-4">
                      <label className="text-sm font-medium">Rejection reason</label>
                      <textarea
                        rows={2}
                        className="w-full rounded-md border border-input px-3 py-2 text-sm"
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                      />
                      <div className="flex gap-2">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => rejectMut.mutate({ id: v.id, reason })}
                          disabled={!reason.trim() || rejectMut.isPending}
                        >
                          Confirm reject
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => setRejectId(null)}>
                          Cancel
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-wrap gap-2">
                      <Button
                        size="sm"
                        onClick={() => approveMut.mutate(v.id)}
                        disabled={approveMut.isPending}
                      >
                        Approve
                      </Button>
                      <Button size="sm" variant="secondary" onClick={() => setRejectId(v.id)}>
                        Reject
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </DashboardLayout>
  )
}

export default VacancyApprovals
