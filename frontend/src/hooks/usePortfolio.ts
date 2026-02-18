import { useQuery } from '@tanstack/react-query'
import { fetchPortfolio } from '../api/portfolio'

interface UsePortfolioOptions {
  enabled?: boolean
}

export function usePortfolio(options?: UsePortfolioOptions) {
  const { enabled = true } = options || {}

  return useQuery({
    queryKey: ['portfolio'],
    queryFn: async () => {
      const response = await fetchPortfolio()

      // Check if token expired error
      if (!response.success && response.error_type === 'token_expired') {
        // Store flag to trigger re-authentication
        sessionStorage.setItem('kite_reauth_required', 'true')
        // Throw error so query knows it failed
        throw new Error(response.error || 'Token expired')
      }

      return response
    },
    enabled,
    refetchInterval: 60000,
    retry: false, // Don't retry on token expiry - let the redirect happen
  })
}
