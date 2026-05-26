import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import App from './App.jsx'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 1000 * 60 * 5,
      refetchOnWindowFocus: false,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
        <Toaster
          position="top-right"
          gutter={12}
          toastOptions={{
            duration: 4000,
            className: 'text-sm font-medium',
            style: {
              background: 'hsl(213 58% 18%)',
              color: '#fff',
              borderRadius: '0.375rem',
              padding: '12px 16px',
              boxShadow: '0 4px 12px rgb(0 0 0 / 0.15)',
            },
            success: {
              iconTheme: { primary: 'hsl(45 93% 47%)', secondary: 'hsl(213 58% 18%)' },
            },
            error: {
              style: { background: 'hsl(0 72% 45%)' },
            },
          }}
        />
      </BrowserRouter>
    </QueryClientProvider>
  </React.StrictMode>,
)
