import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import LoadingPage from '@/components/ui/LoadingPage'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import { Card, CardContent } from '@/components/ui/Card'
import axiosInstance from '@/api/axiosInstance'
import { useState, useEffect } from 'react'

export default function SettingsPage({ role, canEdit = false }) {
  const qc = useQueryClient()
  const base = `/api/${role}`
  const [values, setValues] = useState({})

  const { data, isLoading } = useQuery({
    queryKey: [`${role}-settings`],
    queryFn: async () => {
      const { data: res } = await axiosInstance.get(`${base}/settings`)
      return res.data || []
    },
  })

  useEffect(() => {
    if (data) {
      const map = {}
      data.forEach((s) => {
        map[s.key] = s.value
      })
      setValues(map)
    }
  }, [data])

  const save = useMutation({
    mutationFn: () =>
      axiosInstance.put(`${base}/settings`, {
        settings: Object.entries(values).map(([key, value]) => ({ key, value })),
      }),
    onSuccess: (res) => {
      if (res.data?.success) toast.success('Settings saved')
      else toast.error(res.data?.message)
      qc.invalidateQueries({ queryKey: [`${role}-settings`] })
    },
  })

  return (
    <DashboardLayout title="Settings" description="System configuration">
      <PageHeader
        title="Settings"
        description={
          canEdit
            ? 'Administrator can update platform settings (saved to Supabase).'
            : 'View current platform settings.'
        }
      />
      {isLoading ? (
        <LoadingPage />
      ) : (
        <Card className="max-w-2xl">
          <CardContent className="form-stack pt-6">
            {(data || []).map((s) => (
              <div key={s.key}>
                <label className="mb-1 block text-sm font-semibold">{s.key}</label>
                <p className="mb-2 text-xs text-muted-foreground">{s.description}</p>
                <Input
                  value={values[s.key] ?? ''}
                  readOnly={!canEdit}
                  onChange={(e) =>
                    setValues({ ...values, [s.key]: e.target.value })
                  }
                />
              </div>
            ))}
            {canEdit && (
              <Button onClick={() => save.mutate()} disabled={save.isPending}>
                Save settings
              </Button>
            )}
          </CardContent>
        </Card>
      )}
    </DashboardLayout>
  )
}
