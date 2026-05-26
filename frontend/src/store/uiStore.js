import { create } from 'zustand'

/**
 * Zustand UI store.
 *
 * Manages global UI state such as sidebar collapse and loading overlays.
 */
export const useUIStore = create((set) => ({
  /** Whether the sidebar is collapsed (mobile / narrow viewport) */
  sidebarCollapsed: false,

  /** Toggle sidebar open/closed */
  toggleSidebar: () =>
    set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

  /** Set sidebar state explicitly */
  setSidebarCollapsed: (collapsed) => set({ sidebarCollapsed: collapsed }),

  /** Global full-screen loading overlay (e.g., during file uploads) */
  globalLoading: false,
  setGlobalLoading: (loading) => set({ globalLoading: loading }),
}))
