import { Navigate } from 'react-router-dom'
import { STAFF } from '@/config/modulePaths'

/** @deprecated Use Job Vacancy Management → Pending approval tab */
export default function VacancyApprovals() {
  return <Navigate to={`${STAFF.vacancies}?tab=pending`} replace />
}
