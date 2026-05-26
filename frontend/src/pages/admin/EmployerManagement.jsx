import ResourceListPage from '@/pages/shared/ResourceListPage'
import { employerColumns } from '@/pages/staff/managementColumns'

export default function EmployerManagement() {
  return (
    <ResourceListPage
      role="admin"
      title="Employer Management"
      description="All registered employers"
      endpoint="/api/admin/employers"
      columns={employerColumns}
      queryKey={['admin-employers']}
    />
  )
}
