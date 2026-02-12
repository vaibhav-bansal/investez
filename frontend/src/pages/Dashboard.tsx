import { useState, useMemo, useEffect } from 'react'
import toast from 'react-hot-toast'
import { usePortfolio } from '../hooks/usePortfolio'
import PortfolioSummary from '../components/portfolio/PortfolioSummary'
import HoldingsTable from '../components/portfolio/HoldingsTable'
import MFHoldingsTable from '../components/portfolio/MFHoldingsTable'
import AllocationCharts from '../components/charts/AllocationCharts'
import BrokerFilter from '../components/portfolio/BrokerFilter'
import { calculateFilteredSummary, calculateAllocation } from '../utils/portfolioCalculations'
import type { Holding, MFHolding } from '../types/portfolio'

interface DashboardProps {
  onDataUpdate?: (timestamp: string) => void
}

export default function Dashboard({ onDataUpdate }: DashboardProps) {
  const { data, isLoading, error } = usePortfolio()
  const [selectedBrokers, setSelectedBrokers] = useState<string[]>(['kite', 'groww'])

  const portfolio = data?.data

  // Get unique brokers from both stock and MF holdings
  const availableBrokers = useMemo(() => {
    if (!portfolio?.holdings && !portfolio?.mf_holdings) return []
    const brokers = new Set<string>()
    portfolio?.holdings?.forEach((h: Holding) => brokers.add(h.broker))
    portfolio?.mf_holdings?.forEach((m: MFHolding) => brokers.add(m.broker))
    return Array.from(brokers)
  }, [portfolio?.holdings, portfolio?.mf_holdings])

  // Filter holdings by selected brokers
  const filteredHoldings = useMemo(() => {
    if (!portfolio?.holdings) return []
    return portfolio.holdings.filter((h: Holding) =>
      selectedBrokers.includes(h.broker)
    )
  }, [portfolio?.holdings, selectedBrokers])

  // Filter MF holdings by selected brokers
  const filteredMFHoldings = useMemo(() => {
    if (!portfolio?.mf_holdings) return []
    return portfolio.mf_holdings.filter((m: MFHolding) =>
      selectedBrokers.includes(m.broker)
    )
  }, [portfolio?.mf_holdings, selectedBrokers])

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

  // Notify parent about the timestamp (after render, not during)
  useEffect(() => {
    if (onDataUpdate && portfolio?.fetched_at) {
      onDataUpdate(portfolio.fetched_at)
    }
  }, [onDataUpdate, portfolio?.fetched_at])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-gray-500">Loading portfolio...</div>
      </div>
    )
  }

  if (error || !data?.success || !portfolio) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">
          {data?.error || 'Failed to load portfolio. Please check your Kite connection.'}
        </p>
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

  return (
    <div className="space-y-6">
      {/* Broker Filter - moved to top */}
      {availableBrokers.length > 0 && (
        <BrokerFilter
          availableBrokers={availableBrokers}
          selectedBrokers={selectedBrokers}
          onToggle={handleBrokerToggle}
        />
      )}

      <PortfolioSummary summary={filteredSummary} />

      <AllocationCharts
        allocation={filteredAllocation}
        totalValue={filteredSummary.total_value}
        isLoading={false}
      />

      <div className="grid grid-cols-1 gap-6">
        <HoldingsTable holdings={mergedHoldings} />
        {filteredMFHoldings.length > 0 && (
          <MFHoldingsTable holdings={filteredMFHoldings} />
        )}
      </div>
    </div>
  )
}
