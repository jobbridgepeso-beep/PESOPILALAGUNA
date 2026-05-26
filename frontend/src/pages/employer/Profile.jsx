import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import DashboardLayout from '@/components/common/DashboardLayout'
import PageHeader from '@/components/ui/PageHeader'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Label from '@/components/ui/Label'
import LoadingPage from '@/components/ui/LoadingPage'
import { Card, CardContent } from '@/components/ui/Card'
import { getProfile, updateProfile } from '@/api/employerApi'

function Profile() {
  const qc = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ['employer-profile'],
    queryFn: async () => (await getProfile()).data,
  })
  const [form, setForm] = useState({})

  useEffect(() => {
    if (data) {
      setForm({
        company_name: data.company_name || '',
        industry: data.industry || '',
        phone: data.phone || '',
        address: data.address || '',
        website: data.website || '',
        description: data.description || '',
      })
    }
  }, [data])

  const mutation = useMutation({
    mutationFn: () => updateProfile(form),
    onSuccess: (res) => {
      if (res.success) {
        toast.success('Company profile saved')
        qc.invalidateQueries({ queryKey: ['employer-profile'] })
      } else toast.error(res.message)
    },
  })

  return (
    <DashboardLayout title="Company Profile" description="Your employer information">
      <PageHeader title="Company profile" description="Visible to jobseekers on your vacancies." />
      {isLoading ? (
        <LoadingPage />
      ) : (
        <Card className="max-w-2xl">
          <CardContent className="form-stack pt-6">
            <div>
              <Label htmlFor="company_name" required>Company name</Label>
              <Input
                id="company_name"
                value={form.company_name || ''}
                onChange={(e) => setForm({ ...form, company_name: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="industry">Industry</Label>
              <Input
                id="industry"
                value={form.industry || ''}
                onChange={(e) => setForm({ ...form, industry: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="phone">Phone</Label>
              <Input
                id="phone"
                value={form.phone || ''}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="address">Address</Label>
              <Input
                id="address"
                value={form.address || ''}
                onChange={(e) => setForm({ ...form, address: e.target.value })}
              />
            </div>
            <div>
              <Label htmlFor="description">Description</Label>
              <textarea
                id="description"
                rows={4}
                className="w-full rounded-md border border-input px-4 py-2 text-sm"
                value={form.description || ''}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
              />
            </div>
            <Button onClick={() => mutation.mutate()} disabled={mutation.isPending}>
              Save company profile
            </Button>
          </CardContent>
        </Card>
      )}
    </DashboardLayout>
  )
}

export default Profile
