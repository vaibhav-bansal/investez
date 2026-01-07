export interface Holding {
  symbol: string
  exchange: string
  isin: string | null
  quantity: number
  avg_price: number
  current_price: number
  value: number
  invested: number
  pnl: number
  pnl_percent: number
  day_change: number
  day_change_percent: number
  weight: number
  sector: string | null
  market_cap_category: string | null
}

export interface MFHolding {
  scheme_code: string
  scheme_name: string
  fund_house: string | null
  folio: string | null
  units: number
  avg_nav: number
  current_nav: number
  value: number
  invested: number
  pnl: number
  pnl_percent: number
  weight: number
}

export interface PortfolioSummary {
  total_value: number
  total_invested: number
  total_pnl: number
  total_pnl_percent: number
  day_pnl: number
  day_pnl_percent: number
  stocks_value: number
  mf_value: number
  holdings_count: number
  mf_count: number
}

export interface AllocationBreakdown {
  sector: Record<string, number>
  market_cap: Record<string, number>
  asset_type: Record<string, number>
}

export interface Portfolio {
  summary: PortfolioSummary
  holdings: Holding[]
  mf_holdings: MFHolding[]
  allocation: AllocationBreakdown
  fetched_at: string
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  cached_at?: string
  error?: string
}
