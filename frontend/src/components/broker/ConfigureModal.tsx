import { type Broker } from '../../api/portfolio'

interface ConfigureModalProps {
  isOpen: boolean
  broker: Broker | null
  apiKey: string
  apiSecret: string
  error: string
  isSaving: boolean
  onSave: (e: React.FormEvent) => void
  onCancel: () => void
  onApiKeyChange: (value: string) => void
  onApiSecretChange: (value: string) => void
}

export default function ConfigureModal({
  isOpen,
  broker,
  apiKey,
  apiSecret,
  error,
  isSaving,
  onSave,
  onCancel,
  onApiKeyChange,
  onApiSecretChange,
}: ConfigureModalProps) {
  if (!isOpen || !broker) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onCancel} />
      <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex justify-between items-center p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            Configure {broker.name}
          </h2>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
          >
            &times;
          </button>
        </div>

        <form onSubmit={onSave} className="p-6 space-y-4">
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {broker.broker_id === 'groww' ? (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  TOTP Token
                </label>
                <input
                  type="text"
                  value={apiKey}
                  onChange={(e) => onApiKeyChange(e.target.value)}
                  placeholder="Enter your TOTP Token (API Key from Groww)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Found in Groww app &rarr; Settings &rarr; API & Access
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  TOTP QR Code Secret
                </label>
                <input
                  type="password"
                  value={apiSecret}
                  onChange={(e) => onApiSecretChange(e.target.value)}
                  placeholder="Enter your TOTP Secret (from QR code)"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Scan the QR code in Groww with an authenticator app to get the secret
                </p>
              </div>
            </>
          ) : (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  API Key
                </label>
                <input
                  type="text"
                  value={apiKey}
                  onChange={(e) => onApiKeyChange(e.target.value)}
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
                  onChange={(e) => onApiSecretChange(e.target.value)}
                  placeholder="Enter your API secret"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
            </>
          )}

          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={isSaving}
              className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {isSaving ? 'Saving...' : 'Save Credentials'}
            </button>
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-sm font-medium text-gray-700 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
