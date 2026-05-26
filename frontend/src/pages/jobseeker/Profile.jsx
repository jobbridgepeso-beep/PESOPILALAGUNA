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
import { getProfile, updateProfile } from '@/api/jobseekerApi'

function Profile() {
  const qc = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ['jobseeker-profile'],
    queryFn: async () => {
      const res = await getProfile()
      return res.data
    },
  })

  const [form, setForm] = useState({})

  useEffect(() => {
    if (data) {
      setForm({
        first_name: data.first_name || '',
        last_name: data.last_name || '',
        phone: data.phone || '',
        address: data.address || '',
        skills: (data.skills || []).join(', '),
      })
    }
  }, [data])

  const mutation = useMutation({
    mutationFn: () =>
      updateProfile({
        ...form,
        skills: form.skills
          ? form.skills.split(',').map((s) => s.trim()).filter(Boolean)
          : [],
      }),
    onSuccess: (res) => {
      if (res.success) {
        toast.success('Profile saved to database')
        qc.invalidateQueries({ queryKey: ['jobseeker-profile'] })
      } else toast.error(res.message)
    },
    onError: (e) => toast.error(e.response?.data?.message || 'Save failed'),
  })

  return (
    <DashboardLayout title="My Profile" description="Your jobseeker information for PESO Pila">
      <PageHeader
        title="Profile"
        description="Update your details for better job matching. All changes are saved to Supabase."
      />
      {isLoading ? (
        <LoadingPage />
      ) : (
        <Card className="max-w-2xl">
          <CardContent className="form-stack pt-6">
            <div className="grid gap-5 sm:grid-cols-2">
              <div>
                <Label htmlFor="first_name">First name</Label>
                <Input
                  id="first_name"
                  value={form.first_name || ''}
                  onChange={(e) => setForm({ ...form, first_name: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="last_name">Last name</Label>
                <Input
                  id="last_name"
                  value={form.last_name || ''}
                  onChange={(e) => setForm({ ...form, last_name: e.target.value })}
                />
              </div>
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
              <Label htmlFor="skills">Skills (comma-separated)</Label>
              <Input
                id="skills"
                placeholder="e.g. customer service, Microsoft Office"
                value={form.skills || ''}
                onChange={(e) => setForm({ ...form, skills: e.target.value })}
              />
            </div>
            <Button
              onClick={() => mutation.mutate()}
              disabled={mutation.isPending}
              className="w-full sm:w-auto"
            >
              {mutation.isPending ? 'Saving…' : 'Save profile'}
            </Button>
          </CardContent>
        </Card>
      )}
    </DashboardLayout>
  )
}

export default Profile
