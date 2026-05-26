import axiosInstance from './axiosInstance'

export const getProfile = () => axiosInstance.get('/api/jobseeker/profile').then((r) => r.data)
export const updateProfile = (data) =>
  axiosInstance.put('/api/jobseeker/profile', data).then((r) => r.data)
export const getJobs = () => axiosInstance.get('/api/jobseeker/jobs').then((r) => r.data)
export const applyToJob = (vacancyId, coverLetter) =>
  axiosInstance.post(`/api/jobseeker/jobs/${vacancyId}/apply`, { cover_letter: coverLetter }).then((r) => r.data)
export const getApplications = () =>
  axiosInstance.get('/api/jobseeker/applications').then((r) => r.data)
