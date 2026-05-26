import ResourceListPage from '@/pages/shared/ResourceListPage'
import { lmiColumns } from './managementColumns'

export default function LMIReports() {
  return (
    <ResourceListPage
      role="staff"
      title="LMI Reports"
      description="Labor market intelligence reports"
      endpoint="/api/staff/lmi-reports"
      columns={lmiColumns}
      queryKey={['staff-lmi']}
    />
  )
}
