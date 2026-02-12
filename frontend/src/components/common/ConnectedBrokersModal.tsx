import { useState } from 'react'
import ConfirmDialog from './ConfirmDialog'

interface Broker {
  name: string
  broker_id: string
  user_id: string
  connected: boolean
}

interface ConnectedBrokersModalProps {
  isOpen: boolean
  brokers: Broker[]
  onClose: () => void
  onEndSession: (brokerId: string) => Promise<void>
}

export default function ConnectedBrokersModal({
  isOpen,
  brokers,
  onClose,
  onEndSession,
}: ConnectedBrokersModalProps) {
  const [confirmDialog, setConfirmDialog] = useState<{
    isOpen: boolean
    brokerId: string
    brokerName: string
  }>({ isOpen: false, brokerId: '', brokerName: '' })
  const [endingSession, setEndingSession] = useState<string | null>(null)

  if (!isOpen && !confirmDialog.isOpen) return null

  const handleEndSessionClick = (brokerId: string, brokerName: string) => {
    setConfirmDialog({ isOpen: true, brokerId, brokerName })
  }

  const handleCancelConfirm = () => {
    setConfirmDialog({ isOpen: false, brokerId: '', brokerName: '' })
  }

  const handleConfirmEndSession = async () => {
    if (!confirmDialog.brokerId) return

    setEndingSession(confirmDialog.brokerId)
    try {
      await onEndSession(confirmDialog.brokerId)
      setConfirmDialog({ isOpen: false, brokerId: '', brokerName: '' })
    } finally {
      setEndingSession(null)
    }
  }

  return (
    <>
      {isOpen && !confirmDialog.isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="fixed inset-0 bg-black bg-opacity-50" onClick={onClose} />

          <div className="relative bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Connected Brokers
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
            >
              &times;
            </button>
          </div>

          <div className="space-y-3">
            {brokers.length === 0 ? (
              <p className="text-sm text-gray-500 py-4 text-center">
                No brokers connected
              </p>
            ) : (
              brokers.map((broker) => (
                <div
                  key={broker.broker_id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg"
                >
                  <div>
                    <h3 className="font-medium text-gray-900">{broker.name}</h3>
                    <p className="text-sm text-gray-500">
                      User ID: {broker.user_id}
                    </p>
                    <p className="text-xs text-gray-400 mt-1">
                      Status:{' '}
                      <span
                        className={
                          broker.connected ? 'text-green-600' : 'text-red-600'
                        }
                      >
                        {broker.connected ? 'Connected' : 'Disconnected'}
                      </span>
                    </p>
                  </div>

                  {broker.connected && (
                    <button
                      onClick={() => handleEndSessionClick(broker.broker_id, broker.name)}
                      disabled={endingSession === broker.broker_id}
                      className="px-4 py-2 text-sm font-medium text-red-600 border border-red-600 rounded-md hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {endingSession === broker.broker_id
                        ? 'Ending...'
                        : 'End Session'}
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
        </div>
      )}

      <ConfirmDialog
        isOpen={confirmDialog.isOpen}
        title="End Broker Session"
        message={`Are you sure you want to end your session with ${confirmDialog.brokerName}? You will need to login again to access your portfolio.`}
        confirmText="End Session"
        cancelText="Cancel"
        isDestructive={true}
        onConfirm={handleConfirmEndSession}
        onCancel={handleCancelConfirm}
      />
    </>
  )
}
