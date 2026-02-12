import { useState } from 'react'
import type { Holding } from '../../types/portfolio'

interface Props {
  holdings: Holding[]
}

type SortKey = 'symbol' | 'value' | 'pnl' | 'pnl_percent' | 'day_change_percent'

function formatCurrency(value: number): string {
  return value.toLocaleString('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  })
}

export default function HoldingsTable({ holdings }: Props) {
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
        <h3 className="font-semibold text-gray-900">Stock Holdings</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <SortHeader label="Symbol" keyName="symbol" />
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Broker
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Qty
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Avg Price
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                LTP
              </th>
              <SortHeader label="Value" keyName="value" />
              <SortHeader label="P&L" keyName="pnl" />
              <SortHeader label="P&L %" keyName="pnl_percent" />
              <SortHeader label="Day %" keyName="day_change_percent" />
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {sorted.map((h, index) => (
              <tr key={`${h.symbol}-${index}`} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium text-gray-900">{h.symbol}</td>
                <td className="px-4 py-3">
                  <span className={`px-2 py-1 text-xs font-medium rounded ${
                    h.broker === 'kite' ? 'bg-blue-100 text-blue-700' :
                    h.broker === 'groww' ? 'bg-green-100 text-green-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {h.broker === 'kite' ? 'Kite' : h.broker === 'groww' ? 'Groww' : h.broker === 'multiple' ? 'Multiple' : h.broker}
                  </span>
                </td>
                <td className="px-4 py-3 text-gray-600">{h.quantity}</td>
                <td className="px-4 py-3 text-gray-600">{formatCurrency(h.avg_price)}</td>
                <td className="px-4 py-3 text-gray-600">{formatCurrency(h.current_price)}</td>
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
