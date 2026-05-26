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
import StatusBadge from '@/components/ui/StatusBadge'
import { Card, CardContent } from '@/components/ui/Card'
import axiosInstance from '@/api/axiosInstance'

export default function StaffManagement() {
  const qc = useQueryClient()
  const [email, setEmail] = useState('')
  const [tempPw, setTempPw] = useState(null)

  const { data, isLoading } = useQuery({
    queryKey: ['admin-staff'],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get('/api/admin/staff')
      return res.data || []
    },
  })

  const create = useMutation({
    mutationFn: () => axiosInstance.post('/api/admin/staff', { email }),
    onSuccess: (res) => {
      if (res.data?.success) {
        toast.success('Staff account created')
        setTempPw(res.data.data?.temporary_password)
        setEmail('')
        qc.invalidateQueries({ queryKey: ['admin-staff'] })
      }
    },
  })

  const toggle = useMutation({
    mutationFn: ({ id, is_active }) =>
      axiosInstance.patch(`/api/admin/staff/${id}/activate`, { is_active }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-staff'] }),
  })

  const columns = [
    { key: 'email', label: 'Email' },
    {
      key: 'status',
      label: 'Status',
      render: (r) => <StatusBadge status={r.is_active ? 'active' : 'inactive'} />,
    },
    {
      key: 'actions',
      label: 'Actions',
      render: (r) => (
        <Button
          size="sm"
          variant="secondary"
          onClick={() => toggle.mutate({ id: r.id, is_active: !r.is_active })}
        >
          {r.is_active ? 'Deactivate' : 'Activate'}
        </Button>
      ),
    },
  ]

  return (
    <DashboardLayout title="Staff Management" description="PESO staff accounts">
      <PageHeader title="Staff management" description="Create and manage PESO staff logins." />
      <Card className="mb-6 max-w-md">
        <CardContent className="form-stack pt-6">
          <div>
            <Label required>Staff email</Label>
            <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <Button onClick={() => create.mutate()} disabled={create.isPending || !email}>
            Create staff account
          </Button>
          {tempPw && (
            <p className="rounded-md bg-muted p-3 text-sm">
              Temporary password (share securely):{' '}
              <strong className="font-mono">{tempPw}</strong>
            </p>
          )}
        </CardContent>
      </Card>
      {isLoading ? <LoadingPage /> : <DataTable columns={columns} rows={data} />}
    </DashboardLayout>
  )
}
