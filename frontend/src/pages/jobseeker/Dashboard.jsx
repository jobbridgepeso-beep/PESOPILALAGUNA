import { useQuery } from '@tanstack/react-query'
import axiosInstance from '@/api/axiosInstance'
import DashboardLayout from '@/components/common/DashboardLayout'

function StatCard({ label, value }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-1 text-3xl font-bold text-slate-800">{value}</p>
    </div>
  )
}

function JobseekerDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['jobseeker-dashboard'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/jobseeker/dashboard')
      return res.data
    },
  })

  return (
    <DashboardLayout title="Jobseeker Dashboard">
      {isLoading ? (
        <p className="text-slate-500">Loading…</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <StatCard label="My applications" value={data?.applications?.total ?? 0} />
          <StatCard label="Pending" value={data?.applications?.pending ?? 0} />
          <StatCard label="Active job openings" value={data?.active_jobs ?? 0} />
        </div>
      )}
    </DashboardLayout>
  )
}

export default JobseekerDashboard
