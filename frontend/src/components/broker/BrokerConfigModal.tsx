import { useState } from 'react'
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query'
import {
  fetchBrokers,
  saveBrokerCredentials,
  deleteBrokerCredentials,
  fetchLoginUrl,
  logout,
  logoutAllBrokers,
  type Broker,
} from '../../api/portfolio'
import ConfirmDialog from '../common/ConfirmDialog'

interface BrokerConfigModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function BrokerConfigModal({
  isOpen,
  onClose,
}: BrokerConfigModalProps) {
  const queryClient = useQueryClient()
  const [editingBroker, setEditingBroker] = useState<Broker | null>(null)
  const [apiKey, setApiKey] = useState('')
  const [apiSecret, setApiSecret] = useState('')
  const [error, setError] = useState('')

  // Confirm dialog states
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false)
  const [showLogoutAllConfirm, setShowLogoutAllConfirm] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [actionBroker, setActionBroker] = useState<Broker | null>(null)

  const { data: brokersData, isLoading } = useQuery({
    queryKey: ['brokers'],
    queryFn: fetchBrokers,
    enabled: isOpen,
  })

  const saveMutation = useMutation({
    mutationFn: ({ brokerId, apiKey, apiSecret }: { brokerId: string; apiKey: string; apiSecret: string }) =>
      saveBrokerCredentials(brokerId, apiKey, apiSecret),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brokers'] })
      queryClient.invalidateQueries({ queryKey: ['auth-status'] })
      setEditingBroker(null)
      setApiKey('')
      setApiSecret('')
      setError('')
    },
    onError: (err: any) => {
      setError(err.response?.data?.error || 'Failed to save credentials')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (brokerId: string) => deleteBrokerCredentials(brokerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brokers'] })
      queryClient.invalidateQueries({ queryKey: ['auth-status'] })
    },
  })

  const logoutMutation = useMutation({
    mutationFn: logout,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brokers'] })
      queryClient.invalidateQueries({ queryKey: ['auth-status'] })
      queryClient.invalidateQueries({ queryKey: ['portfolio'] })
      window.location.reload()
    },
  })

  const logoutAllMutation = useMutation({
    mutationFn: logoutAllBrokers,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brokers'] })
      queryClient.invalidateQueries({ queryKey: ['auth-status'] })
      queryClient.invalidateQueries({ queryKey: ['portfolio'] })
      window.location.reload()
    },
  })

  const brokers = brokersData?.data?.brokers || []
  const hasAuthenticatedBrokers = brokers.some(b => b.status === 'authenticated')

  const handleConfigureClick = (broker: Broker) => {
    setEditingBroker(broker)
    setApiKey('')
    setApiSecret('')
    setError('')
  }

  const handleSaveCredentials = (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingBroker) return

    if (!apiKey.trim() || !apiSecret.trim()) {
      setError('API key and secret are required')
      return
    }

    saveMutation.mutate({
      brokerId: editingBroker.broker_id,
      apiKey: apiKey.trim(),
      apiSecret: apiSecret.trim(),
    })
  }

  const handleCancelEdit = () => {
    setEditingBroker(null)
    setApiKey('')
    setApiSecret('')
    setError('')
  }

  const handleAuthenticate = async () => {
    try {
      const response = await fetchLoginUrl()
      if (response.success && response.data?.login_url) {
        window.location.href = response.data.login_url
      } else {
        setError(response.error || 'Failed to get login URL')
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to authenticate')
    }
  }

  const handleLogout = (broker: Broker) => {
    setActionBroker(broker)
    setShowLogoutConfirm(true)
  }

  const confirmLogout = () => {
    logoutMutation.mutate()
    setShowLogoutConfirm(false)
    setActionBroker(null)
  }

  const handleLogoutAll = () => {
    setShowLogoutAllConfirm(true)
  }

  const confirmLogoutAll = () => {
    logoutAllMutation.mutate()
    setShowLogoutAllConfirm(false)
  }

  const handleDelete = (broker: Broker) => {
    setActionBroker(broker)
    setShowDeleteConfirm(true)
  }

  const confirmDelete = () => {
    if (actionBroker) {
      deleteMutation.mutate(actionBroker.broker_id)
    }
    setShowDeleteConfirm(false)
    setActionBroker(null)
  }

  if (!isOpen) return null

  // Check if any confirm dialog is open
  const isConfirmDialogOpen = showLogoutConfirm || showLogoutAllConfirm || showDeleteConfirm

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'authenticated':
        return <span className="px-2 py-1 text-xs font-medium text-green-700 bg-green-100 rounded">Authenticated</span>
      case 'configured':
        return <span className="px-2 py-1 text-xs font-medium text-blue-700 bg-blue-100 rounded">Configured</span>
      default:
        return <span className="px-2 py-1 text-xs font-medium text-gray-700 bg-gray-100 rounded">Unconfigured</span>
    }
  }

  const getActionButton = (broker: Broker) => {
    if (broker.status === 'authenticated') {
      return (
        <button
          onClick={() => handleLogout(broker)}
          disabled={logoutMutation.isPending}
          className="px-4 py-2 text-sm font-medium text-red-600 border border-red-600 rounded-md hover:bg-red-50 disabled:opacity-50"
        >
          {logoutMutation.isPending ? 'Logging out...' : 'Logout'}
        </button>
      )
    } else if (broker.status === 'configured') {
      return (
        <button
          onClick={() => handleAuthenticate()}
          className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700"
        >
          Authenticate
        </button>
      )
    } else {
      return (
        <button
          onClick={() => handleConfigureClick(broker)}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
        >
          Configure
        </button>
      )
    }
  }

  return (
    <>
      {!isConfirmDialogOpen && (
      <div className="fixed inset-0 z-50 flex items-center justify-center">
        <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose} />
        <div className="relative bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] flex flex-col">
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            Manage Brokers
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
          >
            &times;
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {isLoading ? (
            <div className="text-center py-8 text-gray-500">Loading brokers...</div>
          ) : editingBroker ? (
            <div>
              <div className="mb-4">
                <button
                  onClick={handleCancelEdit}
                  className="text-sm text-gray-600 hover:text-gray-800 flex items-center"
                >
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                  Back to brokers
                </button>
              </div>

              <h3 className="text-lg font-semibold text-gray-900 mb-4">
                Configure {editingBroker.name}
              </h3>

              <form onSubmit={handleSaveCredentials} className="space-y-4">
                {error && (
                  <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                    <p className="text-sm text-red-700">{error}</p>
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    API Key
                  </label>
                  <input
                    type="text"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="Enter your API key"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    API Secret
                  </label>
                  <input
                    type="password"
                    value={apiSecret}
                    onChange={(e) => setApiSecret(e.target.value)}
                    placeholder="Enter your API secret"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    disabled={saveMutation.isPending}
                    className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    {saveMutation.isPending ? 'Saving...' : 'Save Credentials'}
                  </button>
                  <button
                    type="button"
                    onClick={handleCancelEdit}
                    className="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          ) : (
            <div className="space-y-3">
              {brokers.length === 0 ? (
                <p className="text-sm text-gray-500 py-4 text-center">
                  No brokers available
                </p>
              ) : (
                brokers.map((broker) => (
                  <div
                    key={broker.id}
                    className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-gray-300"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-medium text-gray-900">{broker.name}</h3>
                        {getStatusBadge(broker.status)}
                      </div>
                      {broker.user_id && (
                        <p className="text-sm text-gray-500">
                          Client ID: {broker.user_id}
                        </p>
                      )}
                    </div>

                    <div className="flex gap-2">
                      {getActionButton(broker)}
                      {broker.has_credentials && (
                        <button
                          onClick={() => handleDelete(broker)}
                          disabled={deleteMutation.isPending}
                          className="p-2 text-gray-400 hover:text-red-600"
                          title="Delete credentials"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                            />
                          </svg>
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}

              {hasAuthenticatedBrokers && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <button
                    onClick={handleLogoutAll}
                    disabled={logoutAllMutation.isPending}
                    className="w-full px-4 py-2 text-sm font-medium text-red-600 border border-red-600 rounded-md hover:bg-red-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {logoutAllMutation.isPending ? 'Logging out...' : 'Logout All Brokers'}
                  </button>
                  <p className="text-xs text-gray-500 mt-2 text-center">
                    This will end all broker sessions but keep you signed in with Google
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
        </div>
      </div>
      )}

      {/* Confirm Dialogs */}
      <ConfirmDialog
        isOpen={showLogoutConfirm}
        title="Logout Broker"
        message={`Are you sure you want to end your session with ${actionBroker?.name}?`}
        confirmText="Logout"
        cancelText="Cancel"
        onConfirm={confirmLogout}
        onCancel={() => {
          setShowLogoutConfirm(false)
          setActionBroker(null)
        }}
        isDestructive={true}
      />

      <ConfirmDialog
        isOpen={showLogoutAllConfirm}
        title="Logout All Brokers"
        message="Are you sure you want to logout from all brokers? You will need to authenticate again to access your portfolio."
        confirmText="Logout All"
        cancelText="Cancel"
        onConfirm={confirmLogoutAll}
        onCancel={() => setShowLogoutAllConfirm(false)}
        isDestructive={true}
      />

      <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="Delete Credentials"
        message={`Are you sure you want to delete your ${actionBroker?.name} credentials? You will need to add them again to reconnect.`}
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={confirmDelete}
        onCancel={() => {
          setShowDeleteConfirm(false)
          setActionBroker(null)
        }}
        isDestructive={true}
      />
    </>
  )
}
