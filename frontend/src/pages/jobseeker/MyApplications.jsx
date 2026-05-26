import { useQuery } from '@tanstack/react-query'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import LoadingPage from '@/components/ui/LoadingPage'
import StatusBadge from '@/components/ui/StatusBadge'
import { Card, CardContent } from '@/components/ui/Card'
import { getApplications } from '@/api/jobseekerApi'

function MyApplications() {
  const { data: apps, isLoading } = useQuery({
    queryKey: ['jobseeker-applications'],
    queryFn: async () => {
      const res = await getApplications()
      return res.data || []
    },
  })

  return (
    <DashboardLayout title="My Applications" description="Track your application status">
      <PageHeader
        title="Applications"
        description="Status updates are stored in Supabase and reflected here in real time."
      />
      {isLoading ? (
        <LoadingPage />
      ) : !apps?.length ? (
        <Card>
          <CardContent className="py-12 text-center text-muted-foreground">
            You have not applied to any jobs yet. Visit Job Search to apply.
          </CardContent>
        </Card>
      ) : (
        <ul className="space-y-3">
          {apps.map((app) => (
            <li key={app.id}>
              <Card>
                <CardContent className="flex flex-col gap-3 p-5 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="font-semibold">{app.job_vacancies?.title}</p>
                    <p className="text-sm text-muted-foreground">
                      {app.job_vacancies?.employer_profiles?.company_name}
                    </p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      Applied {new Date(app.applied_at).toLocaleDateString('en-PH')}
                      {app.match_score != null && (
                        <> · Match {Math.round(app.match_score * 100)}%</>
                      )}
                    </p>
                  </div>
                  <StatusBadge status={app.status} />
                </CardContent>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </DashboardLayout>
  )
}

export default MyApplications
