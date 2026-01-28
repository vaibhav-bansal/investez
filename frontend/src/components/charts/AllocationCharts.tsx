import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import type { AllocationBreakdown } from '../../types/portfolio'

interface Props {
  allocation: AllocationBreakdown
  totalValue: number
}

const COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1',
]

interface ChartData {
  name: string
  value: number
  amount: number
}

function toChartData(data: Record<string, number>, totalValue: number): ChartData[] {
  return Object.entries(data)
    .map(([name, value]) => ({
      name,
      value,
      amount: (value / 100) * totalValue,
    }))
    .sort((a, b) => b.value - a.value)
}

function formatAmount(amount: number): string {
  if (amount >= 10000000) {
    return `₹${(amount / 10000000).toFixed(2)} Cr`
  }
  if (amount >= 100000) {
    return `₹${(amount / 100000).toFixed(2)} L`
  }
  return `₹${amount.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`
}

interface PieChartCardProps {
  title: string
  data: ChartData[]
}

function PieChartCard({ title, data }: PieChartCardProps) {
  if (data.length === 0) {
    return null
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <h4 className="font-medium text-gray-900 mb-2">{title}</h4>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={80}
              label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
              labelLine={false}
            >
              {data.map((_, index) => (
                <Cell key={index} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              formatter={(value: number, _name, props) => {
                const amount = (props as any)?.payload?.amount
                if (typeof amount === 'number') {
                  return `${formatAmount(amount)} (${value.toFixed(1)}%)`
                }
                return `${value.toFixed(1)}%`
              }}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default function AllocationCharts({ allocation, totalValue }: Props) {
  const marketCapData = toChartData(allocation.market_cap, totalValue)
  const assetData = toChartData(allocation.asset_type, totalValue)

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <PieChartCard title="By Market Cap" data={marketCapData} />
      <PieChartCard title="By Asset Type" data={assetData} />
    </div>
  )
}
