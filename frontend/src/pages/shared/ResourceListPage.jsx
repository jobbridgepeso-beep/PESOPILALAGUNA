import { useQuery } from '@tanstack/react-query'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import LoadingPage from '@/components/ui/LoadingPage'
import DataTable from '@/components/shared/DataTable'
import axiosInstance from '@/api/axiosInstance'

export default function ResourceListPage({
  role,
  title,
  description,
  endpoint,
  columns,
  queryKey,
}) {
  const { data, isLoading } = useQuery({
    queryKey: queryKey || [endpoint],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get(endpoint)
      return res.data || []
    },
  })

  return (
    <DashboardLayout title={title} description={description}>
      <PageHeader title={title} description={description} />
      {isLoading ? <LoadingPage /> : <DataTable columns={columns} rows={data} />}
    </DashboardLayout>
  )
}
