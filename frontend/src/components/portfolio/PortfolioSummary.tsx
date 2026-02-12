import type { PortfolioSummary as SummaryType } from '../../types/portfolio'

interface Props {
  summary: SummaryType
}

function formatCurrency(value: number): string {
  if (value >= 10000000) {
    return `₹${(value / 10000000).toFixed(2)} Cr`
  }
  if (value >= 100000) {
    return `₹${(value / 100000).toFixed(2)} L`
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
  breakdown?: { label: string; value: string }[]
  valueColor?: 'gain' | 'loss' | 'neutral'
}

function SummaryCard({ title, value, breakdown, valueColor = 'neutral' }: CardProps) {
  const colorClass = {
    gain: 'text-green-600',
    loss: 'text-red-600',
    neutral: 'text-gray-900',
  }[valueColor]

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <p className="text-sm text-gray-500">{title}</p>
      <p className={`text-2xl font-semibold ${colorClass}`}>{value}</p>
      {breakdown && breakdown.length > 0 && (
        <div className="mt-2 space-y-1">
          {breakdown.map((item, idx) => (
            <p key={idx} className="text-sm text-gray-600">
              {item.label}: {item.value}
            </p>
          ))}
        </div>
      )}
    </div>
  )
}

export default function PortfolioSummary({ summary }: Props) {
  const pnlColor = summary.total_pnl >= 0 ? 'gain' : 'loss'
  const dayColor = summary.day_pnl >= 0 ? 'gain' : 'loss'

  // Calculate percentage returns for stocks and MF
  const stocksPnlPercent = summary.stocks_invested > 0
    ? (summary.stocks_pnl / summary.stocks_invested * 100)
    : 0
  const mfPnlPercent = summary.mf_invested > 0
    ? (summary.mf_pnl / summary.mf_invested * 100)
    : 0

  // Calculate day change percentages
  const stocksDayChangePercent = summary.stocks_value > 0
    ? (summary.stocks_day_change / summary.stocks_value * 100)
    : 0

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <SummaryCard
        title="Invested"
        value={formatCurrency(summary.total_invested)}
        breakdown={[
          { label: 'Stocks', value: formatCurrency(summary.stocks_invested) },
          { label: 'Mutual Funds', value: formatCurrency(summary.mf_invested) },
        ]}
      />
      <SummaryCard
        title="Total Value"
        value={formatCurrency(summary.total_value)}
        breakdown={[
          { label: 'Stocks', value: formatCurrency(summary.stocks_value) },
          { label: 'Mutual Funds', value: formatCurrency(summary.mf_value) },
        ]}
      />
      <SummaryCard
        title="Total P&L"
        value={`${formatCurrency(summary.total_pnl)} (${formatPercent(summary.total_pnl_percent)})`}
        breakdown={[
          { label: 'Stocks', value: `${formatCurrency(summary.stocks_pnl)} (${formatPercent(stocksPnlPercent)})` },
          { label: 'Mutual Funds', value: `${formatCurrency(summary.mf_pnl)} (${formatPercent(mfPnlPercent)})` },
        ]}
        valueColor={pnlColor}
      />
      <SummaryCard
        title="Today's Change"
        value={`${formatCurrency(summary.day_pnl)} (${formatPercent(summary.day_pnl_percent)})`}
        breakdown={[
          { label: 'Stocks', value: `${formatCurrency(summary.stocks_day_change)} (${formatPercent(stocksDayChangePercent)})` },
          { label: 'Mutual Funds', value: 'N/A' },
        ]}
        valueColor={dayColor}
      />
    </div>
  )
}
