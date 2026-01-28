import { UserPlus, Link2, Eye } from 'lucide-react'
import { Section } from '../ui/Section'

export const HowItWorks = () => {
  const steps = [
    {
      number: '01',
      icon: <UserPlus size={48} className="text-primary" />,
      title: 'Create Account',
      description: 'Sign up for free in seconds. No credit card required, no hidden fees.'
    },
    {
      number: '02',
      icon: <Link2 size={48} className="text-primary" />,
      title: 'Connect Brokers',
      description: 'Link your investment accounts from Zerodha, Groww, Upstox, or any broker. Add as many as you want - all in one place.'
    },
    {
      number: '03',
      icon: <Eye size={48} className="text-primary" />,
      title: 'See Everything',
      description: 'Get a unified view of all your investments. Track performance across brokers. Ask AI questions about your portfolio and get instant insights.'
    }
  ]

  return (
    <Section id="how-it-works" background="white">
      <div className="text-center mb-16">
        <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          How It Works
        </h2>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          Start consolidating your investments in three simple steps
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12 relative">
        {steps.map((step, index) => (
          <div key={index} className="relative">
            <div className="text-center">
              <div className="inline-flex items-center justify-center mb-6">
                {step.icon}
              </div>

              <div className="text-6xl font-bold text-gray-200 mb-4">
                {step.number}
              </div>

              <h3 className="text-2xl font-semibold text-gray-900 mb-3">
                {step.title}
              </h3>

              <p className="text-gray-600 leading-relaxed">
                {step.description}
              </p>
            </div>

            {index < steps.length - 1 && (
              <div className="hidden md:block absolute top-24 -right-6 w-12 h-0.5 bg-gray-300"></div>
            )}
          </div>
        ))}
      </div>
    </Section>
  )
}
