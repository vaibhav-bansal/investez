import { Holding, MFHolding, PortfolioSummary, AllocationBreakdown } from '../types/portfolio'

export function calculateFilteredSummary(
  stockHoldings: Holding[],
  mfHoldings: MFHolding[]
): PortfolioSummary {
  const stocks_value = stockHoldings.reduce((sum, h) => sum + h.value, 0)
  const stocks_invested = stockHoldings.reduce((sum, h) => sum + h.invested, 0)
  const stocks_pnl = stockHoldings.reduce((sum, h) => sum + (h.pnl || 0), 0)
  const stocks_day_change = stockHoldings.reduce(
    (sum, h) => sum + ((h.day_change || 0) * h.quantity),
    0
  )

  const mf_value = mfHoldings.reduce((sum, m) => sum + m.value, 0)
  const mf_invested = mfHoldings.reduce((sum, m) => sum + m.invested, 0)
  const mf_pnl = mfHoldings.reduce((sum, m) => sum + m.pnl, 0)
  const mf_day_change = mfHoldings.reduce(
    (sum, m) => sum + ((m.day_change || 0) * m.units),
    0
  )

  const total_value = stocks_value + mf_value
  const total_invested = stocks_invested + mf_invested
  const total_pnl = stocks_pnl + mf_pnl
  const total_pnl_percent = total_invested > 0
    ? (total_pnl / total_invested) * 100
    : 0
  const day_pnl = stocks_day_change + mf_day_change
  const day_pnl_percent = total_value > 0
    ? (day_pnl / total_value) * 100
    : 0

  return {
    total_value,
    total_invested,
    total_pnl,
    total_pnl_percent,
    day_pnl,
    day_pnl_percent,
    stocks_value,
    mf_value,
    stocks_invested,
    mf_invested,
    stocks_pnl,
    mf_pnl,
    stocks_day_change,
    mf_day_change,
    holdings_count: stockHoldings.length,
    mf_count: mfHoldings.length,
  }
}

export function calculateAllocation(
  stockHoldings: Holding[],
  mfHoldings: MFHolding[]
): AllocationBreakdown {
  const stocks_value = stockHoldings.reduce((sum, h) => sum + h.value, 0)
  const mf_value = mfHoldings.reduce((sum, m) => sum + m.value, 0)
  const total = stocks_value + mf_value

  const mcap_values: Record<string, number> = {}

  stockHoldings.forEach(h => {
    const mcap = h.market_cap_category || 'Unknown'
    mcap_values[mcap] = (mcap_values[mcap] || 0) + h.value
  })

  mfHoldings.forEach(m => {
    const mcap = m.market_cap_category || 'Unknown'
    mcap_values[mcap] = (mcap_values[mcap] || 0) + m.value
  })

  const mcap_filtered = Object.entries(mcap_values)
    .filter(([key]) => key !== 'Unknown')
  const total_filtered = mcap_filtered.reduce((sum, [, val]) => sum + val, 0)

  const market_cap: Record<string, number> = {}
  mcap_filtered.forEach(([key, val]) => {
    market_cap[key] = total_filtered > 0
      ? (val / total_filtered) * 100
      : 0
  })

  const asset_type: Record<string, number> = {}
  if (total > 0) {
    asset_type['Stocks'] = (stocks_value / total) * 100
    asset_type['Mutual Funds'] = (mf_value / total) * 100
  }

  return { market_cap, asset_type }
}
