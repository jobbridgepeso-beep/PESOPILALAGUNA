import ResourceListPage from '@/pages/shared/ResourceListPage'
import { employmentColumns } from '@/pages/staff/managementColumns'

export default function EmploymentMonitoring() {
  return (
    <ResourceListPage
      role="admin"
      title="Employment Monitoring"
      description="Employment records"
      endpoint="/api/admin/employment"
      columns={employmentColumns}
      queryKey={['admin-employment']}
    />
  )
}
