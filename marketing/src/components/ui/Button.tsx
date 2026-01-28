interface ButtonProps {
  children: React.ReactNode
  variant?: 'primary' | 'secondary' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  onClick?: () => void
  className?: string
}

export const Button = ({
  children,
  variant = 'primary',
  size = 'md',
  onClick,
  className = ''
}: ButtonProps) => {
  const baseClasses = 'font-medium rounded-lg transition-all duration-200 cursor-pointer inline-block text-center'

  const variantClasses = {
    primary: 'bg-primary text-white hover:bg-blue-600 shadow-md hover:shadow-lg',
    secondary: 'bg-secondary text-white hover:bg-green-600 shadow-md hover:shadow-lg',
    outline: 'border-2 border-primary text-primary hover:bg-primary hover:text-white'
  }

  const sizeClasses = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg'
  }

  const classes = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${className}`

  return (
    <button onClick={onClick} className={classes}>
      {children}
    </button>
  )
}
