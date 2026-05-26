import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import LoadingPage from '@/components/ui/LoadingPage'
import DataTable from '@/components/shared/DataTable'
import PendingVacancyList from '@/components/staff/PendingVacancyList'
import { cn } from '@/utils/cn'
import axiosInstance from '@/api/axiosInstance'
import { vacancyColumns } from './managementColumns'

const TABS = [
  { id: 'all', label: 'All vacancies' },
  { id: 'pending', label: 'Pending approval' },
]

export default function VacancyManagement() {
  const [searchParams, setSearchParams] = useSearchParams()
  const tab = searchParams.get('tab') === 'pending' ? 'pending' : 'all'

  const { data, isLoading } = useQuery({
    queryKey: ['staff-vacancies'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/staff/vacancies')
      return res.data || []
    },
    enabled: tab === 'all',
  })

  return (
    <DashboardLayout
      title="Job Vacancy Management"
      description="Review and approve employer job postings"
    >
      <PageHeader
        title="Job vacancy management"
        description="View all vacancies or approve pending postings before they go live."
      />

      <div className="mb-6 flex flex-wrap gap-2 border-b border-border pb-2">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setSearchParams(t.id === 'all' ? {} : { tab: t.id })}
            className={cn(
              'rounded-md px-4 py-2 text-sm font-medium transition-colors',
              tab === t.id
                ? 'bg-primary text-primary-foreground'
                : 'text-muted-foreground hover:bg-muted',
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'pending' ? (
        <PendingVacancyList />
      ) : isLoading ? (
        <LoadingPage />
      ) : (
        <DataTable columns={vacancyColumns} rows={data} />
      )}
    </DashboardLayout>
  )
}
