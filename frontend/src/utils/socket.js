import { io } from 'socket.io-client'
import { useAuthStore } from '@/store/authStore'

/**
 * Socket.io-client singleton.
 *
 * The socket is created lazily on first call to getSocket() so that the
 * access token is available before the connection is established.
 *
 * Requirements: 14.1, 8.5
 */
let socket = null

/**
 * Return the shared Socket.io instance, creating it if necessary.
 * @returns {import('socket.io-client').Socket}
 */
export const getSocket = () => {
  if (socket) return socket

  const accessToken = useAuthStore.getState().accessToken
  const serverUrl = import.meta.env.VITE_SOCKET_URL || 'http://localhost:5000'

  socket = io(serverUrl, {
    auth: { token: accessToken },
    autoConnect: false,
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 2000,
    transports: ['websocket', 'polling'],
  })

  return socket
}

/**
 * Connect the socket (call after successful login).
 */
export const connectSocket = () => {
  const s = getSocket()
  if (!s.connected) {
    // Refresh the auth token before connecting
    const accessToken = useAuthStore.getState().accessToken
    s.auth = { token: accessToken }
    s.connect()
  }
}

/**
 * Disconnect and destroy the socket (call on logout).
 */
export const disconnectSocket = () => {
  if (socket) {
    socket.disconnect()
    socket = null
  }
}
