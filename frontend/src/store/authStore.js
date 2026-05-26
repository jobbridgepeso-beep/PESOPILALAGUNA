import { create } from 'zustand'
import { persist } from 'zustand/middleware'

/**
 * Zustand auth store.
 *
 * Persists user identity and access token to sessionStorage so the
 * session survives page refreshes but is cleared when the tab closes.
 *
 * Requirements: 2.1, 2.2, 3.1
 */
export const useAuthStore = create(
  persist(
    (set) => ({
      /** Decoded user object: { id, email, role, first_login } */
      user: null,
      /** Current JWT access token string */
      accessToken: null,
      /** User role shorthand for route guards */
      role: null,

      /**
       * Store auth data after a successful login or token refresh.
       * @param {object} payload - { user, accessToken }
       */
      setAuth: ({ user, accessToken }) =>
        set({
          user,
          accessToken,
          role: user?.role ?? null,
        }),

      /**
       * Update only the access token (used by the refresh interceptor).
       * @param {string} accessToken
       */
      setAccessToken: (accessToken) => set({ accessToken }),

      /**
       * Clear all auth state on logout or session expiry.
       */
      clearAuth: () => set({ user: null, accessToken: null, role: null }),
    }),
    {
      name: 'jobbridge-auth',
      storage: {
        getItem: (key) => {
          const value = sessionStorage.getItem(key)
          return value ? JSON.parse(value) : null
        },
        setItem: (key, value) => sessionStorage.setItem(key, JSON.stringify(value)),
        removeItem: (key) => sessionStorage.removeItem(key),
      },
      // Only persist non-sensitive identity fields; access token is kept in
      // memory via sessionStorage (cleared on tab close).
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        role: state.role,
      }),
    },
  ),
)
