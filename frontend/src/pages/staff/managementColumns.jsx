import StatusBadge from '@/components/ui/StatusBadge'

export const jobseekerColumns = [
  {
    key: 'name',
    label: 'Name',
    render: (r) => `${r.first_name || ''} ${r.last_name || ''}`.trim() || '—',
  },
  { key: 'phone', label: 'Phone' },
  { key: 'email', label: 'Email', render: (r) => r.users?.email || '—' },
  {
    key: 'active',
    label: 'Account',
    render: (r) => <StatusBadge status={r.users?.is_active ? 'active' : 'inactive'} />,
  },
]

export const employerColumns = [
  { key: 'company_name', label: 'Company' },
  { key: 'industry', label: 'Industry' },
  { key: 'phone', label: 'Phone' },
  { key: 'email', label: 'Email', render: (r) => r.users?.email || '—' },
]

export const vacancyColumns = [
  { key: 'title', label: 'Title' },
  {
    key: 'company',
    label: 'Employer',
    render: (r) => r.employer_profiles?.company_name || '—',
  },
  { key: 'status', label: 'Status', render: (r) => <StatusBadge status={r.status} /> },
]

export const interviewColumns = [
  {
    key: 'vacancy',
    label: 'Vacancy',
    render: (r) => r.job_applications?.job_vacancies?.title || '—',
  },
  {
    key: 'when',
    label: 'Scheduled',
    render: (r) =>
      r.scheduled_at ? new Date(r.scheduled_at).toLocaleString('en-PH') : '—',
  },
  { key: 'status', label: 'Status', render: (r) => <StatusBadge status={r.status} /> },
]

export const employmentColumns = [
  {
    key: 'seeker',
    label: 'Jobseeker',
    render: (r) =>
      `${r.jobseeker_profiles?.first_name || ''} ${r.jobseeker_profiles?.last_name || ''}`.trim(),
  },
  {
    key: 'employer',
    label: 'Employer',
    render: (r) => r.employer_profiles?.company_name || '—',
  },
  { key: 'position', label: 'Position' },
  { key: 'status', label: 'Status', render: (r) => <StatusBadge status={r.status} /> },
]

export const lmiColumns = [
  { key: 'title', label: 'Report' },
  {
    key: 'generated_at',
    label: 'Generated',
    render: (r) =>
      r.generated_at ? new Date(r.generated_at).toLocaleDateString('en-PH') : '—',
  },
  { key: 'status', label: 'Status', render: (r) => <StatusBadge status={r.status || 'active'} /> },
]

export const auditColumns = [
  { key: 'action_type', label: 'Action' },
  { key: 'actor_role', label: 'Role' },
  { key: 'resource_type', label: 'Resource' },
  {
    key: 'when',
    label: 'When',
    render: (r) =>
      r.created_at ? new Date(r.created_at).toLocaleString('en-PH') : '—',
  },
]
