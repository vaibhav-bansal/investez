import { useState, useMemo, useEffect } from 'react'
import toast from 'react-hot-toast'
import { useQuery } from '@tanstack/react-query'
import { format } from 'date-fns'
import { usePortfolioData } from '../hooks/usePortfolioData'
import { fetchBrokers, type Broker } from '../api/portfolio'
import PortfolioSummary from '../components/portfolio/PortfolioSummary'
import HoldingsTable from '../components/portfolio/HoldingsTable'
import MFHoldingsTable from '../components/portfolio/MFHoldingsTable'
import AllocationCharts from '../components/charts/AllocationCharts'
import BrokerFilter from '../components/portfolio/BrokerFilter'
import { calculateFilteredSummary, calculateAllocation } from '../utils/portfolioCalculations'
import type { Holding, MFHolding } from '../types/portfolio'

interface DashboardProps {
  onNavigateToConnections?: () => void
}

export default function Dashboard({ onNavigateToConnections }: DashboardProps) {
  const { data: brokersData } = useQuery({
    queryKey: ['brokers'],
    queryFn: fetchBrokers,
  })
  const [selectedBrokers, setSelectedBrokers] = useState<string[]>(['kite', 'groww'])
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<string | null>(null)

  const brokers = brokersData?.data?.brokers || []
  const hasAuthenticatedBroker = brokers.some((b: Broker) => b.status === 'authenticated')

  // Fetch portfolio data with progressive loading
  const {
    holdings,
    mfHoldings,
    isLoadingCore,
    error,
    tokenExpired,
    refetch,
  } = usePortfolioData({
    enabled: hasAuthenticatedBroker,
  })

  // Set lastUpdated time when data first loads
  useEffect(() => {
    if ((holdings || mfHoldings) && !lastUpdated && !isLoadingCore) {
      setLastUpdated(new Date().toISOString())
    }
  }, [holdings, mfHoldings, isLoadingCore, lastUpdated])

  // Get unique brokers from both stock and MF holdings
  const availableBrokers = useMemo(() => {
    if (!holdings && !mfHoldings) return []
    const brokers = new Set<string>()
    holdings?.forEach((h: Holding) => brokers.add(h.broker))
    mfHoldings?.forEach((m: MFHolding) => brokers.add(m.broker))
    return Array.from(brokers)
  }, [holdings, mfHoldings])

  // Filter holdings by selected brokers
  const filteredHoldings = useMemo(() => {
    if (!holdings) return []
    return holdings.filter((h: Holding) => selectedBrokers.includes(h.broker))
  }, [holdings, selectedBrokers])

  // Filter MF holdings by selected brokers
  const filteredMFHoldings = useMemo(() => {
    if (!mfHoldings) return []
    return mfHoldings.filter((m: MFHolding) => selectedBrokers.includes(m.broker))
  }, [mfHoldings, selectedBrokers])

  // Calculate filtered summary and allocation
  const filteredSummary = useMemo(() => {
    return calculateFilteredSummary(filteredHoldings, filteredMFHoldings)
  }, [filteredHoldings, filteredMFHoldings])

  const filteredAllocation = useMemo(() => {
    return calculateAllocation(filteredHoldings, filteredMFHoldings)
  }, [filteredHoldings, filteredMFHoldings])

  // Merge same stocks from different brokers
  const mergedHoldings = useMemo(() => {
    const merged = new Map<string, Holding>()

    for (const holding of filteredHoldings) {
      const key = `${holding.symbol}-${holding.exchange}`

      if (merged.has(key)) {
        const existing = merged.get(key)!
        // Merge quantities and recalculate
        const totalQty = existing.quantity + holding.quantity
        const totalInvested = existing.invested + holding.invested
        const totalValue = existing.value + holding.value
        const avgPrice = totalInvested / totalQty

        merged.set(key, {
          ...existing,
          quantity: totalQty,
          avg_price: avgPrice,
          value: totalValue,
          invested: totalInvested,
          pnl: totalValue - totalInvested,
          pnl_percent: ((totalValue - totalInvested) / totalInvested) * 100,
          broker: selectedBrokers.length > 1 ? 'multiple' : holding.broker,
        })
      } else {
        merged.set(key, { ...holding })
      }
    }

    return Array.from(merged.values())
  }, [filteredHoldings, selectedBrokers])

  // Check if no broker is authenticated - show empty state immediately (no loading)
  if (!hasAuthenticatedBroker) {
    return (
      <div className="flex flex-col items-center justify-center py-20 px-4">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
          <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          No Broker Connected
        </h2>
        <p className="text-gray-600 text-center mb-6 max-w-md">
          Connect your broker account to view your portfolio holdings, mutual funds, and allocation analysis.
        </p>
        <button
          onClick={onNavigateToConnections}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
        >
          Go to Connections
        </button>
      </div>
    )
  }

  // Handle errors
  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">
          Failed to load portfolio. Please check your broker connection.
        </p>
      </div>
    )
  }

  // Handle token expiry
  if (tokenExpired) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-700">
          Your broker session has expired. Please reconnect your broker.
        </p>
        <button
          onClick={onNavigateToConnections}
          className="mt-2 px-3 py-1 text-sm font-medium text-yellow-700 bg-yellow-100 rounded hover:bg-yellow-200"
        >
          Reconnect
        </button>
      </div>
    )
  }

  const handleBrokerToggle = (broker: string) => {
    setSelectedBrokers(prev => {
      if (prev.includes(broker)) {
        // Prevent deselecting the last broker
        if (prev.length === 1) {
          toast.error('At least one broker must be selected')
          return prev
        }
        return prev.filter(b => b !== broker)
      }
      return [...prev, broker]
    })
  }

  const handleRefresh = async () => {
    setIsRefreshing(true)
    toast.success('Portfolio refresh initiated')
    try {
      await refetch()
      setLastUpdated(new Date().toISOString())
    } catch (error) {
      toast.error('Failed to refresh portfolio')
    } finally {
      setTimeout(() => setIsRefreshing(false), 500)
    }
  }

  return (
    <div className="space-y-6">
      {/* Broker Filter and Refresh - only show when data is loaded */}
      {availableBrokers.length > 0 && !isLoadingCore && (
        <div className="flex items-center justify-between">
          <BrokerFilter
            availableBrokers={availableBrokers}
            selectedBrokers={selectedBrokers}
            onToggle={handleBrokerToggle}
          />
          <div className="flex items-center gap-3">
            {lastUpdated && (
              <p className="text-xs text-gray-400">
                Updated: {format(new Date(lastUpdated), 'd MMM yyyy, h:mm a')}
              </p>
            )}
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              title="Refresh"
            >
              <svg
                className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
            </button>
          </div>
        </div>
      )}

      <PortfolioSummary summary={filteredSummary} isLoading={isRefreshing || isLoadingCore} />

      <AllocationCharts
        allocation={filteredAllocation}
        totalValue={filteredSummary.total_value}
        isLoading={isRefreshing || isLoadingCore}
      />

      <div className="grid grid-cols-1 gap-6">
        <HoldingsTable holdings={mergedHoldings} isLoading={isRefreshing || isLoadingCore} />
        {filteredMFHoldings.length > 0 && (
          <MFHoldingsTable holdings={filteredMFHoldings} isLoading={isRefreshing || isLoadingCore} />
        )}
      </div>
    </div>
  )
}
