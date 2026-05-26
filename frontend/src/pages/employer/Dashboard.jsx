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

function EmployerDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['employer-dashboard'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/employer/dashboard')
      return res.data
    },
  })

  return (
    <DashboardLayout title="Employer Dashboard">
      {isLoading ? (
        <p className="text-slate-500">Loading…</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Active vacancies" value={data?.active_vacancies ?? 0} />
          <StatCard label="Total applicants" value={data?.total_applicants ?? 0} />
          <StatCard label="Pending reviews" value={data?.pending_reviews ?? 0} />
          <StatCard label="Hired" value={data?.hired ?? 0} />
        </div>
      )}
    </DashboardLayout>
  )
}

export default EmployerDashboard
