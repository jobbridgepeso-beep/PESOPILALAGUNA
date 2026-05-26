import ResourceListPage from '@/pages/shared/ResourceListPage'
import { lmiColumns } from '@/pages/staff/managementColumns'

export default function LMIReports() {
  return (
    <ResourceListPage
      role="admin"
      title="LMI Reports"
      description="Labor market intelligence"
      endpoint="/api/admin/lmi-reports"
      columns={lmiColumns}
      queryKey={['admin-lmi']}
    />
  )
}
