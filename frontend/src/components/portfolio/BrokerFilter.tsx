interface BrokerFilterProps {
  availableBrokers: string[]
  selectedBrokers: string[]
  onToggle: (broker: string) => void
}

const brokerDisplayNames: Record<string, string> = {
  'kite': 'Zerodha Kite',
  'groww': 'Groww',
}

export default function BrokerFilter({
  availableBrokers,
  selectedBrokers,
  onToggle,
}: BrokerFilterProps) {
  return (
    <div className="flex items-center gap-4">
      <span className="text-sm font-medium text-gray-700">Filter by Broker:</span>
      {availableBrokers.map(broker => (
        <label
          key={broker}
          className="flex items-center gap-2 cursor-pointer text-sm text-gray-700 hover:text-gray-900"
        >
          <input
            type="checkbox"
            checked={selectedBrokers.includes(broker)}
            onChange={() => onToggle(broker)}
            className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2"
          />
          <span>{brokerDisplayNames[broker] || broker}</span>
        </label>
      ))}
    </div>
  )
}
