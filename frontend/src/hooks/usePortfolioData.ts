import { useQuery } from '@tanstack/react-query'
import {
  fetchHoldings,
  fetchMFHoldings,
  fetchHoldingsQuotes,
  fetchMarketCapEnrichment,
  fetchMFDayChangeEnrichment,
} from '../api/portfolio'

interface UsePortfolioDataOptions {
  enabled?: boolean
}

/**
 * Hook to fetch portfolio data with progressive loading.
 *
 * Data flow:
 * 1. Core data (holdings + MF holdings) loads immediately (~5s)
 * 2. Enrichment data loads in parallel after core data arrives
 * 3. UI updates progressively as data arrives
 */
export function usePortfolioData(options?: UsePortfolioDataOptions) {
  const { enabled = true } = options || {}

  // Core data - fetched immediately, but not on remount
  const holdingsQuery = useQuery({
    queryKey: ['holdings'],
    queryFn: fetchHoldings,
    enabled,
    staleTime: Infinity, // Never consider data stale (prevents auto-refetch)
    gcTime: Infinity, // Keep data in cache forever
    retry: false,
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  const mfHoldingsQuery = useQuery({
    queryKey: ['mf-holdings'],
    queryFn: fetchMFHoldings,
    enabled,
    staleTime: Infinity,
    gcTime: Infinity,
    retry: false,
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  // Enrichment data - fetched after core data arrives
  const quotesQuery = useQuery({
    queryKey: ['holdings-quotes'],
    queryFn: fetchHoldingsQuotes,
    enabled: enabled && (holdingsQuery.data?.success || false),
    staleTime: Infinity,
    gcTime: Infinity,
    retry: false,
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  const marketCapQuery = useQuery({
    queryKey: ['market-cap'],
    queryFn: fetchMarketCapEnrichment,
    enabled: enabled && (holdingsQuery.data?.success || false),
    staleTime: Infinity,
    gcTime: Infinity,
    retry: false,
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  const mfDayChangeQuery = useQuery({
    queryKey: ['mf-day-change'],
    queryFn: fetchMFDayChangeEnrichment,
    enabled: enabled && (mfHoldingsQuery.data?.success || false),
    staleTime: Infinity,
    gcTime: Infinity,
    retry: false,
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  })

  // Check for token expiry errors
  const tokenExpired =
    (holdingsQuery.error as any)?.response?.data?.error_type === 'token_expired' ||
    (mfHoldingsQuery.error as any)?.response?.data?.error_type === 'token_expired'

  // Extract data from responses
  const holdings = holdingsQuery.data?.data || []
  const mfHoldings = mfHoldingsQuery.data?.data || []
  const quotesEnrichment = quotesQuery.data?.data || {}
  const marketCapEnrichment = marketCapQuery.data?.data || {}
  const mfDayChangeEnrichment = mfDayChangeQuery.data?.data || {}

  // Merge enrichment data
  const enrichedHoldings = holdings.map((h) => {
    const quotes = quotesEnrichment[h.symbol]
    const marketCap = marketCapEnrichment[h.symbol]

    // Get enriched current_price (from quotes API or original)
    const enrichedCurrentPrice = quotes?.last_price ?? h.current_price

    // Recalculate P&L and value if we got a new price from quotes
    if (quotes?.last_price !== undefined && quotes.last_price !== null) {
      const newValue = quotes.last_price * h.quantity
      const newPnL = (quotes.last_price - h.avg_price) * h.quantity
      const newPnLPercent = h.invested > 0 ? (newPnL / h.invested) * 100 : 0

      return {
        ...h,
        current_price: quotes.last_price,
        value: newValue,
        pnl: newPnL,
        pnl_percent: newPnLPercent,
        day_change: quotes.day_change ?? h.day_change,
        day_change_percent: quotes.day_change_percent ?? h.day_change_percent,
        market_cap_category: marketCap ?? h.market_cap_category,
      }
    }

    // No new price data, return original with market cap enrichment
    return {
      ...h,
      current_price: enrichedCurrentPrice,
      day_change: quotes?.day_change ?? h.day_change,
      day_change_percent: quotes?.day_change_percent ?? h.day_change_percent,
      market_cap_category: marketCap ?? h.market_cap_category,
    }
  })

  const enrichedMFHoldings = mfHoldings.map((mf) => {
    const dayChange = mfDayChangeEnrichment[mf.scheme_code]

    return {
      ...mf,
      // Apply day change enrichment
      day_change: dayChange?.day_change ?? mf.day_change,
      day_change_percent: dayChange?.day_change_percent ?? mf.day_change_percent,
    }
  })

  // Loading states
  const isLoadingCore = holdingsQuery.isLoading || mfHoldingsQuery.isLoading
  const isLoadingEnrichment = quotesQuery.isLoading || marketCapQuery.isLoading || mfDayChangeQuery.isLoading

  // Error states
  const error = holdingsQuery.error || mfHoldingsQuery.error

  return {
    // Data
    holdings: enrichedHoldings,
    mfHoldings: enrichedMFHoldings,
    rawHoldings: holdings,
    rawMFHoldings: mfHoldings,

    // Loading states
    isLoadingCore,
    isLoadingEnrichment,
    isLoading: isLoadingCore || isLoadingEnrichment,

    // Enrichment progress
    hasQuotes: !!quotesQuery.data,
    hasMarketCap: !!marketCapQuery.data,
    hasMFDayChange: !!mfDayChangeQuery.data,

    // Error handling
    error,
    tokenExpired,

    // Refetch functions
    refetch: () => {
      holdingsQuery.refetch()
      mfHoldingsQuery.refetch()
      quotesQuery.refetch()
      marketCapQuery.refetch()
      mfDayChangeQuery.refetch()
    },
  }
}
