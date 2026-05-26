import ResourceListPage from '@/pages/shared/ResourceListPage'
import { jobseekerColumns } from '@/pages/staff/managementColumns'

export default function JobseekerManagement() {
  return (
    <ResourceListPage
      role="admin"
      title="Jobseeker Management"
      description="All registered jobseekers"
      endpoint="/api/admin/jobseekers"
      columns={jobseekerColumns}
      queryKey={['admin-jobseekers']}
    />
  )
}
