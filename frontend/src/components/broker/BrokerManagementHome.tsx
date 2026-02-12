import { useState } from 'react'
import BrokerConfigModal from './BrokerConfigModal'

export default function BrokerManagementHome() {
  const [showConfigModal, setShowConfigModal] = useState(false)

  const handleOpenModal = () => {
    setShowConfigModal(true)
  }

  return (
    <>
      <div className="flex flex-col items-center justify-center py-20">
        <h2 className="text-2xl font-semibold text-gray-900 mb-2 text-center">
          Get Started with InvestEz
        </h2>
        <p className="text-gray-600 mb-8 text-center max-w-lg">
          Configure your broker credentials and connect to view your portfolio holdings and analysis.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl w-full px-4">
          <div
            onClick={handleOpenModal}
            className="bg-white rounded-lg shadow-sm border-2 border-gray-200 hover:border-blue-500 p-6 cursor-pointer transition-all hover:shadow-md"
          >
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </div>

            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Configure Brokers
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Add your broker API credentials to enable portfolio access. Your credentials are encrypted and stored securely.
            </p>
            <div className="flex items-center text-blue-600 text-sm font-medium">
              Configure now
              <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>

          <div
            onClick={handleOpenModal}
            className="bg-white rounded-lg shadow-sm border-2 border-gray-200 hover:border-green-500 p-6 cursor-pointer transition-all hover:shadow-md"
          >
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 10V3L4 14h7v7l9-11h-7z"
                />
              </svg>
            </div>

            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Authenticate
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              Connect to your broker to access real-time portfolio data and holdings. Authentication required after configuring credentials.
            </p>
            <div className="flex items-center text-green-600 text-sm font-medium">
              Authenticate now
              <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </div>
        </div>

        <p className="text-xs text-gray-500 mt-8 text-center max-w-lg">
          Currently supported: Zerodha Kite. More brokers coming soon.
        </p>
      </div>

      <BrokerConfigModal
        isOpen={showConfigModal}
        onClose={() => setShowConfigModal(false)}
      />
    </>
  )
}
