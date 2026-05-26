import ResourceListPage from '@/pages/shared/ResourceListPage'
import { employerColumns } from './managementColumns'

export default function EmployerManagement() {
  return (
    <ResourceListPage
      role="staff"
      title="Employer Management"
      description="Registered employers"
      endpoint="/api/staff/employers"
      columns={employerColumns}
      queryKey={['staff-employers']}
    />
  )
}
