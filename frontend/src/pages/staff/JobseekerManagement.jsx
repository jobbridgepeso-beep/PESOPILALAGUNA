import ResourceListPage from '@/pages/shared/ResourceListPage'
import { jobseekerColumns } from './managementColumns'

export default function JobseekerManagement() {
  return (
    <ResourceListPage
      role="staff"
      title="Jobseeker Management"
      description="Registered jobseekers in Pila, Laguna"
      endpoint="/api/staff/jobseekers"
      columns={jobseekerColumns}
      queryKey={['staff-jobseekers']}
    />
  )
}
