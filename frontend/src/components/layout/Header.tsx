import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { format } from 'date-fns'
import ProfileDropdown from '../common/ProfileDropdown'

interface User {
  id: number
  google_id: string
  email: string
  name: string
  profile_picture?: string
}

interface HeaderProps {
  isUserAuthenticated?: boolean
  isBrokerAuthenticated?: boolean
  onGoogleLogout: () => void
  lastUpdated?: string | null
  currentUser?: User
}

export default function Header({
  isUserAuthenticated = false,
  isBrokerAuthenticated = false,
  onGoogleLogout,
  lastUpdated,
  currentUser
}: HeaderProps) {
  const queryClient = useQueryClient()
  const [isRefreshing, setIsRefreshing] = useState(false)

  const handleRefresh = async () => {
    setIsRefreshing(true)
    try {
      await queryClient.invalidateQueries({ queryKey: ['portfolio'] })
      await queryClient.invalidateQueries({ queryKey: ['auth-status'] })
    } finally {
      setTimeout(() => setIsRefreshing(false), 500)
    }
  }

  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">
              InvestEz
            </h1>
            <p className="text-sm text-gray-500">Portfolio Dashboard</p>
          </div>

          {isUserAuthenticated && (
            <div className="flex items-center gap-3">
              {isBrokerAuthenticated && lastUpdated && (
                <p className="text-xs text-gray-400 mr-2">
                  Updated: {format(new Date(lastUpdated), 'd MMM yyyy, h:mm a')}
                </p>
              )}

              {isBrokerAuthenticated && (
                <button
                  onClick={handleRefresh}
                  disabled={isRefreshing}
                  className="flex items-center justify-center w-10 h-10 rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Refresh"
                >
                  <svg
                    className={`w-5 h-5 ${isRefreshing ? 'animate-spin' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                    />
                  </svg>
                </button>
              )}

              <ProfileDropdown
                isBrokerAuthenticated={isBrokerAuthenticated}
                onGoogleLogout={onGoogleLogout}
                currentUser={currentUser}
              />
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
