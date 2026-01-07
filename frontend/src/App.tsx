import { useEffect, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { fetchAuthStatus } from './api/portfolio'
import Dashboard from './pages/Dashboard'
import AuthPrompt from './components/layout/AuthPrompt'
import Header from './components/layout/Header'

export default function App() {
  const queryClient = useQueryClient()
  const [callbackStatus, setCallbackStatus] = useState<'idle' | 'processing' | 'error'>('idle')
  const [callbackError, setCallbackError] = useState('')

  // Handle OAuth callback
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const requestToken = params.get('request_token')
    const status = params.get('status')

    if (requestToken && status === 'success') {
      setCallbackStatus('processing')

      axios.post('/api/auth/callback', { request_token: requestToken })
        .then((response) => {
          if (response.data.success) {
            // Clear URL params and refresh auth status
            window.history.replaceState({}, '', '/')
            queryClient.invalidateQueries({ queryKey: ['auth-status'] })
            setCallbackStatus('idle')
          } else {
            setCallbackStatus('error')
            setCallbackError(response.data.error || 'Authentication failed')
          }
        })
        .catch((err) => {
          setCallbackStatus('error')
          setCallbackError(err.message || 'Failed to authenticate')
        })
    }
  }, [queryClient])

  const { data: authStatus, isLoading } = useQuery({
    queryKey: ['auth-status'],
    queryFn: fetchAuthStatus,
  })

  if (callbackStatus === 'processing') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">Completing authentication...</div>
      </div>
    )
  }

  if (callbackStatus === 'error') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-700 mb-4">{callbackError}</p>
          <a href="/" className="text-blue-600 hover:underline">Try again</a>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-500">Loading...</div>
      </div>
    )
  }

  const isAuthenticated = authStatus?.data?.authenticated ?? false

  return (
    <div className="min-h-screen">
      <Header />
      <main className="max-w-7xl mx-auto px-4 py-6">
        {isAuthenticated ? <Dashboard /> : <AuthPrompt />}
      </main>
    </div>
  )
}
