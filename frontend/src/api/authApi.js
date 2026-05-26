import axiosInstance from './axiosInstance'

export async function login(email, password) {
  const { data } = await axiosInstance.post('/api/auth/login', { email, password })
  return data
}

export async function register(payload) {
  const { data } = await axiosInstance.post('/api/auth/register', payload)
  return data
}

export async function verifyOtp(email, otp) {
  const { data } = await axiosInstance.post('/api/auth/verify-otp', { email, otp })
  return data
}

export async function resendOtp(email, purpose = 'registration') {
  const { data } = await axiosInstance.post('/api/auth/resend-otp', { email, purpose })
  return data
}

export async function forgotPassword(email) {
  const { data } = await axiosInstance.post('/api/auth/forgot-password', { email })
  return data
}

export async function resetPassword(email, otp, password) {
  const { data } = await axiosInstance.post('/api/auth/reset-password', {
    email,
    otp,
    password,
  })
  return data
}

export async function logout() {
  const { data } = await axiosInstance.post('/api/auth/logout')
  return data
}
