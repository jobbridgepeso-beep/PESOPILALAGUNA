import ResourceListPage from '@/pages/shared/ResourceListPage'
import { auditColumns } from '@/pages/staff/managementColumns'

export default function AuditTrail() {
  return (
    <ResourceListPage
      role="admin"
      title="Audit Trail"
      description="System activity log"
      endpoint="/api/admin/audit-trail"
      columns={auditColumns}
      queryKey={['admin-audit']}
    />
  )
}
