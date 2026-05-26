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

function AdminDashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-dashboard'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/admin/dashboard')
      return res.data
    },
  })

  return (
    <DashboardLayout title="Admin Dashboard">
      {isLoading ? (
        <p className="text-slate-500">Loading…</p>
      ) : (
        <>
          <div className="mb-6 grid gap-4 sm:grid-cols-3">
            <StatCard label="Staff accounts" value={data?.staff_total ?? 0} />
            <StatCard label="Active staff" value={data?.staff_active ?? 0} />
            <StatCard label="Jobseekers" value={data?.total_jobseekers ?? 0} />
          </div>
          <div className="rounded-lg border border-slate-200 bg-white p-5">
            <h2 className="mb-3 font-semibold text-slate-800">Recent audit trail</h2>
            {(data?.recent_audit || []).length === 0 ? (
              <p className="text-sm text-slate-500">No audit entries yet.</p>
            ) : (
              <ul className="space-y-2 text-sm">
                {data.recent_audit.map((row) => (
                  <li key={row.id} className="flex justify-between border-b border-slate-100 py-2">
                    <span>
                      {row.action_type} · {row.actor_role}
                    </span>
                    <span className="text-slate-400">
                      {new Date(row.created_at).toLocaleString()}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </>
      )}
    </DashboardLayout>
  )
}

export default AdminDashboard
