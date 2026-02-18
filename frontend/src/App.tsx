import { useEffect, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { fetchAuthStatus, sendAuthCallback, googleLogout, fetchCurrentUser, fetchLoginUrl } from './api/portfolio'
import Dashboard from './pages/Dashboard'
import Connections from './pages/Connections'
import GoogleLogin from './components/auth/GoogleLogin'
import Header from './components/layout/Header'

export default function App() {
  const queryClient = useQueryClient()
  const [callbackStatus, setCallbackStatus] = useState<'idle' | 'processing' | 'error'>('idle')
  const [callbackError, setCallbackError] = useState('')
  const [isRedirecting, setIsRedirecting] = useState(false)
  const [currentPage, setCurrentPage] = useState<'connections' | 'portfolio'>('connections')

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
            // Clear re-auth flag after successful callback
            sessionStorage.removeItem('kite_reauth_required')
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

  // Handle automatic re-authentication when token expires
  useEffect(() => {
    const checkReauthRequired = async () => {
      const reauthRequired = sessionStorage.getItem('kite_reauth_required')
      if (reauthRequired === 'true' && !isRedirecting) {
        setIsRedirecting(true)
        try {
          // Get fresh OAuth login URL (same flow as clicking Authenticate button)
          const response = await fetchLoginUrl()
          if (response.success && response.data?.login_url) {
            // Wait 2 seconds so user can read the message before redirecting
            await new Promise(resolve => setTimeout(resolve, 2000))
            // Redirect to Kite OAuth
            window.location.href = response.data.login_url
          } else {
            // If we can't get login URL, clear flag and show error
            sessionStorage.removeItem('kite_reauth_required')
            setIsRedirecting(false)
          }
        } catch (err) {
          // Clear flag on error
          sessionStorage.removeItem('kite_reauth_required')
          setIsRedirecting(false)
        }
      }
    }

    checkReauthRequired()
  }, []) // Empty deps - only run once on mount

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

  if (isRedirecting) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-gray-500 mb-2">Your Kite session has expired</div>
          <div className="text-gray-400">Redirecting to login...</div>
        </div>
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

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      {isUserAuthenticated && (
        <Header
          isUserAuthenticated={isUserAuthenticated}
          onGoogleLogout={handleLogout}
          currentUser={currentUserData?.data}
          currentPage={currentPage}
          onPageChange={setCurrentPage}
        />
      )}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {!isUserAuthenticated ? (
          <GoogleLogin onSuccess={handleGoogleLoginSuccess} onError={handleGoogleLoginError} />
        ) : currentPage === 'connections' ? (
          <Connections onNavigateToPortfolio={() => setCurrentPage('portfolio')} />
        ) : (
          <Dashboard onNavigateToConnections={() => setCurrentPage('connections')} />
        )}
      </main>
    </div>
  )
}
