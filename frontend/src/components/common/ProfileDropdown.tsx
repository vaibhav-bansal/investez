import { useState, useEffect, useRef } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { googleLogout } from '../../api/portfolio'
import ConfirmDialog from './ConfirmDialog'

interface User {
  id: number
  google_id?: string
  email: string
  name: string
  profile_picture?: string
}

interface ProfileDropdownProps {
  onGoogleLogout: () => void
  currentUser?: User
}

export default function ProfileDropdown({ onGoogleLogout, currentUser }: ProfileDropdownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false)
  const [isLoggingOut, setIsLoggingOut] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const queryClient = useQueryClient()

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen])

  const handleGoogleLogout = async () => {
    setIsLoggingOut(true)
    try {
      await googleLogout()
      queryClient.clear()
      setShowLogoutConfirm(false)
      setIsOpen(false)
      onGoogleLogout()
    } catch (error) {
      console.error('Google logout failed:', error)
    } finally {
      setIsLoggingOut(false)
    }
  }

  return (
    <>
      <div className="relative" ref={dropdownRef}>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 overflow-hidden"
          title="Profile"
        >
          {currentUser?.profile_picture ? (
            <img src={currentUser.profile_picture} alt={currentUser.name} className="w-full h-full object-cover" />
          ) : (
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
              />
            </svg>
          )}
        </button>

        {isOpen && (
          <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
            {currentUser ? (
              <>
                <div className="px-4 py-3 border-b border-gray-200">
                  <p className="text-sm font-medium text-gray-900">
                    {currentUser.name}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {currentUser.email}
                  </p>
                </div>

                <button
                  onClick={() => {
                    setShowLogoutConfirm(true)
                    setIsOpen(false)
                  }}
                  className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                >
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                    />
                  </svg>
                  Logout
                </button>
              </>
            ) : (
              <div className="px-4 py-3 text-sm text-gray-500">
                Profile not available
              </div>
            )}
          </div>
        )}
      </div>

      {currentUser && (
        <ConfirmDialog
          isOpen={showLogoutConfirm}
          title="Logout"
          message="Are you sure you want to logout? You will need to sign in with Google again to access the application."
          confirmText={isLoggingOut ? 'Logging out...' : 'Logout'}
          cancelText="Cancel"
          isDestructive={true}
          onConfirm={handleGoogleLogout}
          onCancel={() => setShowLogoutConfirm(false)}
        />
      )}
    </>
  )
}
