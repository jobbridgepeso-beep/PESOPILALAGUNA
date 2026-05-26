import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import LoadingPage from '@/components/ui/LoadingPage'
import DataTable from '@/components/shared/DataTable'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Label from '@/components/ui/Label'
import { Card, CardContent } from '@/components/ui/Card'
import StatusBadge from '@/components/ui/StatusBadge'
import axiosInstance from '@/api/axiosInstance'

export default function Interviews() {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    application_id: '',
    scheduled_at: '',
    location: '',
    meeting_link: '',
  })

  const { data, isLoading } = useQuery({
    queryKey: ['employer-interviews'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/employer/interviews')
      return res.data || []
    },
  })

  const schedule = useMutation({
    mutationFn: () => axiosInstance.post('/api/employer/interviews', form),
    onSuccess: (res) => {
      if (res.data?.success) {
        toast.success('Interview scheduled')
        setForm({ application_id: '', scheduled_at: '', location: '', meeting_link: '' })
        qc.invalidateQueries({ queryKey: ['employer-interviews'] })
      } else toast.error(res.data?.message)
    },
  })

  const columns = [
    {
      key: 'applicant',
      label: 'Applicant',
      render: (r) => {
        const p = r.job_applications?.jobseeker_profiles
        return p ? `${p.first_name} ${p.last_name}` : '—'
      },
    },
    {
      key: 'when',
      label: 'Scheduled',
      render: (r) =>
        r.scheduled_at ? new Date(r.scheduled_at).toLocaleString('en-PH') : '—',
    },
    { key: 'location', label: 'Location' },
    { key: 'status', label: 'Status', render: (r) => <StatusBadge status={r.status} /> },
  ]

  return (
    <DashboardLayout title="Interview Management" description="Schedule and view interviews">
      <PageHeader title="Interviews" description="Schedule interviews for shortlisted applicants." />
      <Card className="mb-6 max-w-xl">
        <CardContent className="form-stack pt-6">
          <div>
            <Label>Application ID</Label>
            <Input
              value={form.application_id}
              onChange={(e) => setForm({ ...form, application_id: e.target.value })}
              placeholder="From applicant list"
            />
          </div>
          <div>
            <Label>Date & time (ISO)</Label>
            <Input
              type="datetime-local"
              value={form.scheduled_at}
              onChange={(e) =>
                setForm({ ...form, scheduled_at: new Date(e.target.value).toISOString() })
              }
            />
          </div>
          <div>
            <Label>Location</Label>
            <Input
              value={form.location}
              onChange={(e) => setForm({ ...form, location: e.target.value })}
            />
          </div>
          <Button onClick={() => schedule.mutate()} disabled={schedule.isPending}>
            Schedule interview
          </Button>
        </CardContent>
      </Card>
      {isLoading ? <LoadingPage /> : <DataTable columns={columns} rows={data} />}
    </DashboardLayout>
  )
}
