import { create } from 'zustand'

/**
 * Zustand notification store.
 *
 * Holds in-app notifications received via Socket.io and tracks the
 * unread count displayed in the NotificationBell component.
 *
 * Requirements: 14.3, 14.4
 */
export const useNotificationStore = create((set, get) => ({
  /** Array of notification objects from the server */
  notifications: [],
  /** Count of notifications where is_read === false */
  unreadCount: 0,

  /**
   * Replace the full notification list (e.g., after fetching from API).
   * @param {Array} notifications
   */
  setAll: (notifications) =>
    set({
      notifications,
      unreadCount: notifications.filter((n) => !n.is_read).length,
    }),

  /**
   * Prepend a new real-time notification from Socket.io.
   * @param {object} notification
   */
  addNotification: (notification) =>
    set((state) => ({
      notifications: [notification, ...state.notifications],
      unreadCount: state.unreadCount + (notification.is_read ? 0 : 1),
    })),

  /**
   * Mark a single notification as read and decrement the unread count.
   * @param {string} id - notification UUID
   */
  markRead: (id) =>
    set((state) => {
      const notifications = state.notifications.map((n) =>
        n.id === id ? { ...n, is_read: true } : n,
      )
      return {
        notifications,
        unreadCount: notifications.filter((n) => !n.is_read).length,
      }
    }),

  /**
   * Mark all notifications as read.
   */
  markAllRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, is_read: true })),
      unreadCount: 0,
    })),

  /**
   * Clear all notifications (e.g., on logout).
   */
  clearNotifications: () => set({ notifications: [], unreadCount: 0 }),
}))
