export interface Holding {
  symbol: string
  exchange: string
  isin: string | null
  quantity: number
  avg_price: number
  current_price: number | null  // From broker (Kite) or enrichment (Groww quotes)
  value: number  // quantity * current_price (or avg_price if current_price is null)
  invested: number  // quantity * avg_price
  pnl: number | null  // value - invested (null if current_price is not available)
  pnl_percent: number | null  // null if current_price is not available
  day_change: number | null  // From broker (Kite) or enrichment (Groww quotes)
  day_change_percent: number | null  // From broker (Kite) or enrichment (Groww quotes)
  market_cap_category: string | null  // From enrichment (Screener)
  broker: string  // Which broker this holding is from (kite, groww, etc.)
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
  day_change: number | null  // From enrichment (MFApi)
  day_change_percent: number | null  // From enrichment (MFApi)
  market_cap_category: string | null  // Parsed from scheme name
  broker: string
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
  stocks_invested: number
  mf_invested: number
  stocks_pnl: number
  mf_pnl: number
  stocks_day_change: number
  mf_day_change: number
  holdings_count: number
  mf_count: number
}

export interface AllocationBreakdown {
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
  data?: T
  cached_at?: string
  error?: string
  error_type?: 'token_expired' | string
}

// Enrichment response types
export interface QuotesEnrichment {
  [symbol: string]: {
    last_price: number
    day_change: number | null
    day_change_percent: number | null
  } | null
}

export interface MarketCapEnrichment {
  [symbol: string]: string | null  // market_cap_category or null
}

export interface MFDayChangeEnrichment {
  [scheme_code: string]: {
    day_change: number
    day_change_percent: number
  } | null
}
