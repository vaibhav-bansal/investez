import { useEffect, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchAuthStatus, sendAuthCallback, googleLogout, fetchCurrentUser } from './api/portfolio'
import Dashboard from './pages/Dashboard'
import GoogleLogin from './components/auth/GoogleLogin'
import BrokerManagementHome from './components/broker/BrokerManagementHome'
import Header from './components/layout/Header'

export default function App() {
  const queryClient = useQueryClient()
  const [callbackStatus, setCallbackStatus] = useState<'idle' | 'processing' | 'error'>('idle')
  const [callbackError, setCallbackError] = useState('')
  const [lastUpdated, setLastUpdated] = useState<string | null>(null)

  const handleGoogleLoginSuccess = async () => {
    try {
      // Small delay to ensure cookie is set in browser
      await new Promise(resolve => setTimeout(resolve, 100))

      // Invalidate and refetch queries to update UI
      await queryClient.invalidateQueries({ queryKey: ['auth-status'] })
      await queryClient.invalidateQueries({ queryKey: ['current-user'] })
      await queryClient.refetchQueries({ queryKey: ['auth-status'], type: 'active' })
    } catch (error) {
      console.error('Failed to update auth state:', error)
    }
  }

  const handleGoogleLoginError = (error: string) => {
    alert(`Login failed: ${error}`)
  }

  const handleLogout = async () => {
    try {
      await googleLogout()
      queryClient.clear()
      window.location.reload()
    } catch (error) {
      console.error('Logout failed:', error)
    }
  }

  const handleDataUpdate = (timestamp: string) => {
    setLastUpdated(timestamp)
  }

  // Handle Kite OAuth callback
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const requestToken = params.get('request_token')
    const status = params.get('status')

    if (requestToken && status === 'success') {
      setCallbackStatus('processing')

      sendAuthCallback(requestToken)
        .then((response) => {
          if (response.success) {
            window.history.replaceState({}, '', '/')
            queryClient.invalidateQueries({ queryKey: ['auth-status'] })
            queryClient.invalidateQueries({ queryKey: ['brokers'] })
            setCallbackStatus('idle')
          } else {
            setCallbackStatus('error')
            setCallbackError(response.error || 'Authentication failed')
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

  const isUserAuthenticated = authStatus?.data?.user_authenticated ?? false

  // Fetch current user data when user is authenticated
  const { data: currentUserData } = useQuery({
    queryKey: ['current-user'],
    queryFn: fetchCurrentUser,
    enabled: isUserAuthenticated,
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

  const isBrokerAuthenticated = authStatus?.data?.broker_authenticated ?? false

  return (
    <div className="min-h-screen bg-gray-50">
      {isUserAuthenticated && (
        <Header
          isUserAuthenticated={isUserAuthenticated}
          isBrokerAuthenticated={isBrokerAuthenticated}
          onGoogleLogout={handleLogout}
          lastUpdated={lastUpdated}
          currentUser={currentUserData?.data}
        />
      )}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {!isUserAuthenticated ? (
          <GoogleLogin onSuccess={handleGoogleLoginSuccess} onError={handleGoogleLoginError} />
        ) : !isBrokerAuthenticated ? (
          <BrokerManagementHome />
        ) : (
          <Dashboard onDataUpdate={handleDataUpdate} />
        )}
      </main>
    </div>
  )
}
