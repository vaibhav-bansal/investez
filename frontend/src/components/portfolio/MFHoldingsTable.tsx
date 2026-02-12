import { useState } from 'react'
import type { MFHolding } from '../../types/portfolio'

interface Props {
  holdings: MFHolding[]
}

type SortKey = 'scheme_name' | 'value' | 'pnl' | 'pnl_percent' | 'day_change_percent'

function formatCurrency(value: number): string {
  return value.toLocaleString('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  })
}

export default function MFHoldingsTable({ holdings }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>('value')
  const [sortAsc, setSortAsc] = useState(false)

  const handleSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortAsc(!sortAsc)
    } else {
      setSortKey(key)
      setSortAsc(false)
    }
  }

  const sorted = [...holdings].sort((a, b) => {
    const aVal = a[sortKey]
    const bVal = b[sortKey]
    if (typeof aVal === 'string' && typeof bVal === 'string') {
      return sortAsc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal)
    }
    return sortAsc ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number)
  })

  const SortHeader = ({ label, keyName }: { label: string; keyName: SortKey }) => (
    <th
      className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase cursor-pointer hover:bg-gray-100"
      onClick={() => handleSort(keyName)}
    >
      {label}
      {sortKey === keyName && (sortAsc ? ' ↑' : ' ↓')}
    </th>
  )

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900">Mutual Fund Holdings</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <SortHeader label="Scheme Name" keyName="scheme_name" />
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Units
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Avg NAV
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Current NAV
              </th>
              <SortHeader label="Value" keyName="value" />
              <SortHeader label="P&L" keyName="pnl" />
              <SortHeader label="P&L %" keyName="pnl_percent" />
              <SortHeader label="Day %" keyName="day_change_percent" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {sorted.map((h) => (
              <tr key={h.scheme_code} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900 max-w-xs truncate">
                  {h.scheme_name}
                </td>
                <td className="px-4 py-3 text-gray-600">{h.units.toFixed(3)}</td>
                <td className="px-4 py-3 text-gray-600">{formatCurrency(h.avg_nav)}</td>
                <td className="px-4 py-3 text-gray-600">{formatCurrency(h.current_nav)}</td>
                <td className="px-4 py-3 text-gray-900">{formatCurrency(h.value)}</td>
                <td className={`px-4 py-3 ${h.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatCurrency(h.pnl)}
                </td>
                <td className={`px-4 py-3 ${h.pnl_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {h.pnl_percent >= 0 ? '+' : ''}{h.pnl_percent.toFixed(2)}%
                </td>
                <td className={`px-4 py-3 ${h.day_change_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {h.day_change_percent >= 0 ? '+' : ''}{h.day_change_percent.toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
