import axiosInstance from './axiosInstance'

export const getPendingVacancies = () =>
  axiosInstance.get('/api/staff/vacancies/pending').then((r) => r.data)
export const approveVacancy = (id) =>
  axiosInstance.patch(`/api/staff/vacancies/${id}/approve`).then((r) => r.data)
export const rejectVacancy = (id, reason) =>
  axiosInstance.patch(`/api/staff/vacancies/${id}/reject`, { reason }).then((r) => r.data)
