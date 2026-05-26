import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import LoadingPage from '@/components/ui/LoadingPage'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Label from '@/components/ui/Label'
import StatusBadge from '@/components/ui/StatusBadge'
import { Card, CardContent } from '@/components/ui/Card'
import axiosInstance from '@/api/axiosInstance'

export default function JobFairManagement() {
  const qc = useQueryClient()
  const [form, setForm] = useState({
    title: '',
    event_date: '',
    start_time: '',
    end_time: '',
    venue: '',
    description: '',
  })

  const { data, isLoading } = useQuery({
    queryKey: ['staff-job-fairs'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/staff/job-fairs')
      return res.data || []
    },
  })

  const create = useMutation({
    mutationFn: () => axiosInstance.post('/api/staff/job-fairs', form),
    onSuccess: (res) => {
      if (res.data?.success) {
        toast.success('Job fair created')
        setForm({ title: '', event_date: '', start_time: '', end_time: '', venue: '', description: '' })
        qc.invalidateQueries({ queryKey: ['staff-job-fairs'] })
      } else toast.error(res.data?.message)
    },
  })

  return (
    <DashboardLayout title="Job Fair Management" description="Create and manage job fairs">
      <PageHeader title="Job fair management" description="Schedule job fairs for Pila, Laguna." />
      <Card className="mb-6 max-w-2xl">
        <CardContent className="form-stack pt-6">
          <div>
            <Label required>Title</Label>
            <Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <Label required>Event date</Label>
              <Input type="date" value={form.event_date} onChange={(e) => setForm({ ...form, event_date: e.target.value })} />
            </div>
            <div>
              <Label required>Venue</Label>
              <Input value={form.venue} onChange={(e) => setForm({ ...form, venue: e.target.value })} />
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <Label required>Start time</Label>
              <Input type="time" value={form.start_time} onChange={(e) => setForm({ ...form, start_time: e.target.value })} />
            </div>
            <div>
              <Label required>End time</Label>
              <Input type="time" value={form.end_time} onChange={(e) => setForm({ ...form, end_time: e.target.value })} />
            </div>
          </div>
          <Button onClick={() => create.mutate()} disabled={create.isPending}>
            Create job fair
          </Button>
        </CardContent>
      </Card>
      {isLoading ? (
        <LoadingPage />
      ) : (
        <ul className="space-y-3">
          {(data || []).map((fair) => (
            <li key={fair.id}>
              <Card>
                <CardContent className="flex flex-wrap items-center justify-between gap-2 p-5">
                  <div>
                    <p className="font-semibold">{fair.title}</p>
                    <p className="text-sm text-muted-foreground">
                      {fair.event_date} · {fair.venue}
                    </p>
                  </div>
                  <StatusBadge status={fair.status} />
                </CardContent>
              </Card>
            </li>
          ))}
        </ul>
      )}
    </DashboardLayout>
  )
}
