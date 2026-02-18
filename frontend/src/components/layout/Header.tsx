import ProfileDropdown from '../common/ProfileDropdown'

interface User {
  id: number
  google_id?: string
  email: string
  name: string
  profile_picture?: string
}

interface HeaderProps {
  isUserAuthenticated?: boolean
  currentPage: 'connections' | 'portfolio'
  onGoogleLogout: () => void
  currentUser?: User
  onPageChange: (page: 'connections' | 'portfolio') => void
}

export default function Header({
  isUserAuthenticated = false,
  onGoogleLogout,
  currentUser,
  currentPage,
  onPageChange,
}: HeaderProps) {

  return (
    <header className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-gray-900">
              InvestEz
            </h1>
            {isUserAuthenticated && (
              <nav className="flex gap-6 mt-1">
                <button
                  onClick={() => onPageChange('connections')}
                  className={`text-sm font-medium transition-colors ${
                    currentPage === 'connections'
                      ? 'text-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Connections
                </button>
                <button
                  onClick={() => onPageChange('portfolio')}
                  className={`text-sm font-medium transition-colors ${
                    currentPage === 'portfolio'
                      ? 'text-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Portfolio
                </button>
              </nav>
            )}
          </div>

          {isUserAuthenticated && (
            <div className="flex items-center gap-3">
              <ProfileDropdown
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
