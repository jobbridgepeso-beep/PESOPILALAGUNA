import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import Button from '@/components/ui/Button'
import LoadingPage from '@/components/ui/LoadingPage'
import StatusBadge from '@/components/ui/StatusBadge'
import { Card, CardContent } from '@/components/ui/Card'
import { getJobs, applyToJob } from '@/api/jobseekerApi'

function MatchBadge({ score }) {
  const pct = Math.round((score || 0) * 100)
  return (
    <span className="rounded-full bg-primary/10 px-2.5 py-1 text-xs font-bold text-primary">
      {pct}% match
    </span>
  )
}

function JobSearch() {
  const qc = useQueryClient()
  const [search, setSearch] = useState('')

  const { data: jobs, isLoading } = useQuery({
    queryKey: ['jobseeker-jobs'],
    queryFn: async () => {
      const res = await getJobs()
      return res.data || []
    },
  })

  const applyMutation = useMutation({
    mutationFn: (vacancyId) => applyToJob(vacancyId),
    onSuccess: (res) => {
      if (res.success) {
        toast.success('Application submitted!')
        qc.invalidateQueries({ queryKey: ['jobseeker-applications'] })
        qc.invalidateQueries({ queryKey: ['jobseeker-dashboard'] })
      } else toast.error(res.message)
    },
    onError: (e) => toast.error(e.response?.data?.message || 'Apply failed'),
  })

  const filtered = (jobs || []).filter((j) => {
    const q = search.toLowerCase()
    const company = j.employer_profiles?.company_name || ''
    return (
      j.title?.toLowerCase().includes(q) ||
      company.toLowerCase().includes(q) ||
      j.employment_type?.toLowerCase().includes(q)
    )
  })

  return (
    <DashboardLayout title="Job Search" description="AI-ranked vacancies in Pila, Laguna">
      <PageHeader
        title="Find jobs"
        description="Vacancies are ranked by match score based on your profile skills and experience."
      />
      <div className="mb-6 max-w-md">
        <input
          type="search"
          placeholder="Search by title or company…"
          className="h-11 w-full rounded-md border border-input px-4 text-sm shadow-sm"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>
      {isLoading ? (
        <LoadingPage />
      ) : filtered.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            No active vacancies yet. Check back after PESO staff approves employer postings.
          </CardContent>
        </Card>
      ) : (
        <ul className="space-y-4">
          {filtered.map((job) => (
            <li key={job.id}>
              <Card className="transition-shadow hover:shadow-card-hover">
                <CardContent className="flex flex-col gap-4 p-6 sm:flex-row sm:items-start sm:justify-between">
                  <div className="space-y-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-lg font-semibold">{job.title}</h3>
                      <MatchBadge score={job.match_score} />
                    </div>
                    <p className="text-sm font-medium text-primary">
                      {job.employer_profiles?.company_name || 'Employer'}
                    </p>
                    <p className="line-clamp-2 text-sm text-muted-foreground">
                      {job.description}
                    </p>
                    <div className="flex flex-wrap gap-2">
                      <StatusBadge status={job.employment_type} />
                      {job.salary_min && (
                        <span className="text-xs text-muted-foreground">
                          ₱{Number(job.salary_min).toLocaleString()}
                          {job.salary_max ? ` – ₱${Number(job.salary_max).toLocaleString()}` : '+'}
                        </span>
                      )}
                    </div>
                  </div>
                  <Button
                    size="sm"
                    className="shrink-0"
                    disabled={applyMutation.isPending}
                    onClick={() => applyMutation.mutate(job.id)}
                  >
                    Apply now
                  </Button>
                </CardContent>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </DashboardLayout>
  )
}

export default JobSearch
