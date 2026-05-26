import { useQuery } from '@tanstack/react-query'
import { Users, UserCog, Shield } from 'lucide-react'
import axiosInstance from '@/api/axiosInstance'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import StatCard from '@/components/ui/StatCard'
import AnimatedStatGrid from '@/components/ui/AnimatedStatGrid'
import LoadingPage from '@/components/ui/LoadingPage'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'

function AdminDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/admin/dashboard')
      return res.data
    },
  })

  return (
    <DashboardLayout
      title="Administrator Dashboard"
      description="System administration and oversight"
    >
      <PageHeader
        title="System overview"
        description="Staff accounts, platform activity, and audit trail for PESO Pila, Laguna."
      />

      {isLoading ? (
        <LoadingPage message="Loading dashboard…" />
      ) : (
        <div className="space-y-8">
          <AnimatedStatGrid>
            <StatCard
              label="Staff accounts"
              value={data?.staff_total ?? 0}
              icon={UserCog}
            />
            <StatCard
              label="Active staff"
              value={data?.staff_active ?? 0}
              icon={Users}
            />
            <StatCard
              label="Registered jobseekers"
              value={data?.total_jobseekers ?? 0}
              icon={Shield}
            />
          </AnimatedStatGrid>

          <Card>
            <CardHeader>
              <CardTitle>Recent audit trail</CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {(data?.recent_audit || []).length === 0 ? (
                <p className="px-6 py-8 text-center text-sm text-muted-foreground">
                  No audit entries recorded yet.
                </p>
              ) : (
                <ul className="divide-y divide-border">
                  {data.recent_audit.map((row) => (
                    <li
                      key={row.id}
                      className="flex flex-col gap-2 px-6 py-4 sm:flex-row sm:items-center sm:justify-between"
                    >
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-sm font-medium text-foreground">
                          {row.action_type.replace(/_/g, ' ')}
                        </span>
                        <Badge variant="muted">{row.actor_role}</Badge>
                      </div>
                      <time className="text-xs text-muted-foreground">
                        {new Date(row.created_at).toLocaleString('en-PH', {
                          dateStyle: 'medium',
                          timeStyle: 'short',
                        })}
                      </time>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </DashboardLayout>
  )
}

export default AdminDashboard
