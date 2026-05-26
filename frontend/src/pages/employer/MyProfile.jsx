import { useQuery } from '@tanstack/react-query'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import LoadingPage from '@/components/ui/LoadingPage'
import { Card, CardContent } from '@/components/ui/Card'
import StatusBadge from '@/components/ui/StatusBadge'
import axiosInstance from '@/api/axiosInstance'

export default function MyProfile() {
  const { data, isLoading } = useQuery({
    queryKey: ['employer-account'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/employer/account')
      return res.data
    },
  })

  return (
    <DashboardLayout title="My Profile" description="Your account information">
      <PageHeader title="My profile" description="Login account details for your employer access." />
      {isLoading ? (
        <LoadingPage />
      ) : (
        <Card className="max-w-lg">
          <CardContent className="space-y-4 pt-6">
            <div>
              <p className="text-xs font-semibold uppercase text-muted-foreground">Email</p>
              <p className="font-medium">{data?.email}</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase text-muted-foreground">Role</p>
              <p className="font-medium capitalize">{data?.role}</p>
            </div>
            <div className="flex items-center gap-2">
              <p className="text-xs font-semibold uppercase text-muted-foreground">Status</p>
              <StatusBadge status={data?.is_active ? 'active' : 'inactive'} />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase text-muted-foreground">Member since</p>
              <p className="text-sm">
                {data?.created_at
                  ? new Date(data.created_at).toLocaleDateString('en-PH')
                  : '—'}
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </DashboardLayout>
  )
}
