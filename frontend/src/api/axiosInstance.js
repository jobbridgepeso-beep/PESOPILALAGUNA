import axios from 'axios'
import { useAuthStore } from '@/store/authStore'

/**
 * Axios instance pre-configured with the backend base URL.
 * JWT interceptors attach the access token to every request and
 * handle silent token refresh on 401 responses (Requirement 2.2).
 */
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  withCredentials: true, // send httpOnly refresh-token cookie automatically
  headers: {
    'Content-Type': 'application/json',
  },
})

// ── Request interceptor ──────────────────────────────────────────────────────
// Attach the current access token from Zustand auth store before every request.
axiosInstance.interceptors.request.use(
  (config) => {
    const accessToken = useAuthStore.getState().accessToken
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// ── Response interceptor ─────────────────────────────────────────────────────
// On 401: attempt silent token refresh, then retry the original request once.
// On 403: redirect to the user's role dashboard (Requirement 3.2).
let isRefreshing = false
let failedQueue = []

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token)
    }
  })
  failedQueue = []
}

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Queue subsequent 401s while a refresh is in flight
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            return axiosInstance(originalRequest)
          })
          .catch((err) => Promise.reject(err))
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const { data } = await axiosInstance.post('/api/auth/refresh')
        const newToken = data?.data?.access_token

        if (newToken) {
          useAuthStore.getState().setAccessToken(newToken)
          axiosInstance.defaults.headers.common.Authorization = `Bearer ${newToken}`
          processQueue(null, newToken)
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return axiosInstance(originalRequest)
        }
      } catch (refreshError) {
        processQueue(refreshError, null)
        // Refresh failed — clear auth state and redirect to login
        useAuthStore.getState().clearAuth()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    if (error.response?.status === 403) {
      // Redirect to the user's own role dashboard
      const role = useAuthStore.getState().role
      if (role) {
        window.location.href = `/${role}/dashboard`
      }
    }

    return Promise.reject(error)
  },
)

export default axiosInstance
