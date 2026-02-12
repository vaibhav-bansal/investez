import { useQuery } from '@tanstack/react-query'
import { fetchLoginUrl } from '../../api/portfolio'

export default function AuthPrompt() {
  const { data: loginData, isLoading, error } = useQuery({
    queryKey: ['login-url'],
    queryFn: fetchLoginUrl,
  })

  const handleConnect = () => {
    if (loginData?.data?.login_url) {
      window.location.href = loginData.data.login_url
    }
  }

  const isButtonDisabled = isLoading || !loginData?.data?.login_url || !!error

  return (
    <div className="flex flex-col items-center justify-center py-20">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center max-w-md">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">
          Connect to Zerodha Kite
        </h2>
        <p className="text-gray-600 mb-6">
          Connect your Zerodha account to view your portfolio holdings and analysis.
        </p>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-700">
              {loginData?.error || 'Failed to load login URL. Please check your API configuration.'}
            </p>
          </div>
        )}

        <button
          onClick={handleConnect}
          disabled={isButtonDisabled}
          className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Loading...' : 'Connect to Kite'}
        </button>
      </div>
    </div>
  )
}
