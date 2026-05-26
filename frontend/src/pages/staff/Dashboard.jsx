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

function StaffDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['staff-dashboard'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/staff/dashboard')
      return res.data
    },
  })

  return (
    <DashboardLayout title="PESO Staff Dashboard">
      {isLoading ? (
        <p className="text-slate-500">Loading…</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <StatCard label="Registered jobseekers" value={data?.total_jobseekers ?? 0} />
          <StatCard label="Active vacancies" value={data?.active_vacancies ?? 0} />
          <StatCard label="Pending approvals" value={data?.pending_approvals ?? 0} />
          <StatCard label="Upcoming job fairs" value={data?.upcoming_job_fairs ?? 0} />
          <StatCard label="Pending programs" value={data?.pending_programs ?? 0} />
        </div>
      )}
    </DashboardLayout>
  )
}

export default StaffDashboard
