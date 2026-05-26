import ResourceListPage from '@/pages/shared/ResourceListPage'
import { vacancyColumns } from '@/pages/staff/managementColumns'

export default function VacancyManagement() {
  return (
    <ResourceListPage
      role="admin"
      title="Job Vacancy Management"
      description="All vacancies"
      endpoint="/api/admin/vacancies"
      columns={vacancyColumns}
      queryKey={['admin-vacancies']}
    />
  )
}
