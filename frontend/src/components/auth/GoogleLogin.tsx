import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchGoogleAuthUrl } from '../../api/portfolio'

interface GoogleLoginProps {
  onSuccess: (token: string) => void
  onError: (error: string) => void
}

export default function GoogleLogin({ onSuccess, onError }: GoogleLoginProps) {
  const [isAuthenticating, setIsAuthenticating] = useState(false)

  const { data: authData, isLoading, error } = useQuery({
    queryKey: ['google-auth-url'],
    queryFn: fetchGoogleAuthUrl,
  })

  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) {
        return
      }

      if (event.data.type === 'GOOGLE_AUTH_SUCCESS') {
        setIsAuthenticating(false)
        onSuccess(event.data.token)
      } else if (event.data.type === 'GOOGLE_AUTH_ERROR') {
        setIsAuthenticating(false)
        onError(event.data.error || 'Authentication failed')
      }
    }

    window.addEventListener('message', handleMessage)
    return () => window.removeEventListener('message', handleMessage)
  }, [onSuccess, onError])

  const handleGoogleLogin = () => {
    if (!authData?.data?.auth_url) return

    setIsAuthenticating(true)

    const width = 500
    const height = 600
    const left = window.screen.width / 2 - width / 2
    const top = window.screen.height / 2 - height / 2

    window.open(
      authData.data.auth_url,
      'Google Login',
      `width=${width},height=${height},left=${left},top=${top}`
    )
  }

  const isButtonDisabled = isLoading || !authData?.data?.auth_url || !!error || isAuthenticating

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center max-w-md w-full">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
            />
          </svg>
        </div>

        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Welcome to InvestEz
        </h2>
        <p className="text-gray-600 mb-6">
          Sign in with your Google account to get started with portfolio analysis.
        </p>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-700">
              {authData?.error || 'Failed to load login. Please check your configuration.'}
            </p>
          </div>
        )}

        <button
          onClick={handleGoogleLogin}
          disabled={isButtonDisabled}
          className="w-full bg-white border border-gray-300 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          {isAuthenticating ? 'Authenticating...' : 'Sign in with Google'}
        </button>

        <p className="text-xs text-gray-500 mt-4">
          By signing in, you agree to our terms and privacy policy
        </p>
      </div>
    </div>
  )
}
