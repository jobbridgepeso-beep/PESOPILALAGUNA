import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Label from '@/components/ui/Label'
import { Card, CardContent } from '@/components/ui/Card'
import axiosInstance from '@/api/axiosInstance'

export default function AdminAnnouncements() {
  const [form, setForm] = useState({ title: '', body: '', audience: 'jobseeker' })

  const send = useMutation({
    mutationFn: () => axiosInstance.post('/api/admin/announcements', form),
    onSuccess: (res) => {
      if (res.data?.success) {
        toast.success(res.data.message || 'Announcement sent')
        setForm({ title: '', body: '', audience: 'jobseeker' })
      }
    },
  })

  return (
    <DashboardLayout title="Announcements" description="Broadcast to users">
      <PageHeader title="Announcements" description="Send platform-wide in-app notifications." />
      <Card className="max-w-xl">
        <CardContent className="form-stack pt-6">
          <div>
            <Label required>Title</Label>
            <Input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          </div>
          <div>
            <Label required>Message</Label>
            <textarea
              className="flex min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={form.body}
              onChange={(e) => setForm({ ...form, body: e.target.value })}
            />
          </div>
          <div>
            <Label>Target audience</Label>
            <select
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 text-sm"
              value={form.audience}
              onChange={(e) => setForm({ ...form, audience: e.target.value })}
            >
              <option value="jobseeker">Jobseekers</option>
              <option value="employer">Employers</option>
            </select>
          </div>
          <Button onClick={() => send.mutate()} disabled={send.isPending}>
            Send announcement
          </Button>
        </CardContent>
      </Card>
    </DashboardLayout>
  )
}
