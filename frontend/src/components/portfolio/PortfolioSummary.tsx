import type { PortfolioSummary as SummaryType } from '../../types/portfolio'

interface Props {
  summary: SummaryType
}

function formatCurrency(value: number): string {
  if (value >= 10000000) {
    return `${(value / 10000000).toFixed(2)} Cr`
  }
  if (value >= 100000) {
    return `${(value / 100000).toFixed(2)} L`
  }
  return value.toLocaleString('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  })
}

function formatPercent(value: number): string {
  const sign = value >= 0 ? '+' : ''
  return `${sign}${value.toFixed(2)}%`
}

interface CardProps {
  title: string
  value: string
  subtitle?: string
  valueColor?: 'gain' | 'loss' | 'neutral'
}

function SummaryCard({ title, value, subtitle, valueColor = 'neutral' }: CardProps) {
  const colorClass = {
    gain: 'text-green-600',
    loss: 'text-red-600',
    neutral: 'text-gray-900',
  }[valueColor]

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <p className="text-sm text-gray-500">{title}</p>
      <p className={`text-2xl font-semibold ${colorClass}`}>{value}</p>
      {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
    </div>
  )
}

export default function PortfolioSummary({ summary }: Props) {
  const pnlColor = summary.total_pnl >= 0 ? 'gain' : 'loss'
  const dayColor = summary.day_pnl >= 0 ? 'gain' : 'loss'

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <SummaryCard
        title="Total Value"
        value={formatCurrency(summary.total_value)}
        subtitle={`${summary.holdings_count} stocks, ${summary.mf_count} MFs`}
      />
      <SummaryCard
        title="Total P&L"
        value={formatCurrency(summary.total_pnl)}
        subtitle={formatPercent(summary.total_pnl_percent)}
        valueColor={pnlColor}
      />
      <SummaryCard
        title="Today's Change"
        value={formatCurrency(summary.day_pnl)}
        subtitle={formatPercent(summary.day_pnl_percent)}
        valueColor={dayColor}
      />
      <SummaryCard
        title="Invested"
        value={formatCurrency(summary.total_invested)}
        subtitle={`Stocks: ${formatCurrency(summary.stocks_value)}`}
      />
    </div>
  )
}
