import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Label from '@/components/ui/Label'
import Select from '@/components/ui/Select'
import LoadingPage from '@/components/ui/LoadingPage'
import StatusBadge from '@/components/ui/StatusBadge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import {
  getVacancies,
  createVacancy,
  closeVacancy,
  getApplicants,
  updateApplicationStatus,
} from '@/api/employerApi'

function Vacancies() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [selectedVacancy, setSelectedVacancy] = useState(null)
  const [form, setForm] = useState({
    title: '',
    description: '',
    requirements: '',
    employment_type: 'full-time',
    skills_required: '',
  })

  const { data: vacancies, isLoading } = useQuery({
    queryKey: ['employer-vacancies'],
    queryFn: async () => (await getVacancies()).data || [],
  })

  const { data: applicants, isLoading: loadingApplicants } = useQuery({
    queryKey: ['employer-applicants', selectedVacancy],
    queryFn: async () => (await getApplicants(selectedVacancy)).data || [],
    enabled: !!selectedVacancy,
  })

  const createMut = useMutation({
    mutationFn: () =>
      createVacancy({
        ...form,
        skills_required: form.skills_required
          ? form.skills_required.split(',').map((s) => s.trim()).filter(Boolean)
          : [],
      }),
    onSuccess: (res) => {
      if (res.success) {
        toast.success(res.message || 'Vacancy submitted for PESO approval')
        setShowForm(false)
        setForm({ title: '', description: '', requirements: '', employment_type: 'full-time', skills_required: '' })
        qc.invalidateQueries({ queryKey: ['employer-vacancies'] })
      } else toast.error(res.message)
    },
  })

  const statusMut = useMutation({
    mutationFn: ({ appId, status }) => updateApplicationStatus(appId, status),
    onSuccess: (res) => {
      if (res.success) {
        toast.success('Applicant status updated')
        qc.invalidateQueries({ queryKey: ['employer-applicants', selectedVacancy] })
      }
    },
  })

  return (
    <DashboardLayout title="Vacancies" description="Post and manage job openings">
      <PageHeader
        title="Job vacancies"
        description="New posts require PESO staff approval before jobseekers can apply."
        action={
          <Button onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : 'Post new vacancy'}
          </Button>
        }
      />

      {showForm && (
        <Card className="mb-8 max-w-2xl">
          <CardHeader>
            <CardTitle>New vacancy</CardTitle>
          </CardHeader>
          <CardContent className="form-stack">
            <div>
              <Label required>Job title</Label>
              <Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            </div>
            <div>
              <Label required>Description</Label>
              <textarea
                rows={3}
                className="w-full rounded-md border border-input px-4 py-2 text-sm"
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
              />
            </div>
            <div>
              <Label required>Requirements</Label>
              <textarea
                rows={3}
                className="w-full rounded-md border border-input px-4 py-2 text-sm"
                value={form.requirements}
                onChange={(e) => setForm({ ...form, requirements: e.target.value })}
              />
            </div>
            <div>
              <Label>Skills (comma-separated)</Label>
              <Input
                value={form.skills_required}
                onChange={(e) => setForm({ ...form, skills_required: e.target.value })}
              />
            </div>
            <div>
              <Label>Employment type</Label>
              <Select
                value={form.employment_type}
                onChange={(e) => setForm({ ...form, employment_type: e.target.value })}
              >
                <option value="full-time">Full-time</option>
                <option value="part-time">Part-time</option>
                <option value="contract">Contract</option>
                <option value="temporary">Temporary</option>
              </Select>
            </div>
            <Button onClick={() => createMut.mutate()} disabled={createMut.isPending}>
              Submit for approval
            </Button>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <LoadingPage />
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="space-y-3">
            <h3 className="font-semibold">Your vacancies</h3>
            {(vacancies || []).map((v) => (
              <Card
                key={v.id}
                className={`cursor-pointer transition-shadow hover:shadow-card-hover ${
                  selectedVacancy === v.id ? 'ring-2 ring-primary' : ''
                }`}
                onClick={() => setSelectedVacancy(v.id)}
              >
                <CardContent className="flex items-center justify-between p-4">
                  <div>
                    <p className="font-medium">{v.title}</p>
                    <StatusBadge status={v.status} />
                  </div>
                  {v.status !== 'closed' && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation()
                        closeVacancy(v.id).then(() => {
                          toast.success('Vacancy closed')
                          qc.invalidateQueries({ queryKey: ['employer-vacancies'] })
                        })
                      }}
                    >
                      Close
                    </Button>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>

          <div>
            <h3 className="mb-3 font-semibold">Applicants</h3>
            {!selectedVacancy ? (
              <p className="text-sm text-muted-foreground">Select a vacancy to view applicants.</p>
            ) : loadingApplicants ? (
              <LoadingPage />
            ) : !applicants?.length ? (
              <p className="text-sm text-muted-foreground">No applicants yet.</p>
            ) : (
              <ul className="space-y-3">
                {applicants.map((a) => (
                  <Card key={a.id}>
                    <CardContent className="space-y-3 p-4">
                      <div className="flex justify-between">
                        <p className="font-medium">
                          {a.profile?.first_name} {a.profile?.last_name}
                        </p>
                        <span className="text-xs font-bold text-primary">
                          {Math.round((a.match_score || 0) * 100)}% match
                        </span>
                      </div>
                      <StatusBadge status={a.status} />
                      <div className="flex flex-wrap gap-2">
                        {['reviewed', 'shortlisted', 'rejected', 'hired'].map((s) => (
                          <Button
                            key={s}
                            size="sm"
                            variant="secondary"
                            onClick={() => statusMut.mutate({ appId: a.id, status: s })}
                          >
                            {s}
                          </Button>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </DashboardLayout>
  )
}

export default Vacancies
