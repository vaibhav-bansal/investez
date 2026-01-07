import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import type { AllocationBreakdown } from '../../types/portfolio'

interface Props {
  allocation: AllocationBreakdown
}

const COLORS = [
  '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
  '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#6366f1',
]

interface ChartData {
  name: string
  value: number
}

function toChartData(data: Record<string, number>): ChartData[] {
  return Object.entries(data)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
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
              formatter={(value: number) => `${value.toFixed(2)}%`}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default function AllocationCharts({ allocation }: Props) {
  const sectorData = toChartData(allocation.sector)
  const marketCapData = toChartData(allocation.market_cap)
  const assetData = toChartData(allocation.asset_type)

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <PieChartCard title="By Sector" data={sectorData} />
      <PieChartCard title="By Market Cap" data={marketCapData} />
      <PieChartCard title="By Asset Type" data={assetData} />
    </div>
  )
}
