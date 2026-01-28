interface CardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
}

export const Card = ({ children, className = '', hover = false }: CardProps) => {
  const hoverClasses = hover ? 'hover:shadow-xl hover:-translate-y-1 transition-all duration-300' : ''

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${hoverClasses} ${className}`}>
      {children}
    </div>
  )
}
