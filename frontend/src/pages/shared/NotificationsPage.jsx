import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import LoadingPage from '@/components/ui/LoadingPage'
import EmptyState from '@/components/shared/EmptyState'
import { Card, CardContent } from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import axiosInstance from '@/api/axiosInstance'

export default function NotificationsPage({ role, title = 'Notifications' }) {
  const qc = useQueryClient()
  const base = `/api/${role}`

  const { data, isLoading } = useQuery({
    queryKey: [`${role}-notifications`],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get(`${base}/notifications`)
      return res.data
    },
  })

  const canMarkRead = role === 'jobseeker' || role === 'employer'

  const markRead = useMutation({
    mutationFn: (id) => axiosInstance.patch(`${base}/notifications/${id}/read`),
    onSuccess: () => qc.invalidateQueries({ queryKey: [`${role}-notifications`] }),
  })

  const items = data?.items || []

  return (
    <DashboardLayout title={title} description="In-app notifications from PESO JobBridge">
      <PageHeader
        title={title}
        description={
          data?.unread_count
            ? `${data.unread_count} unread notification(s)`
            : 'All caught up'
        }
      />
      {isLoading ? (
        <LoadingPage />
      ) : !items.length ? (
        <EmptyState message="No notifications yet." />
      ) : (
        <ul className="space-y-3">
          {items.map((n) => (
            <li key={n.id}>
              <Card className={!n.is_read ? 'border-l-4 border-l-gov-gold' : ''}>
                <CardContent className="flex flex-col gap-2 p-5 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="font-semibold text-foreground">{n.title}</p>
                    <p className="text-sm text-muted-foreground">{n.body}</p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {new Date(n.created_at).toLocaleString('en-PH')}
                    </p>
                  </div>
                  {!n.is_read && canMarkRead && (
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => markRead.mutate(n.id)}
                    >
                      Mark read
                    </Button>
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
