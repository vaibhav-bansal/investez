import { usePortfolio } from '../hooks/usePortfolio'
import PortfolioSummary from '../components/portfolio/PortfolioSummary'
import HoldingsTable from '../components/portfolio/HoldingsTable'
import MFHoldingsTable from '../components/portfolio/MFHoldingsTable'
import AllocationCharts from '../components/charts/AllocationCharts'

export default function Dashboard() {
  const { data, isLoading, error } = usePortfolio()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="text-gray-500">Loading portfolio...</div>
      </div>
    )
  }

  if (error || !data?.success) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-700">
          {data?.error || 'Failed to load portfolio. Please check your Kite connection.'}
        </p>
      </div>
    )
  }

  const portfolio = data.data

  return (
    <div className="space-y-6">
      <PortfolioSummary summary={portfolio.summary} />

      <AllocationCharts allocation={portfolio.allocation} totalValue={portfolio.summary.total_value} />

      <div className="grid grid-cols-1 gap-6">
        <HoldingsTable holdings={portfolio.holdings} />
        {portfolio.mf_holdings.length > 0 && (
          <MFHoldingsTable holdings={portfolio.mf_holdings} />
        )}
      </div>

      <p className="text-xs text-gray-400 text-right">
        Last updated: {new Date(portfolio.fetched_at).toLocaleString()}
      </p>
    </div>
  )
}
