import ResourceListPage from '@/pages/shared/ResourceListPage'
import { interviewColumns } from './managementColumns'

export default function InterviewOversight() {
  return (
    <ResourceListPage
      role="staff"
      title="Interview Oversight"
      description="Scheduled interviews across employers"
      endpoint="/api/staff/interviews"
      columns={interviewColumns}
      queryKey={['staff-interviews']}
    />
  )
}
