import ResourceListPage from '@/pages/shared/ResourceListPage'
import { interviewColumns } from '@/pages/staff/managementColumns'

export default function InterviewOversight() {
  return (
    <ResourceListPage
      role="admin"
      title="Interview Oversight"
      description="Scheduled interviews"
      endpoint="/api/admin/interviews"
      columns={interviewColumns}
      queryKey={['admin-interviews']}
    />
  )
}
