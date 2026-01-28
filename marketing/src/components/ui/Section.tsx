interface SectionProps {
  children: React.ReactNode
  className?: string
  background?: 'white' | 'gray'
  id?: string
}

export const Section = ({
  children,
  className = '',
  background = 'white',
  id
}: SectionProps) => {
  const bgClasses = {
    white: 'bg-white',
    gray: 'bg-gray-50'
  }

  return (
    <section
      id={id}
      className={`py-20 ${bgClasses[background]} ${className}`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {children}
      </div>
    </section>
  )
}
