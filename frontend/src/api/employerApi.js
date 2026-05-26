import axiosInstance from './axiosInstance'

export const getProfile = () => axiosInstance.get('/api/employer/profile').then((r) => r.data)
export const updateProfile = (data) =>
  axiosInstance.put('/api/employer/profile', data).then((r) => r.data)
export const getVacancies = () => axiosInstance.get('/api/employer/vacancies').then((r) => r.data)
export const createVacancy = (data) =>
  axiosInstance.post('/api/employer/vacancies', data).then((r) => r.data)
export const closeVacancy = (id) =>
  axiosInstance.delete(`/api/employer/vacancies/${id}`).then((r) => r.data)
export const getApplicants = (vacancyId) =>
  axiosInstance.get(`/api/employer/vacancies/${vacancyId}/applicants`).then((r) => r.data)
export const updateApplicationStatus = (applicationId, status) =>
  axiosInstance
    .patch(`/api/employer/applications/${applicationId}/status`, { status })
    .then((r) => r.data)
