import { useState } from 'react'
import { useQuery, useQueryClient, useMutation } from '@tanstack/react-query'
import {
  fetchBrokers,
  saveBrokerCredentials,
  deleteBrokerCredentials,
  fetchLoginUrl,
  authenticateGroww,
  logout,
  logoutGroww,
  logoutAllBrokers,
  type Broker,
} from '../api/portfolio'
import ConfirmDialog from '../components/common/ConfirmDialog'
import ConfigureModal from '../components/broker/ConfigureModal'

interface ConnectionsProps {
  onNavigateToPortfolio: () => void
}

export default function Connections({ onNavigateToPortfolio }: ConnectionsProps) {
  const queryClient = useQueryClient()
  const [configuringBroker, setConfiguringBroker] = useState<Broker | null>(null)
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
  })

  const saveMutation = useMutation({
    mutationFn: ({ brokerId, apiKey, apiSecret }: { brokerId: string; apiKey: string; apiSecret: string }) =>
      saveBrokerCredentials(brokerId, apiKey, apiSecret),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brokers'] })
      queryClient.invalidateQueries({ queryKey: ['auth-status'] })
      // Invalidate all portfolio queries when credentials are saved
      queryClient.invalidateQueries({ queryKey: ['holdings'] })
      queryClient.invalidateQueries({ queryKey: ['mf-holdings'] })
      queryClient.invalidateQueries({ queryKey: ['holdings-quotes'] })
      queryClient.invalidateQueries({ queryKey: ['market-cap'] })
      queryClient.invalidateQueries({ queryKey: ['mf-day-change'] })
      setConfiguringBroker(null)
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
      // Invalidate all portfolio queries when credentials are deleted
      queryClient.invalidateQueries({ queryKey: ['holdings'] })
      queryClient.invalidateQueries({ queryKey: ['mf-holdings'] })
      queryClient.invalidateQueries({ queryKey: ['holdings-quotes'] })
      queryClient.invalidateQueries({ queryKey: ['market-cap'] })
      queryClient.invalidateQueries({ queryKey: ['mf-day-change'] })
    },
  })

  const logoutMutation = useMutation({
    mutationFn: logout,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brokers'] })
      queryClient.invalidateQueries({ queryKey: ['auth-status'] })
      // Invalidate all portfolio queries
      queryClient.invalidateQueries({ queryKey: ['holdings'] })
      queryClient.invalidateQueries({ queryKey: ['mf-holdings'] })
      queryClient.invalidateQueries({ queryKey: ['holdings-quotes'] })
      queryClient.invalidateQueries({ queryKey: ['market-cap'] })
      queryClient.invalidateQueries({ queryKey: ['mf-day-change'] })
    },
  })

  const logoutGrowwMutation = useMutation({
    mutationFn: logoutGroww,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brokers'] })
      queryClient.invalidateQueries({ queryKey: ['auth-status'] })
      // Invalidate all portfolio queries
      queryClient.invalidateQueries({ queryKey: ['holdings'] })
      queryClient.invalidateQueries({ queryKey: ['mf-holdings'] })
      queryClient.invalidateQueries({ queryKey: ['holdings-quotes'] })
      queryClient.invalidateQueries({ queryKey: ['market-cap'] })
      queryClient.invalidateQueries({ queryKey: ['mf-day-change'] })
    },
  })

  const logoutAllMutation = useMutation({
    mutationFn: logoutAllBrokers,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brokers'] })
      queryClient.invalidateQueries({ queryKey: ['auth-status'] })
      // Invalidate all portfolio queries
      queryClient.invalidateQueries({ queryKey: ['holdings'] })
      queryClient.invalidateQueries({ queryKey: ['mf-holdings'] })
      queryClient.invalidateQueries({ queryKey: ['holdings-quotes'] })
      queryClient.invalidateQueries({ queryKey: ['market-cap'] })
      queryClient.invalidateQueries({ queryKey: ['mf-day-change'] })
    },
  })

  const authenticateGrowwMutation = useMutation({
    mutationFn: authenticateGroww,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brokers'] })
      queryClient.invalidateQueries({ queryKey: ['auth-status'] })
      // Invalidate all portfolio queries when broker is authenticated
      queryClient.invalidateQueries({ queryKey: ['holdings'] })
      queryClient.invalidateQueries({ queryKey: ['mf-holdings'] })
      queryClient.invalidateQueries({ queryKey: ['holdings-quotes'] })
      queryClient.invalidateQueries({ queryKey: ['market-cap'] })
      queryClient.invalidateQueries({ queryKey: ['mf-day-change'] })
      setError('')
    },
    onError: (err: any) => {
      setError(err.response?.data?.error || 'Failed to authenticate with Groww')
    },
  })

  const brokers = brokersData?.data?.brokers || []
  const hasAuthenticatedBrokers = brokers.some(b => b.status === 'authenticated')

  const handleConfigureClick = (broker: Broker) => {
    setConfiguringBroker(broker)
    setApiKey('')
    setApiSecret('')
    setError('')
  }

  const handleSaveCredentials = (e: React.FormEvent) => {
    e.preventDefault()
    if (!configuringBroker) return

    if (!apiKey.trim() || !apiSecret.trim()) {
      setError('API key and secret are required')
      return
    }

    saveMutation.mutate({
      brokerId: configuringBroker.broker_id,
      apiKey: apiKey.trim(),
      apiSecret: apiSecret.trim(),
    })
  }

  const handleCancelConfigure = () => {
    setConfiguringBroker(null)
    setApiKey('')
    setApiSecret('')
    setError('')
  }

  const handleAuthenticate = async (broker: Broker) => {
    setError('')

    if (broker.broker_id === 'kite') {
      try {
        const response = await fetchLoginUrl()
        if (response.success && response.data?.login_url) {
          window.location.href = response.data.login_url
        } else {
          setError(response.error || 'Failed to get login URL')
        }
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to authenticate with Kite')
      }
    } else if (broker.broker_id === 'groww') {
      authenticateGrowwMutation.mutate()
    } else {
      setError(`Authentication not supported for ${broker.name}`)
    }
  }

  const handleLogout = (broker: Broker) => {
    setActionBroker(broker)
    setShowLogoutConfirm(true)
  }

  const confirmLogout = () => {
    if (actionBroker?.broker_id === 'groww') {
      logoutGrowwMutation.mutate()
    } else {
      logoutMutation.mutate()
    }
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
      const isLoggingOut = broker.broker_id === 'groww' ? logoutGrowwMutation.isPending : logoutMutation.isPending
      return (
        <button
          onClick={() => handleLogout(broker)}
          disabled={isLoggingOut}
          className="px-4 py-2 text-sm font-medium text-red-600 border border-red-600 rounded-md hover:bg-red-50 disabled:opacity-50"
        >
          {isLoggingOut ? 'Logging out...' : 'Logout'}
        </button>
      )
    } else if (broker.status === 'configured') {
      const isAuthenticating = broker.broker_id === 'groww' && authenticateGrowwMutation.isPending
      return (
        <button
          onClick={() => handleAuthenticate(broker)}
          disabled={isAuthenticating}
          className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isAuthenticating ? 'Authenticating...' : 'Authenticate'}
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
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-semibold text-gray-900">
            Connections
          </h1>
          <button
            onClick={onNavigateToPortfolio}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            Portfolio Dashboard
          </button>
        </div>
        <p className="text-gray-600 mb-8">
          Connect your broker accounts to view your portfolio holdings and analysis.
        </p>

        {error && (
          <div className="mb-6 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {isLoading ? (
          <div className="text-center py-8 text-gray-500">Loading brokers...</div>
        ) : brokers.length === 0 ? (
          <p className="text-sm text-gray-500 py-4 text-center">No brokers available</p>
        ) : (
          <div className="space-y-4">
            {brokers.map((broker) => (
              <div
                key={broker.id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:border-gray-300 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-gray-900">{broker.name}</h3>
                      {getStatusBadge(broker.status)}
                    </div>
                    {broker.user_id && broker.broker_id === 'kite' && (
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
              </div>
            ))}
          </div>
        )}

        {hasAuthenticatedBrokers && (
          <div className="mt-10 pt-6 border-t border-gray-200">
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

      <ConfigureModal
        isOpen={configuringBroker !== null}
        broker={configuringBroker}
        apiKey={apiKey}
        apiSecret={apiSecret}
        error={error}
        isSaving={saveMutation.isPending}
        onSave={handleSaveCredentials}
        onCancel={handleCancelConfigure}
        onApiKeyChange={setApiKey}
        onApiSecretChange={setApiSecret}
      />

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
